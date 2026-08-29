from dataclasses import (
    asdict,
    dataclass,
)
from datetime import (
    datetime,
    timezone,
)
import ipaddress
import socket
from typing import Optional
from urllib.parse import urlsplit

from app.collectors.http_collector import (
    collect_static_page,
)

from app.core.url_security import (
    is_public_destination,
    validate_url,
)


@dataclass
class LiveAvailabilityResult:
    submitted_url: str

    normalized_url: Optional[str]

    live_status: str

    behavioural_eligible: int
    hybrid_eligible: int

    status_code: Optional[int]
    final_url: Optional[str]

    content_type: Optional[str]

    downloaded_bytes: int
    redirect_count: int

    html_available: int

    error_type: Optional[str]
    error_message: Optional[str]

    audit_timestamp: str


def _utc_now() -> str:
    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )


def _hostname_dns_status(
    normalized_url: str,
) -> tuple[str, Optional[str]]:
    """
    Perform a lightweight DNS/public-IP preflight.

    Returns:
        ("ok", None)
        ("dns_failure", reason)
        ("blocked", reason)

    This does not replace the Phase 5 safety validation.
    It helps distinguish DNS failure from policy blocking.
    """

    try:
        hostname = (
            urlsplit(
                normalized_url
            ).hostname
        )

    except Exception as error:
        return (
            "blocked",
            f"Unable to parse hostname: {error}",
        )

    if not hostname:
        return (
            "blocked",
            "URL contains no hostname.",
        )

    # ---------------------------------
    # IP literal
    # ---------------------------------

    try:
        ip = ipaddress.ip_address(
            hostname
        )

        if not ip.is_global:
            return (
                "blocked",
                (
                    "Destination IP is not "
                    "publicly routable."
                ),
            )

        return (
            "ok",
            None,
        )

    except ValueError:
        pass

    # ---------------------------------
    # DNS hostname
    # ---------------------------------

    try:
        records = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )

    except socket.gaierror as error:
        return (
            "dns_failure",
            str(error),
        )

    except Exception as error:
        return (
            "dns_failure",
            str(error),
        )

    addresses = set()

    for record in records:
        try:
            addresses.add(
                record[4][0]
            )

        except Exception:
            continue

    if not addresses:
        return (
            "dns_failure",
            "No A/AAAA destination addresses resolved.",
        )

    # Conservative policy:
    # if any answer is non-global, do not contact the host.
    for address in addresses:
        try:
            ip = ipaddress.ip_address(
                address
            )

        except ValueError:
            return (
                "blocked",
                (
                    "DNS produced an invalid "
                    f"IP address: {address}"
                ),
            )

        if not ip.is_global:
            return (
                "blocked",
                (
                    "DNS resolution included a "
                    "non-public destination: "
                    f"{address}"
                ),
            )

    return (
        "ok",
        None,
    )


def _map_error_status(
    error_type: Optional[str],
    error_message: Optional[str],
) -> str:
    """
    Map Phase 9 collector outcomes to the frozen
    Phase 13 live_status taxonomy.
    """

    error_type_value = (
        error_type
        or ""
    ).lower()

    message = (
        error_message
        or ""
    ).lower()

    if (
        "timeout" in error_type_value
        or "timed out" in message
        or "timeout" in message
    ):
        return "timeout"

    if (
        "tls" in error_type_value
        or "ssl" in error_type_value
        or "certificate" in message
        or "ssl" in message
        or "tls" in message
    ):
        return "tls_failure"

    if (
        "redirect" in error_type_value
        or "redirect" in message
    ):
        return "redirect_failure"

    if (
        "unsafe" in error_type_value
        or "blocked" in message
        or "private" in message
        or "loopback" in message
        or "link-local" in message
        or "reserved" in message
    ):
        return "blocked"

    if (
        "dns" in error_type_value
        or "name resolution" in message
        or "name or service not known" in message
        or "getaddrinfo" in message
    ):
        return "dns_failure"

    return "inaccessible"


