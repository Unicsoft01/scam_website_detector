from dataclasses import (
    asdict,
    dataclass,
    field,
)
import re
from typing import Optional
from urllib.parse import urlsplit

from playwright.sync_api import (
    Dialog,
    Download,
    Page,
    Request,
    Route,
    sync_playwright,
)

from app.core.url_security import (
    is_public_destination,
    validate_url,
)


DEFAULT_NAVIGATION_TIMEOUT_MS = 10_000
DEFAULT_ACTION_TIMEOUT_MS = 5_000
DEFAULT_OBSERVATION_TIME_MS = 2_000

MAX_MUTATION_COUNT = 10_000


ALLOWED_REQUEST_METHODS = {
    "GET",
    "HEAD",
    "OPTIONS",
}


INTERNAL_BROWSER_SCHEMES = {
    "about",
    "blob",
    "data",
}


# The script is an immediately invoked function expression (IIFE).
# This means it works correctly with BOTH:
#   context.add_init_script(...)
# and:
#   page.evaluate(...)
#
# It is also idempotent: running it a second time will not create
# a second MutationObserver or reset already collected metrics.
BEHAVIOURAL_INIT_SCRIPT = f"""
(() => {{
    if (window.__behaviouralMetrics) {{
        return;
    }}

    window.__behaviouralMetrics = {{
        domMutationCount: 0,
        formActionChangeCount: 0,
        dynamicFormCount: 0,
        titleChangeCount: 0
    }};

    let previousTitle = document.title || "";

    const incrementMutation = () => {{
        if (
            window.__behaviouralMetrics.domMutationCount
            < {MAX_MUTATION_COUNT}
        ) {{
            window.__behaviouralMetrics.domMutationCount++;
        }}
    }};

    const observer = new MutationObserver(
        (mutations) => {{
            for (const mutation of mutations) {{
                incrementMutation();

                if (
                    mutation.type === "attributes"
                    &&
                    mutation.target
                    &&
                    mutation.target.tagName === "FORM"
                    &&
                    mutation.attributeName === "action"
                ) {{
                    window.__behaviouralMetrics
                        .formActionChangeCount++;
                }}

                if (mutation.type === "childList") {{
                    for (const node of mutation.addedNodes) {{
                        if (
                            node.nodeType !==
                            Node.ELEMENT_NODE
                        ) {{
                            continue;
                        }}

                        if (node.tagName === "FORM") {{
                            window.__behaviouralMetrics
                                .dynamicFormCount++;
                        }}

                        if (node.querySelectorAll) {{
                            const nestedForms =
                                node.querySelectorAll("form");

                            window.__behaviouralMetrics
                                .dynamicFormCount
                                += nestedForms.length;
                        }}
                    }}
                }}
            }}

            const currentTitle =
                document.title || "";

            if (currentTitle !== previousTitle) {{
                window.__behaviouralMetrics
                    .titleChangeCount++;

                previousTitle =
                    currentTitle;
            }}
        }}
    );

    const startObserver = () => {{
        if (!document.documentElement) {{
            return;
        }}

        observer.observe(
            document.documentElement,
            {{
                subtree: true,
                childList: true,
                attributes: true,
                characterData: true,
                attributeFilter: [
                    "action",
                    "style",
                    "hidden",
                    "class"
                ]
            }}
        );
    }};

    if (document.documentElement) {{
        startObserver();
    }} else {{
        document.addEventListener(
            "DOMContentLoaded",
            startObserver,
            {{
                once: true
            }}
        );
    }}
}})();
"""


@dataclass
class BrowserObservation:
    submitted_url: Optional[str]

    success: bool = False

    initial_url: Optional[str] = None
    final_url: Optional[str] = None

    main_status_code: Optional[int] = None

    request_urls: list[str] = field(
        default_factory=list
    )

    navigation_urls: list[str] = field(
        default_factory=list
    )

    automatic_navigation_urls: list[str] = field(
        default_factory=list
    )

    redirect_chain: list[str] = field(
        default_factory=list
    )

    blocked_requests: list[dict] = field(
        default_factory=list
    )

    failed_requests: list[str] = field(
        default_factory=list
    )

    popup_count: int = 0
    dialog_count: int = 0
    download_count: int = 0

    page_error_count: int = 0

    page_errors: list[str] = field(
        default_factory=list
    )

    dom_mutation_count: int = 0
    form_action_change_count: int = 0
    dynamic_form_count: int = 0
    title_change_count: int = 0

    countdown_detected: bool = False

    error_type: Optional[str] = None
    error_message: Optional[str] = None


