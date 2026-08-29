from dataclasses import (
    asdict,
    dataclass,
    field,
)
from typing import Optional
from urllib.parse import urlsplit

from playwright.sync_api import (
    Dialog,
    Download,
    Page,
    Playwright,
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


@dataclass
class BrowserObservation:
    submitted_url: Optional[str]

    success: bool = False
    final_url: Optional[str] = None
    main_status_code: Optional[int] = None

    request_urls: list[str] = field(
        default_factory=list
    )

    navigation_urls: list[str] = field(
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
            "resource_type":
                request.resource_type,
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

    Important:
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

    # Browser-internal/non-network resources may be used
    # by a page without contacting another network host.
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

    # During observation we avoid allowing common
    # state-changing HTTP requests.
    if method not in (
        ALLOWED_REQUEST_METHODS
    ):
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

    Browser context is configured with accept_downloads=False,
    so files should not be intentionally persisted.
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

            # Route every browser request through
            # our request safety function.
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
                wait_until=(
                    "domcontentloaded"
                ),
            )

            if response is not None:
                state.main_status_code = (
                    response.status
                )

            # Give runtime JavaScript a small,
            # bounded observation window.
            page.wait_for_timeout(
                observation_time_ms
            )

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

            if javascript:
                page.evaluate(
                    javascript
                )

            page.wait_for_timeout(
                observation_time_ms
            )

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