from enum import Enum


class ScanState(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class FailureCode(str, Enum):
    INVALID_URL = "invalid_url"

    BLOCKED_PRIVATE_DESTINATION = (
        "blocked_private_destination"
    )

    DNS_FAILURE = "dns_failure"

    CONNECTION_TIMEOUT = (
        "connection_timeout"
    )

    INACCESSIBLE_SITE = (
        "inaccessible_site"
    )

    TLS_FAILURE = "tls_failure"

    NON_HTML_CONTENT = (
        "non_html_content"
    )

    BROWSER_TIMEOUT = (
        "browser_timeout"
    )

    BEHAVIOURAL_UNAVAILABLE = (
        "behavioural_unavailable"
    )

    HEURISTIC_UNAVAILABLE = (
        "heuristic_unavailable"
    )

    NO_USABLE_EVIDENCE = (
        "no_usable_evidence"
    )

    INTERNAL_ERROR = (
        "internal_application_error"
    )