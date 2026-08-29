import httpx

from unittest.mock import patch

from app.collectors.http_collector import (
    collect_static_page,
)


def make_mock_client(
    handler
):
    transport = (
        httpx.MockTransport(
            handler
        )
    )

    return httpx.Client(
        transport=transport,
        follow_redirects=False,
    )


@patch(
    "app.collectors.http_collector.is_public_destination"
)
def test_collect_valid_html(
    mock_public
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    def handler(request):
        return httpx.Response(
            200,
            headers={
                "Content-Type":
                    "text/html; charset=utf-8"
            },
            content=(
                b"<html>"
                b"<body>Hello</body>"
                b"</html>"
            ),
        )

    with make_mock_client(
        handler
    ) as client:

        result = collect_static_page(
            "https://example.com",
            client=client,
        )

    assert (
        result.request_success
        is True
    )

    assert (
        result.status_code
        == 200
    )

    assert (
        result.content_type
        == "text/html"
    )

    assert (
        result.content_type_allowed
        is True
    )

    assert (
        "Hello"
        in result.html
    )


@patch(
    "app.collectors.http_collector.is_public_destination"
)
def test_reject_non_html_content(
    mock_public
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    def handler(request):
        return httpx.Response(
            200,
            headers={
                "Content-Type":
                    "application/zip"
            },
            content=b"fake zip data",
        )

    with make_mock_client(
        handler
    ) as client:

        result = collect_static_page(
            "https://example.com/file.zip",
            client=client,
        )

    assert (
        result.request_success
        is True
    )

    assert (
        result.content_type_allowed
        is False
    )

    assert result.html is None

    assert (
        result.error_type
        == "unsupported_content_type"
    )


@patch(
    "app.collectors.http_collector.is_public_destination"
)
def test_reject_large_declared_response(
    mock_public
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    def handler(request):
        return httpx.Response(
            200,
            headers={
                "Content-Type":
                    "text/html",

                "Content-Length":
                    "5000000",
            },
            content=b"",
        )

    with make_mock_client(
        handler
    ) as client:

        result = collect_static_page(
            "https://example.com",
            max_response_bytes=1000,
            client=client,
        )

    assert (
        result.response_too_large
        is True
    )

    assert result.html is None


@patch(
    "app.collectors.http_collector.is_public_destination"
)
def test_streaming_size_limit(
    mock_public
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    def handler(request):
        return httpx.Response(
            200,
            headers={
                "Content-Type":
                    "text/html"
            },
            content=(
                b"A" * 2000
            ),
        )

    with make_mock_client(
        handler
    ) as client:

        result = collect_static_page(
            "https://example.com",
            max_response_bytes=1000,
            client=client,
        )

    assert (
        result.response_too_large
        is True
    )

    assert result.html is None


@patch(
    "app.collectors.http_collector.is_public_destination"
)
def test_safe_redirect(
    mock_public
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    def handler(request):
        if (
            str(request.url)
            == "https://example.com/"
        ):
            return httpx.Response(
                302,
                headers={
                    "Location":
                        "/final"
                },
            )

        return httpx.Response(
            200,
            headers={
                "Content-Type":
                    "text/html"
            },
            content=(
                b"<html>Final</html>"
            ),
        )

    with make_mock_client(
        handler
    ) as client:

        result = collect_static_page(
            "https://example.com",
            client=client,
        )

    assert (
        result.request_success
        is True
    )

    assert (
        result.redirect_count
        == 1
    )

    assert (
        result.final_url
        == "https://example.com/final"
    )

    assert (
        "Final"
        in result.html
    )


def test_private_redirect_is_blocked():
    def safety_check(url):
        if (
            "127.0.0.1"
            in url
        ):
            return (
                False,
                "Private destination blocked",
            )

        return (
            True,
            "Public destination",
        )

    def handler(request):
        return httpx.Response(
            302,
            headers={
                "Location":
                    "http://127.0.0.1/admin"
            },
        )

    with patch(
        "app.collectors.http_collector.is_public_destination",
        side_effect=safety_check,
    ):

        with make_mock_client(
            handler
        ) as client:

            result = (
                collect_static_page(
                    "https://example.com",
                    client=client,
                )
            )

    assert (
        result.request_success
        is False
    )

    assert (
        result.error_type
        == "unsafe_redirect"
    )


@patch(
    "app.collectors.http_collector.is_public_destination"
)
def test_connection_failure_does_not_crash(
    mock_public
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    def handler(request):
        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    with make_mock_client(
        handler
    ) as client:

        result = collect_static_page(
            "https://example.com",
            client=client,
        )

    assert (
        result.request_success
        is False
    )

    assert result.html is None

    assert (
        result.error_type
        == "connection_error"
    )



# 
def test_redirect_to_localhost_is_blocked():
    def safety_check(url):
        if "localhost" in url:
            return (
                False,
                "Localhost is not allowed.",
            )

        return (
            True,
            "Public destination",
        )

    def handler(request):
        return httpx.Response(
            302,
            headers={
                "Location":
                    "http://localhost/admin"
            },
        )

    with patch(
        "app.collectors.http_collector.is_public_destination",
        side_effect=safety_check,
    ):

        with make_mock_client(
            handler
        ) as client:

            result = (
                collect_static_page(
                    "https://example.com",
                    client=client,
                )
            )

    assert (
        result.request_success
        is False
    )

    assert (
        result.error_type
        == "unsafe_redirect"
    )