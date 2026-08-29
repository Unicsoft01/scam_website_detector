from urllib.parse import urlsplit

from app.collectors.browser_environment import (
    BrowserObservation,
)

from app.core.url_security import (
    get_registrable_domain,
)


STATE_CHANGING_METHODS = {
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


def _registrable_domain(
    url: str,
) -> str | None:
    try:
        return (
            get_registrable_domain(
                url
            )
        )

    except Exception:
        return None


def _http_urls(
    urls: list[str],
) -> list[str]:
    """
    Retain HTTP/HTTPS URLs only.
    """

    result = []

    for url in urls:

        try:
            scheme = (
                urlsplit(
                    url
                )
                .scheme
                .lower()
            )

        except Exception:
            continue

        if scheme in {
            "http",
            "https",
        }:
            result.append(
                url
            )

    return result


def _count_cross_domain_redirects(
    redirect_chain: list[str],
) -> int:
    """
    Count consecutive redirect hops where the
    registrable domain changes.
    """

    if len(
        redirect_chain
    ) < 2:
        return 0

    count = 0

    for index in range(
        len(
            redirect_chain
        ) - 1
    ):

        first = (
            _registrable_domain(
                redirect_chain[index]
            )
        )

        second = (
            _registrable_domain(
                redirect_chain[
                    index + 1
                ]
            )
        )

        if (
            first
            and second
            and first != second
        ):
            count += 1

    return count


def extract_behavioural_features(
    observation: BrowserObservation,
) -> dict:
    """
    Convert raw Playwright observations into X_B.

    No classification is performed.
    """

    redirect_chain = (
        observation.redirect_chain
        or []
    )

    redirect_count = max(
        0,
        len(
            redirect_chain
        ) - 1,
    )

    cross_domain_redirect_count = (
        _count_cross_domain_redirects(
            redirect_chain
        )
    )

    http_requests = (
        _http_urls(
            observation.request_urls
        )
    )

    total_request_count = len(
        http_requests
    )

    base_url = (
        observation.initial_url
        or observation.submitted_url
        or ""
    )

    base_domain = (
        _registrable_domain(
            base_url
        )
    )

    external_request_count = 0

    for request_url in (
        http_requests
    ):
        request_domain = (
            _registrable_domain(
                request_url
            )
        )

        if (
            base_domain
            and request_domain
            and request_domain
            != base_domain
        ):
            external_request_count += 1

    external_request_ratio = (
        external_request_count
        / total_request_count
        if total_request_count
        else 0.0
    )

    state_changing_attempts = 0

    for blocked in (
        observation.blocked_requests
    ):

        method = str(
            blocked.get(
                "method",
                ""
            )
        ).upper()

        if method in (
            STATE_CHANGING_METHODS
        ):
            state_changing_attempts += 1

    automatic_navigation_count = len(
        observation.automatic_navigation_urls
    )

    return {
        "redirect_count":
            redirect_count,

        "cross_domain_redirect_count":
            cross_domain_redirect_count,

        "popup_count":
            observation.popup_count,

        "dialog_count":
            observation.dialog_count,

        "automatic_navigation_count":
            automatic_navigation_count,

        "has_automatic_navigation": int(
            automatic_navigation_count
            > 0
        ),

        "total_request_count":
            total_request_count,

        "external_request_count":
            external_request_count,

        "external_request_ratio": round(
            external_request_ratio,
            6,
        ),

        "blocked_request_count":
            len(
                observation.blocked_requests
            ),

        "state_changing_request_attempt_count":
            state_changing_attempts,

        "download_attempt_count":
            observation.download_count,

        "dom_mutation_count":
            observation.dom_mutation_count,

        "form_action_change_count":
            observation.form_action_change_count,

        "dynamic_form_count":
            observation.dynamic_form_count,

        "title_change_count":
            observation.title_change_count,

        "has_title_change": int(
            observation.title_change_count
            > 0
        ),

        "countdown_detected": int(
            observation.countdown_detected
        ),

        "page_error_count":
            observation.page_error_count,

        "failed_request_count":
            len(
                observation.failed_requests
            ),
    }