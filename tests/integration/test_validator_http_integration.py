from app.core.url_security import (
    validate_url,
    is_public_destination,
)
from app.collectors.http_collector import (
    collect_static_page,
)


def test_invalid_url_is_rejected_before_collection():

    validation = validate_url(
        "ftp://example.com/"
    )

    assert validation.is_valid is False


def test_private_destination_is_blocked():

    allowed, _ = is_public_destination(
        "http://127.0.0.1/"
    )

    assert allowed is False


def test_safe_public_page_can_be_collected():

    validation = validate_url(
        "https://example.com/"
    )

    assert validation.is_valid is True

    allowed, _ = is_public_destination(
        validation.normalized_url
    )

    assert allowed is True

    result = collect_static_page(
        validation.normalized_url
    )

    assert result.request_success is True
    assert result.content_type_allowed is True
    assert result.html is not None