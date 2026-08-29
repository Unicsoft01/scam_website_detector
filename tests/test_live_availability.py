from unittest.mock import patch

from app.collectors.http_collector import (
    HTTPCollectionResult,
)

from app.services.live_availability_service import (
    audit_live_url,
)


def _html_result(
    status_code=200,
):
    return HTTPCollectionResult(
        requested_url=(
            "https://example.com/"
        ),

        final_url=(
            "https://example.com/"
        ),

        request_success=True,

        status_code=(
            status_code
        ),

        content_type=(
            "text/html"
        ),

        content_length_header=100,

        downloaded_bytes=100,

        html=(
            "<html><body>"
            "Example"
            "</body></html>"
        ),

        redirect_count=0,

        redirect_chain=[
            "https://example.com/"
        ],

        response_too_large=False,

        content_type_allowed=True,

        error_type=None,
        error_message=None,
    )


@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
@patch(
    "app.services.live_availability_service."
    "is_public_destination"
)
@patch(
    "app.services.live_availability_service."
    "collect_static_page"
)
def test_accessible_html(
    mock_collect,
    mock_public,
    mock_dns,
):
    mock_dns.return_value = (
        "ok",
        None,
    )

    mock_public.return_value = (
        True,
        "Public destination",
    )

    mock_collect.return_value = (
        _html_result(
            200
        )
    )

    result = audit_live_url(
        "https://example.com"
    )

    assert (
        result.live_status
        == "accessible"
    )

    assert (
        result.behavioural_eligible
        == 1
    )

    assert (
        result.hybrid_eligible
        == 1
    )


@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
def test_dns_failure(
    mock_dns,
):
    mock_dns.return_value = (
        "dns_failure",
        "Host not found",
    )

    result = audit_live_url(
        "https://example.com"
    )

    assert (
        result.live_status
        == "dns_failure"
    )

    assert (
        result.behavioural_eligible
        == 0
    )


@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
def test_blocked_destination(
    mock_dns,
):
    mock_dns.return_value = (
        "blocked",
        "Private destination",
    )

    result = audit_live_url(
        "http://127.0.0.1"
    )

    assert (
        result.live_status
        == "blocked"
    )

    assert (
        result.behavioural_eligible
        == 0
    )



@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
@patch(
    "app.services.live_availability_service."
    "is_public_destination"
)
@patch(
    "app.services.live_availability_service."
    "collect_static_page"
)
def test_non_html(
    mock_collect,
    mock_public,
    mock_dns,
):
    mock_dns.return_value = (
        "ok",
        None,
    )

    mock_public.return_value = (
        True,
        "Public",
    )

    mock_collect.return_value = (
        HTTPCollectionResult(
            requested_url=(
                "https://example.com/file.pdf"
            ),

            final_url=(
                "https://example.com/file.pdf"
            ),

            request_success=True,

            status_code=200,

            content_type=(
                "application/pdf"
            ),

            content_length_header=500,

            downloaded_bytes=0,

            html=None,

            redirect_count=0,

            redirect_chain=[],

            response_too_large=False,

            content_type_allowed=False,

            error_type=(
                "unsupported_content_type"
            ),

            error_message=(
                "Unsupported content type"
            ),
        )
    )

    result = audit_live_url(
        "https://example.com/file.pdf"
    )

    assert (
        result.live_status
        == "non_html"
    )

    assert (
        result.behavioural_eligible
        == 0
    )




@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
@patch(
    "app.services.live_availability_service."
    "is_public_destination"
)
@patch(
    "app.services.live_availability_service."
    "collect_static_page"
)
def test_http_404_is_inaccessible(
    mock_collect,
    mock_public,
    mock_dns,
):
    mock_dns.return_value = (
        "ok",
        None,
    )

    mock_public.return_value = (
        True,
        "Public",
    )

    mock_collect.return_value = (
        _html_result(
            404
        )
    )

    result = audit_live_url(
        "https://example.com/missing"
    )

    assert (
        result.live_status
        == "inaccessible"
    )

    assert (
        result.behavioural_eligible
        == 0
    )



@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
@patch(
    "app.services.live_availability_service."
    "is_public_destination"
)
@patch(
    "app.services.live_availability_service."
    "collect_static_page"
)
def test_timeout(
    mock_collect,
    mock_public,
    mock_dns,
):
    mock_dns.return_value = (
        "ok",
        None,
    )

    mock_public.return_value = (
        True,
        "Public",
    )

    mock_collect.return_value = (
        HTTPCollectionResult(
            requested_url=(
                "https://example.com"
            ),

            final_url=None,

            request_success=False,

            status_code=None,
            content_type=None,
            content_length_header=None,

            downloaded_bytes=0,
            html=None,

            redirect_count=0,
            redirect_chain=[],

            response_too_large=False,
            content_type_allowed=False,

            error_type="timeout",

            error_message=(
                "Request timed out"
            ),
        )
    )

    result = audit_live_url(
        "https://example.com"
    )

    assert (
        result.live_status
        == "timeout"
    )





@patch(
    "app.services.live_availability_service."
    "_hostname_dns_status"
)
@patch(
    "app.services.live_availability_service."
    "is_public_destination"
)
@patch(
    "app.services.live_availability_service."
    "collect_static_page"
)
def test_tls_failure(
    mock_collect,
    mock_public,
    mock_dns,
):
    mock_dns.return_value = (
        "ok",
        None,
    )

    mock_public.return_value = (
        True,
        "Public",
    )

    mock_collect.return_value = (
        HTTPCollectionResult(
            requested_url=(
                "https://example.com"
            ),

            final_url=None,

            request_success=False,

            status_code=None,
            content_type=None,
            content_length_header=None,

            downloaded_bytes=0,
            html=None,

            redirect_count=0,
            redirect_chain=[],

            response_too_large=False,
            content_type_allowed=False,

            error_type="tls_error",

            error_message=(
                "Certificate verification failed"
            ),
        )
    )

    result = audit_live_url(
        "https://example.com"
    )

    assert (
        result.live_status
        == "tls_failure"
    )