def _block_request(
    route: Route,
    state: BrowserObservation,
    reason: str,
) -> None:
    """
    Record and abort a browser request.
    """

    request = route.request

    state.blocked_requests.append(
        {
            "url": request.url,
            "method": request.method,
            "resource_type": request.resource_type,
            "reason": reason,
        }
    )

    route.abort()


def _handle_route(
    route: Route,
    state: BrowserObservation,
) -> None:
    """
    Security gate for every intercepted browser request.

    This operates before the browser is permitted to continue
    the request.
    """

    request = route.request
    request_url = request.url

    state.request_urls.append(
        request_url
    )

    try:
        parsed = urlsplit(
            request_url
        )

    except Exception:
        _block_request(
            route,
            state,
            "Request URL could not be parsed.",
        )
        return

    scheme = (
        parsed.scheme
        .strip()
        .lower()
    )

    # Non-network browser resources are allowed.
    if scheme in INTERNAL_BROWSER_SCHEMES:
        route.continue_()
        return

    # Reject file:, ftp:, javascript:, etc.
    if scheme not in {
        "http",
        "https",
    }:
        _block_request(
            route,
            state,
            (
                "Unsupported network "
                f"scheme: {scheme}"
            ),
        )
        return

    method = (
        request.method
        .strip()
        .upper()
    )

    # Avoid common state-changing requests during observation.
    if method not in ALLOWED_REQUEST_METHODS:
        _block_request(
            route,
            state,
            (
                "HTTP method blocked "
                f"during observation: {method}"
            ),
        )
        return

    validation = validate_url(
        request_url
    )

    if not validation.is_valid:
        _block_request(
            route,
            state,
            (
                validation.reason
                or "Invalid browser request URL."
            ),
        )
        return

    allowed, reason = (
        is_public_destination(
            validation.normalized_url
        )
    )

    if not allowed:
        _block_request(
            route,
            state,
            reason,
        )
        return

    route.continue_()


def _handle_dialog(
    dialog: Dialog,
    state: BrowserObservation,
) -> None:
    """
    Record and dismiss JavaScript alerts/prompts/confirms.
    """

    state.dialog_count += 1

    try:
        dialog.dismiss()

    except Exception:
        pass


def _handle_popup(
    popup: Page,
    state: BrowserObservation,
) -> None:
    """
    Record and immediately close popup windows.
    """

    state.popup_count += 1

    try:
        popup.close()

    except Exception:
        pass


def _handle_download(
    download: Download,
    state: BrowserObservation,
) -> None:
    """
    Record attempted downloads.

    accept_downloads=False prevents intentional persistence.
    """

    state.download_count += 1

    try:
        download.cancel()

    except Exception:
        pass


def _handle_page_error(
    error,
    state: BrowserObservation,
) -> None:
    """
    Record JavaScript/runtime page errors.
    """

    state.page_error_count += 1

    state.page_errors.append(
        str(error)
    )


def _handle_failed_request(
    request: Request,
    state: BrowserObservation,
) -> None:
    """
    Record network requests that failed.
    """

    state.failed_requests.append(
        request.url
    )


def _handle_navigation(
    frame,
    state: BrowserObservation,
) -> None:
    """
    Record main-frame navigation changes.
    """

    try:
        if frame == frame.page.main_frame:
            state.navigation_urls.append(
                frame.url
            )

    except Exception:
        pass


def _configure_page(
    page: Page,
    state: BrowserObservation,
) -> None:
    """
    Install runtime observers before page activity begins.
    """

    page.on(
        "dialog",
        lambda dialog:
            _handle_dialog(
                dialog,
                state,
            ),
    )

    page.on(
        "popup",
        lambda popup:
            _handle_popup(
                popup,
                state,
            ),
    )

    page.on(
        "download",
        lambda download:
            _handle_download(
                download,
                state,
            ),
    )

    page.on(
        "pageerror",
        lambda error:
            _handle_page_error(
                error,
                state,
            ),
    )

    page.on(
        "requestfailed",
        lambda request:
            _handle_failed_request(
                request,
                state,
            ),
    )

    page.on(
        "framenavigated",
        lambda frame:
            _handle_navigation(
                frame,
                state,
            ),
    )