def audit_live_url(
    url: str,
) -> LiveAvailabilityResult:
    """
    Audit one URL for current live availability.

    Ground-truth scam/legitimate labels are NOT changed.
    """

    timestamp = (
        _utc_now()
    )

    # ---------------------------------
    # URL syntax validation
    # ---------------------------------

    validation = validate_url(
        url
    )

    if not validation.is_valid:
        return LiveAvailabilityResult(
            submitted_url=url,

            normalized_url=None,

            live_status="blocked",

            behavioural_eligible=0,
            hybrid_eligible=0,

            status_code=None,
            final_url=None,
            content_type=None,

            downloaded_bytes=0,
            redirect_count=0,

            html_available=0,

            error_type="invalid_url",

            error_message=(
                validation.reason
            ),

            audit_timestamp=timestamp,
        )

    normalized_url = (
        validation.normalized_url
    )

    # ---------------------------------
    # DNS / IP audit
    # ---------------------------------

    preflight_status, preflight_reason = (
        _hostname_dns_status(
            normalized_url
        )
    )

    if preflight_status != "ok":
        return LiveAvailabilityResult(
            submitted_url=url,

            normalized_url=(
                normalized_url
            ),

            live_status=(
                preflight_status
            ),

            behavioural_eligible=0,
            hybrid_eligible=0,

            status_code=None,
            final_url=None,
            content_type=None,

            downloaded_bytes=0,
            redirect_count=0,

            html_available=0,

            error_type=(
                preflight_status
            ),

            error_message=(
                preflight_reason
            ),

            audit_timestamp=timestamp,
        )

    # ---------------------------------
    # Phase 5 public-destination policy
    # ---------------------------------

    allowed, reason = (
        is_public_destination(
            normalized_url
        )
    )

    if not allowed:
        return LiveAvailabilityResult(
            submitted_url=url,

            normalized_url=(
                normalized_url
            ),

            live_status="blocked",

            behavioural_eligible=0,
            hybrid_eligible=0,

            status_code=None,
            final_url=None,
            content_type=None,

            downloaded_bytes=0,
            redirect_count=0,

            html_available=0,

            error_type=(
                "unsafe_destination"
            ),

            error_message=reason,

            audit_timestamp=timestamp,
        )

    # ---------------------------------
    # Controlled static collection
    # ---------------------------------

    result = collect_static_page(
        normalized_url
    )

    # ---------------------------------
    # Oversized response
    # ---------------------------------

    if result.response_too_large:
        live_status = (
            "oversized_response"
        )

    # ---------------------------------
    # Non-HTML response
    # ---------------------------------

    elif (
        result.request_success
        and not result.content_type_allowed
    ):
        live_status = (
            "non_html"
        )

    # ---------------------------------
    # Collector/network error
    # ---------------------------------

    elif not result.request_success:
        live_status = (
            _map_error_status(
                result.error_type,
                result.error_message,
            )
        )

    # ---------------------------------
    # HTTP response classification
    # ---------------------------------

    elif (
        result.status_code is not None
        and 200 <= result.status_code < 400
        and result.html
    ):
        live_status = (
            "accessible"
        )

    else:
        live_status = (
            "inaccessible"
        )

    eligible = int(
        live_status == "accessible"
    )

    return LiveAvailabilityResult(
        submitted_url=url,

        normalized_url=(
            normalized_url
        ),

        live_status=live_status,

        behavioural_eligible=(
            eligible
        ),

        hybrid_eligible=(
            eligible
        ),

        status_code=(
            result.status_code
        ),

        final_url=(
            result.final_url
        ),

        content_type=(
            result.content_type
        ),

        downloaded_bytes=(
            result.downloaded_bytes
        ),

        redirect_count=(
            result.redirect_count
        ),

        html_available=int(
            bool(
                result.html
            )
        ),

        error_type=(
            result.error_type
        ),

        error_message=(
            result.error_message
        ),

        audit_timestamp=timestamp,
    )


def live_result_to_dict(
    result: LiveAvailabilityResult,
) -> dict:
    return asdict(
        result
    )