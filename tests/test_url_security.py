from unittest.mock import patch

from app.core.url_security import (
    get_registrable_domain,
    is_disallowed_ip,
    is_public_destination,
    normalize_url,
    validate_redirect_target,
    validate_url,
)


def test_normalize_basic_https_url():
    result = normalize_url(
        "HTTPS://Example.COM:443/test#section"
    )

    assert result == (
        "https://example.com/test"
    )


def test_normalize_default_http_port():
    result = normalize_url(
        "http://Example.COM:80/"
    )

    assert result == (
        "http://example.com/"
    )


def test_normalize_keeps_non_default_port():
    result = normalize_url(
        "https://example.com:8443/test"
    )

    assert result == (
        "https://example.com:8443/test"
    )


def test_normalize_preserves_query_string():
    result = normalize_url(
        "https://example.com/login?a=1&b=2"
    )

    assert result == (
        "https://example.com/login?a=1&b=2"
    )


def test_normalize_removes_fragment():
    result = normalize_url(
        "https://example.com/page#hello"
    )

    assert result == (
        "https://example.com/page"
    )


def test_reject_missing_scheme():
    result = validate_url(
        "example.com"
    )

    assert result.is_valid is False


def test_reject_ftp_scheme():
    result = validate_url(
        "ftp://example.com"
    )

    assert result.is_valid is False


def test_reject_file_scheme():
    result = validate_url(
        "file:///C:/Windows"
    )

    assert result.is_valid is False


def test_accept_http():
    result = validate_url(
        "http://example.com"
    )

    assert result.is_valid is True


def test_accept_https():
    result = validate_url(
        "https://example.com"
    )

    assert result.is_valid is True


def test_reject_invalid_port():
    result = validate_url(
        "https://example.com:999999"
    )

    assert result.is_valid is False


def test_loopback_ipv4_is_disallowed():
    assert (
        is_disallowed_ip(
            "127.0.0.1"
        )
        is True
    )


def test_private_ipv4_is_disallowed():
    assert (
        is_disallowed_ip(
            "192.168.1.1"
        )
        is True
    )


def test_private_10_range_is_disallowed():
    assert (
        is_disallowed_ip(
            "10.0.0.1"
        )
        is True
    )


def test_link_local_ipv4_is_disallowed():
    assert (
        is_disallowed_ip(
            "169.254.1.1"
        )
        is True
    )


def test_loopback_ipv6_is_disallowed():
    assert (
        is_disallowed_ip(
            "::1"
        )
        is True
    )


def test_public_ipv4_is_allowed():
    assert (
        is_disallowed_ip(
            "8.8.8.8"
        )
        is False
    )


def test_localhost_is_rejected():
    allowed, reason = (
        is_public_destination(
            "http://localhost"
        )
    )

    assert allowed is False
    assert "Localhost" in reason


def test_direct_private_ip_is_rejected():
    allowed, reason = (
        is_public_destination(
            "http://192.168.1.10"
        )
    )

    assert allowed is False


def test_direct_loopback_is_rejected():
    allowed, reason = (
        is_public_destination(
            "http://127.0.0.1"
        )
    )

    assert allowed is False


@patch(
    "app.core.url_security.resolve_hostname"
)
def test_hostname_resolving_private_ip_is_rejected(
    mock_resolve,
):
    mock_resolve.return_value = [
        "192.168.1.20"
    ]

    allowed, reason = (
        is_public_destination(
            "https://example.com"
        )
    )

    assert allowed is False


@patch(
    "app.core.url_security.resolve_hostname"
)
def test_hostname_resolving_public_ip_is_allowed(
    mock_resolve,
):
    mock_resolve.return_value = [
        "8.8.8.8"
    ]

    allowed, reason = (
        is_public_destination(
            "https://example.com"
        )
    )

    assert allowed is True


@patch(
    "app.core.url_security.resolve_hostname"
)
def test_mixed_public_private_resolution_is_rejected(
    mock_resolve,
):
    mock_resolve.return_value = [
        "8.8.8.8",
        "10.0.0.10",
    ]

    allowed, reason = (
        is_public_destination(
            "https://example.com"
        )
    )

    assert allowed is False


def test_registrable_domain():
    result = get_registrable_domain(
        "https://login.security.example.co.uk/test"
    )

    assert result == "example.co.uk"


def test_redirect_to_private_ip_is_rejected():
    allowed, reason = (
        validate_redirect_target(
            "http://127.0.0.1/admin"
        )
    )

    assert allowed is False



#
# 
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