def _create_context(
    browser
):
    """
    Create a fresh non-persistent browser context.
    """

    context = browser.new_context(
        accept_downloads=False,
        java_script_enabled=True,
        ignore_https_errors=False,
        service_workers="block",
        viewport={
            "width": 1280,
            "height": 720,
        },
    )

    context.clear_permissions()

    context.set_default_timeout(
        DEFAULT_ACTION_TIMEOUT_MS
    )

    context.set_default_navigation_timeout(
        DEFAULT_NAVIGATION_TIMEOUT_MS
    )

    return context


def _extract_redirect_chain(
    response,
) -> list[str]:
    """
    Reconstruct the HTTP redirect chain for the main document
    request returned by page.goto().

    Example:
        A -> B -> C
    returns:
        [A, B, C]
    """

    if response is None:
        return []

    try:
        request = response.request

        chain = [
            request.url
        ]

        previous = (
            request.redirected_from
        )

        while previous is not None:
            chain.append(
                previous.url
            )

            previous = (
                previous.redirected_from
            )

        chain.reverse()

        return chain

    except Exception:
        return []


def _extract_visible_integer_candidates(
    page: Page,
) -> set[int]:
    """
    Collect reasonable visible integer values from page text.

    Used only for conservative countdown detection.
    """

    try:
        text = page.locator(
            "body"
        ).inner_text(
            timeout=1000
        )

    except Exception:
        return set()

    values = set()

    # Correct regex: \d means a digit.
    # The previous double-escaped form would not detect digits correctly.
    for match in re.findall(
        r"(?<!\d)\d{1,4}(?!\d)",
        text,
    ):
        try:
            value = int(
                match
            )

        except ValueError:
            continue

        if 0 <= value <= 3600:
            values.add(
                value
            )

    return values


def _detect_countdown(
    page: Page,
) -> bool:
    """
    Conservatively detect repeated downward-moving visible
    numeric values.

    A countdown is reported only when at least two consecutive
    transitions show a value decreasing by exactly one during
    four bounded observations.
    """

    snapshots = []

    for _ in range(4):
        snapshots.append(
            _extract_visible_integer_candidates(
                page
            )
        )

        page.wait_for_timeout(
            400
        )

    decrease_evidence = 0

    for index in range(
        len(snapshots) - 1
    ):
        current = (
            snapshots[index]
        )

        following = (
            snapshots[index + 1]
        )

        found_decrease = False

        for value in current:
            if (
                value - 1
                in following
            ):
                found_decrease = True
                break

        if found_decrease:
            decrease_evidence += 1

    return (
        decrease_evidence >= 2
    )


def _read_runtime_metrics(
    page: Page,
    state: BrowserObservation,
) -> None:
    """
    Copy MutationObserver counters from the page into the
    BrowserObservation object.
    """

    try:
        runtime_metrics = page.evaluate(
            """
            () =>
                window.__behaviouralMetrics
                || null
            """
        )

    except Exception:
        runtime_metrics = None

    if not runtime_metrics:
        return

    state.dom_mutation_count = min(
        int(
            runtime_metrics.get(
                "domMutationCount",
                0,
            )
            or 0
        ),
        MAX_MUTATION_COUNT,
    )

    state.form_action_change_count = int(
        runtime_metrics.get(
            "formActionChangeCount",
            0,
        )
        or 0
    )

    state.dynamic_form_count = int(
        runtime_metrics.get(
            "dynamicFormCount",
            0,
        )
        or 0
    )

    state.title_change_count = int(
        runtime_metrics.get(
            "titleChangeCount",
            0,
        )
        or 0
    )


