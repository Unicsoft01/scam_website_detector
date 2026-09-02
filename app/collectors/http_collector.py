from dataclasses import asdict, dataclass
from typing import Optional
from urllib.parse import urljoin

import httpx

from app.core.url_security import (
    is_public_destination,
    validate_url,
)


DEFAULT_TIMEOUT_SECONDS = 10.0

MAX_RESPONSE_BYTES = (
    2 * 1024 * 1024
)

MAX_REDIRECTS = 5


ALLOWED_HTML_CONTENT_TYPES = {
    "text/html",
    "application/xhtml+xml",
}


USER_AGENT = (
    "ScamWebsiteDetectionResearch/1.0 "
    "(Academic Security Research)"
)


@dataclass
class HTTPCollectionResult:
    requested_url: str
    final_url: Optional[str]

    request_success: bool

    status_code: Optional[int]

    content_type: Optional[str]
    content_length_header: Optional[int]
    downloaded_bytes: int

    html: Optional[str]

    redirect_count: int
    redirect_chain: list[str]

    response_too_large: bool
    content_type_allowed: bool

    error_type: Optional[str]
    error_message: Optional[str]


def _get_media_type(
    content_type_header: Optional[str]
) -> Optional[str]:
    """
    Extract the media type from a Content-Type header.

    Example:
        text/html; charset=utf-8
    becomes:
        text/html
    """

    if not content_type_header:
        return None

    return (
        content_type_header
        .split(";")[0]
        .strip()
        .lower()
    )


def _get_content_length(
    value: Optional[str]
) -> Optional[int]:
    """
    Safely convert Content-Length to an integer.
    """

    if not value:
        return None

    try:
        length = int(value)

        if length < 0:
            return None

        return length

    except ValueError:
        return None


def _classify_http_error(
    error: Exception
) -> str:
    """
    Convert network exceptions into broad diagnostic categories.
    """

    message = str(
        error
    ).lower()

    if isinstance(
        error,
        httpx.TimeoutException
    ):
        return "timeout"

    if (
        "certificate verify failed"
        in message
        or "ssl"
        in message
        or "tls"
        in message
    ):
        return "tls_error"

    if (
        "name or service not known"
        in message
        or "nodename nor servname"
        in message
        or "getaddrinfo failed"
        in message
        or "temporary failure in name resolution"
        in message
    ):
        return "dns_error"

    if isinstance(
        error,
        httpx.ConnectError
    ):
        return "connection_error"

    if isinstance(
        error,
        httpx.NetworkError
    ):
        return "network_error"

    if isinstance(
        error,
        httpx.HTTPError
    ):
        return "http_error"

    return "unexpected_error"


def _empty_result(
    requested_url: str,
    final_url: Optional[str],
    redirect_chain: list[str],
    error_type: str,
    error_message: str,
    status_code: Optional[int] = None,
) -> HTTPCollectionResult:
    """
    Create a consistent failure result.
    """

    return HTTPCollectionResult(
        requested_url=requested_url,
        final_url=final_url,

        request_success=False,

        status_code=status_code,

        content_type=None,
        content_length_header=None,
        downloaded_bytes=0,

        html=None,

        redirect_count=max(
            0,
            len(
                redirect_chain
            ) - 1
        ),

        redirect_chain=redirect_chain,

        response_too_large=False,
        content_type_allowed=False,

        error_type=error_type,
        error_message=error_message,
    )


