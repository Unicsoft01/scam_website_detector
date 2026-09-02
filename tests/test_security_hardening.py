from app.core.url_security import (
    MAX_URL_LENGTH,
    is_public_destination,
    validate_url,
)


def test_http_url_is_supported():
    result = validate_url(
        "http://example.com/"
    )

    assert result.is_valid is True


def test_https_url_is_supported():
    result = validate_url(
        "https://example.com/"
    )

    assert result.is_valid is True


def test_ftp_is_rejected():
    result = validate_url(
        "ftp://example.com/"
    )

    assert result.is_valid is False


def test_file_scheme_is_rejected():
    result = validate_url(
        "file:///etc/passwd"
    )

    assert result.is_valid is False


def test_embedded_credentials_are_rejected():
    result = validate_url(
        "https://user:password@example.com/"
    )

    assert result.is_valid is False


def test_overlong_url_is_rejected():
    value = (
        "https://example.com/"
        + ("a" * MAX_URL_LENGTH)
    )

    result = validate_url(
        value
    )

    assert result.is_valid is False


def test_control_character_is_rejected():
    result = validate_url(
        "https://example.com/\nsecret"
    )

    assert result.is_valid is False


def test_loopback_is_not_public():
    allowed, _ = is_public_destination(
        "http://127.0.0.1/"
    )

    assert allowed is False


def test_private_ipv4_is_not_public():
    allowed, _ = is_public_destination(
        "http://192.168.1.1/"
    )

    assert allowed is False


def test_link_local_is_not_public():
    allowed, _ = is_public_destination(
        "http://169.254.169.254/"
    )

    assert allowed is False


def test_ipv6_loopback_is_not_public():
    allowed, _ = is_public_destination(
        "http://[::1]/"
    )

    assert allowed is False


def test_localhost_is_not_public():
    allowed, _ = is_public_destination(
        "http://localhost/"
    )

    assert allowed is False


def test_database_port_is_rejected():
    result = validate_url(
        "http://example.com:3306/"
    )

    assert result.is_valid is False


def test_ssh_port_is_rejected():
    result = validate_url(
        "http://example.com:22/"
    )

    assert result.is_valid is False
    