def observe_public_url(
    url: str,
    observation_time_ms: int = (
        DEFAULT_OBSERVATION_TIME_MS
    ),
) -> BrowserObservation:
    """
    Open a public URL inside a controlled Chromium context.

    This function gathers runtime observations only.
    It does NOT classify the website.
    """

    state = BrowserObservation(
        submitted_url=url
    )

    # ----------------------------------
    # INITIAL URL VALIDATION
    # ----------------------------------

    validation = validate_url(
        url
    )

    if not validation.is_valid:
        state.error_type = (
            "invalid_url"
        )

        state.error_message = (
            validation.reason
        )

        return state

    normalized_url = (
        validation.normalized_url
    )

    # ----------------------------------
    # INITIAL PUBLIC DESTINATION CHECK
    # ----------------------------------

    allowed, reason = (
        is_public_destination(
            normalized_url
        )
    )

    if not allowed:
        state.error_type = (
            "unsafe_destination"
        )

        state.error_message = reason

        return state

    # ----------------------------------
    # BROWSER EXECUTION
    # ----------------------------------

    with sync_playwright() as playwright:
        browser = None
        context = None

        try:
            browser = (
                playwright.chromium.launch(
                    headless=True
                )
            )

            context = (
                _create_context(
                    browser
                )
            )

            # Install the behavioural observer before document
            # scripts execute on navigated pages.
            context.add_init_script(
                BEHAVIOURAL_INIT_SCRIPT
            )

            # Route every browser request through the safety gate.
            context.route(
                "**/*",
                lambda route:
                    _handle_route(
                        route,
                        state,
                    ),
            )

            page = (
                context.new_page()
            )

            _configure_page(
                page,
                state,
            )

            response = page.goto(
                normalized_url,
                wait_until="domcontentloaded",
            )

            # Initial state after page.goto() has completed.
            state.initial_url = (
                page.url
            )

            state.redirect_chain = (
                _extract_redirect_chain(
                    response
                )
            )

            # Everything already recorded up to this point belongs
            # to initial loading. Later main-frame navigation events
            # are treated as automatic runtime navigation because
            # the scanner performs no user interaction.
            navigation_baseline = len(
                state.navigation_urls
            )

            if response is not None:
                state.main_status_code = (
                    response.status
                )

            # Bounded general runtime observation period.
            page.wait_for_timeout(
                observation_time_ms
            )

            state.automatic_navigation_urls = (
                state.navigation_urls[
                    navigation_baseline:
                ]
            )

            # Read DOM behaviour accumulated during page execution.
            _read_runtime_metrics(
                page,
                state,
            )

            # Conservative countdown sampling. This deliberately
            # adds about 1.6 seconds to runtime.
            try:
                state.countdown_detected = (
                    _detect_countdown(
                        page
                    )
                )

            except Exception:
                state.countdown_detected = False


            state.final_url = (
                page.url
            )

            state.success = True

            return state

        except Exception as error:
            state.success = False

            state.error_type = (
                error.__class__.__name__
            )

            state.error_message = (
                str(error)
            )

            return state

        finally:
            if context is not None:
                try:
                    context.close()

                except Exception:
                    pass

            if browser is not None:
                try:
                    browser.close()

                except Exception:
                    pass


def observe_synthetic_html(
    html: str,
    javascript: Optional[str] = None,
    observation_time_ms: int = 500,
) -> BrowserObservation:
    """
    Run synthetic HTML inside Chromium without navigating to
    an external website.

    Intended only for controlled development tests.
    """

    state = BrowserObservation(
        submitted_url=None
    )

    with sync_playwright() as playwright:
        browser = None
        context = None

        try:
            browser = (
                playwright.chromium.launch(
                    headless=True
                )
            )

            context = (
                _create_context(
                    browser
                )
            )

            context.add_init_script(
                BEHAVIOURAL_INIT_SCRIPT
            )

            context.route(
                "**/*",
                lambda route:
                    _handle_route(
                        route,
                        state,
                    ),
            )

            page = (
                context.new_page()
            )

            _configure_page(
                page,
                state,
            )

            page.set_content(
                html
            )

            # set_content() is not an ordinary browser navigation,
            # so execute the observer directly as well. The script
            # is idempotent and will not install twice.
            page.evaluate(
                BEHAVIOURAL_INIT_SCRIPT
            )

            if javascript:
                page.evaluate(
                    javascript
                )

            page.wait_for_timeout(
                observation_time_ms
            )

            _read_runtime_metrics(
                page,
                state,
            )

            try:
                state.countdown_detected = (
                    _detect_countdown(
                        page
                    )
                )

            except Exception:
                state.countdown_detected = False

            state.final_url = (
                page.url
            )

            state.success = True

            return state

        except Exception as error:
            state.success = False

            state.error_type = (
                error.__class__.__name__
            )

            state.error_message = (
                str(error)
            )

            return state

        finally:
            if context is not None:
                try:
                    context.close()

                except Exception:
                    pass

            if browser is not None:
                try:
                    browser.close()

                except Exception:
                    pass


def browser_observation_to_dict(
    result: BrowserObservation
) -> dict:
    return asdict(
        result
    )