def collect_static_page(
    url: str,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_response_bytes: int = MAX_RESPONSE_BYTES,
    max_redirects: int = MAX_REDIRECTS,
    client: Optional[httpx.Client] = None,
) -> HTTPCollectionResult:
    """
    Safely retrieve HTML from a public HTTP/HTTPS URL.

    The function gathers evidence only.
    It does not classify a website.
    """

    submitted_url = url

    validation = validate_url(
        submitted_url
    )

    if not validation.is_valid:
        return _empty_result(
            requested_url=submitted_url,
            final_url=None,
            redirect_chain=[],
            error_type="invalid_url",
            error_message=(
                validation.reason
                or "URL validation failed."
            ),
        )

    current_url = (
        validation.normalized_url
    )

    redirect_chain = [
        current_url
    ]

    owns_client = (
        client is None
    )

    if client is None:
        client = httpx.Client(
            timeout=httpx.Timeout(
                connect=min(
                    timeout_seconds,
                    5.0,
                ),
                read=timeout_seconds,
                write=5.0,
                pool=5.0,
            ),
            follow_redirects=False,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml"
                ),
            },
        )

    try:
        for redirect_number in range(
            max_redirects + 1
        ):
            allowed, reason = (
                is_public_destination(
                    current_url
                )
            )

            if not allowed:
                return _empty_result(
                    requested_url=(
                        submitted_url
                    ),
                    final_url=current_url,
                    redirect_chain=(
                        redirect_chain
                    ),
                    error_type=(
                        "unsafe_destination"
                    ),
                    error_message=reason,
                )

            try:
                with client.stream(
                    "GET",
                    current_url,
                ) as response:

                    status_code = (
                        response.status_code
                    )

                    # -------------------------
                    # HANDLE REDIRECTS MANUALLY
                    # -------------------------

                    if status_code in {
                        301,
                        302,
                        303,
                        307,
                        308,
                    }:
                        location = (
                            response.headers.get(
                                "Location"
                            )
                        )

                        if not location:
                            return _empty_result(
                                requested_url=(
                                    submitted_url
                                ),
                                final_url=current_url,
                                redirect_chain=(
                                    redirect_chain
                                ),
                                error_type=(
                                    "redirect_error"
                                ),
                                error_message=(
                                    "Redirect response "
                                    "did not contain a "
                                    "Location header."
                                ),
                                status_code=(
                                    status_code
                                ),
                            )

                        if (
                            redirect_number
                            >= max_redirects
                        ):
                            return _empty_result(
                                requested_url=(
                                    submitted_url
                                ),
                                final_url=current_url,
                                redirect_chain=(
                                    redirect_chain
                                ),
                                error_type=(
                                    "too_many_redirects"
                                ),
                                error_message=(
                                    "Maximum redirect "
                                    "limit exceeded."
                                ),
                                status_code=(
                                    status_code
                                ),
                            )

                        next_url = urljoin(
                            current_url,
                            location,
                        )

                        next_validation = (
                            validate_url(
                                next_url
                            )
                        )

                        if not (
                            next_validation.is_valid
                        ):
                            return _empty_result(
                                requested_url=(
                                    submitted_url
                                ),
                                final_url=current_url,
                                redirect_chain=(
                                    redirect_chain
                                ),
                                error_type=(
                                    "unsafe_redirect"
                                ),
                                error_message=(
                                    next_validation.reason
                                    or
                                    "Redirect target "
                                    "is invalid."
                                ),
                                status_code=(
                                    status_code
                                ),
                            )

                        next_url = (
                            next_validation
                            .normalized_url
                        )

                        redirect_allowed, (
                            redirect_reason
                        ) = (
                            is_public_destination(
                                next_url
                            )
                        )

                        if not redirect_allowed:
                            return _empty_result(
                                requested_url=(
                                    submitted_url
                                ),
                                final_url=current_url,
                                redirect_chain=(
                                    redirect_chain
                                ),
                                error_type=(
                                    "unsafe_redirect"
                                ),
                                error_message=(
                                    redirect_reason
                                ),
                                status_code=(
                                    status_code
                                ),
                            )

                        current_url = (
                            next_url
                        )

                        redirect_chain.append(
                            current_url
                        )

                        continue

                    # -------------------------
                    # CHECK CONTENT TYPE
                    # -------------------------

                    content_type_header = (
                        response.headers.get(
                            "Content-Type"
                        )
                    )

                    media_type = (
                        _get_media_type(
                            content_type_header
                        )
                    )

                    content_type_allowed = (
                        media_type
                        in ALLOWED_HTML_CONTENT_TYPES
                    )

                    if not content_type_allowed:
                        return HTTPCollectionResult(
                            requested_url=(
                                submitted_url
                            ),
                            final_url=current_url,

                            request_success=True,

                            status_code=(
                                status_code
                            ),

                            content_type=(
                                media_type
                            ),

                            content_length_header=(
                                _get_content_length(
                                    response.headers.get(
                                        "Content-Length"
                                    )
                                )
                            ),

                            downloaded_bytes=0,

                            html=None,

                            redirect_count=max(
                                0,
                                len(
                                    redirect_chain
                                ) - 1
                            ),

                            redirect_chain=(
                                redirect_chain
                            ),

                            response_too_large=False,

                            content_type_allowed=False,

                            error_type=(
                                "unsupported_content_type"
                            ),

                            error_message=(
                                "Response is not an "
                                "allowed HTML content type."
                            ),
                        )

                    # -------------------------
                    # CHECK DECLARED SIZE
                    # -------------------------

                    content_length = (
                        _get_content_length(
                            response.headers.get(
                                "Content-Length"
                            )
                        )
                    )

                    if (
                        content_length
                        is not None
                        and content_length
                        > max_response_bytes
                    ):
                        return HTTPCollectionResult(
                            requested_url=(
                                submitted_url
                            ),
                            final_url=current_url,

                            request_success=True,

                            status_code=(
                                status_code
                            ),

                            content_type=(
                                media_type
                            ),

                            content_length_header=(
                                content_length
                            ),

                            downloaded_bytes=0,

                            html=None,

                            redirect_count=max(
                                0,
                                len(
                                    redirect_chain
                                ) - 1
                            ),

                            redirect_chain=(
                                redirect_chain
                            ),

                            response_too_large=True,

                            content_type_allowed=True,

                            error_type=(
                                "response_too_large"
                            ),

                            error_message=(
                                "Declared response size "
                                "exceeds the permitted limit."
                            ),
                        )

                    # -------------------------
                    # STREAM BODY WITH HARD LIMIT
                    # -------------------------

                    body = bytearray()

                    for chunk in (
                        response.iter_bytes()
                    ):
                        if not chunk:
                            continue

                        if (
                            len(body)
                            + len(chunk)
                            > max_response_bytes
                        ):
                            return HTTPCollectionResult(
                                requested_url=(
                                    submitted_url
                                ),
                                final_url=current_url,

                                request_success=True,

                                status_code=(
                                    status_code
                                ),

                                content_type=(
                                    media_type
                                ),

                                content_length_header=(
                                    content_length
                                ),

                                downloaded_bytes=(
                                    len(body)
                                ),

                                html=None,

                                redirect_count=max(
                                    0,
                                    len(
                                        redirect_chain
                                    ) - 1
                                ),

                                redirect_chain=(
                                    redirect_chain
                                ),

                                response_too_large=True,

                                content_type_allowed=True,

                                error_type=(
                                    "response_too_large"
                                ),

                                error_message=(
                                    "Downloaded response "
                                    "exceeded the permitted "
                                    "size limit."
                                ),
                            )

                        body.extend(
                            chunk
                        )

                    encoding = (
                        response.encoding
                        or "utf-8"
                    )

                    try:
                        html = bytes(
                            body
                        ).decode(
                            encoding,
                            errors="replace",
                        )

                    except LookupError:
                        html = bytes(
                            body
                        ).decode(
                            "utf-8",
                            errors="replace",
                        )

                    return HTTPCollectionResult(
                        requested_url=(
                            submitted_url
                        ),
                        final_url=current_url,

                        request_success=True,

                        status_code=(
                            status_code
                        ),

                        content_type=(
                            media_type
                        ),

                        content_length_header=(
                            content_length
                        ),

                        downloaded_bytes=(
                            len(body)
                        ),

                        html=html,

                        redirect_count=max(
                            0,
                            len(
                                redirect_chain
                            ) - 1
                        ),

                        redirect_chain=(
                            redirect_chain
                        ),

                        response_too_large=False,

                        content_type_allowed=True,

                        error_type=None,
                        error_message=None,
                    )

            except Exception as error:
                return _empty_result(
                    requested_url=(
                        submitted_url
                    ),
                    final_url=current_url,
                    redirect_chain=(
                        redirect_chain
                    ),
                    error_type=(
                        _classify_http_error(
                            error
                        )
                    ),
                    error_message=str(
                        error
                    ),
                )

        return _empty_result(
            requested_url=submitted_url,
            final_url=current_url,
            redirect_chain=(
                redirect_chain
            ),
            error_type=(
                "too_many_redirects"
            ),
            error_message=(
                "Maximum redirect limit exceeded."
            ),
        )

    finally:
        if owns_client:
            client.close()


def http_result_to_dict(
    result: HTTPCollectionResult
) -> dict:
    return asdict(
        result
    )