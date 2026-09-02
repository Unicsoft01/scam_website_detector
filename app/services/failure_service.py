from dataclasses import dataclass
from typing import Optional

from app.core.failures import (
    FailureCode,
    ScanState,
)


@dataclass(frozen=True)
class FailureDetails:
    state: ScanState
    code: FailureCode
    message: str
    behavioural_available: Optional[bool] = None


class FailureService:

    @staticmethod
    def invalid_url(
        message: str = (
            "The submitted URL is invalid."
        ),
    ) -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.INVALID_URL,
            message=message,
        )

    @staticmethod
    def blocked_private_destination(
        message: str = (
            "Analysis was blocked because the "
            "destination is private, loopback, "
            "link-local or otherwise restricted."
        ),
    ) -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=(
                FailureCode
                .BLOCKED_PRIVATE_DESTINATION
            ),
            message=message,
        )

    @staticmethod
    def dns_failure() -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.DNS_FAILURE,
            message=(
                "The website hostname could not "
                "be resolved."
            ),
        )

    @staticmethod
    def connection_timeout() -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.CONNECTION_TIMEOUT,
            message=(
                "The website did not respond "
                "within the permitted time."
            ),
        )

    @staticmethod
    def inaccessible_site() -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.INACCESSIBLE_SITE,
            message=(
                "The website could not be "
                "accessed for analysis."
            ),
        )

    @staticmethod
    def tls_failure() -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.TLS_FAILURE,
            message=(
                "A TLS-related failure prevented "
                "the required website analysis."
            ),
        )

    @staticmethod
    def non_html_content() -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.NON_HTML_CONTENT,
            message=(
                "The destination did not return "
                "HTML content suitable for "
                "website analysis."
            ),
        )

    @staticmethod
    def browser_timeout() -> FailureDetails:

        return FailureDetails(
            state=ScanState.PARTIAL,
            code=FailureCode.BROWSER_TIMEOUT,
            message=(
                "Behavioural analysis exceeded "
                "the permitted browser execution "
                "time."
            ),
            behavioural_available=False,
        )

    @staticmethod
    def behavioural_unavailable() -> FailureDetails:

        return FailureDetails(
            state=ScanState.PARTIAL,
            code=(
                FailureCode
                .BEHAVIOURAL_UNAVAILABLE
            ),
            message=(
                "Behavioural evidence was "
                "unavailable. Any classification "
                "shown is heuristic-only."
            ),
            behavioural_available=False,
        )

    @staticmethod
    def internal_error() -> FailureDetails:

        return FailureDetails(
            state=ScanState.FAILED,
            code=FailureCode.INTERNAL_ERROR,
            message=(
                "An internal application error "
                "prevented the scan from being "
                "completed."
            ),
        )