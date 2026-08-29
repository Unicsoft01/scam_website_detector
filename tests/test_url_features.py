import pytest

from app.features.url_features import (
    count_percent_encoded_sequences,
    count_repeated_characters,
    count_special_characters,
    count_subdomains,
    count_suspicious_tokens,
    extract_url_features,
    get_file_extension,
    has_suspicious_extension,
    is_ip_address,
)


def test_basic_url_features():
    features = extract_url_features(
        "https://example.com/"
    )

    assert (
        features["hostname_length"]
        == len("example.com")
    )

    assert (
        features["path_length"]
        == 1
    )

    assert (
        features["query_length"]
        == 0
    )

    assert (
        features["subdomain_count"]
        == 0
    )

    assert (
        features["has_ip_address"]
        == 0
    )


def test_subdomain_count():
    assert (
        count_subdomains(
            "login.secure.example.com"
        )
        == 2
    )


def test_single_subdomain():
    assert (
        count_subdomains(
            "www.example.com"
        )
        == 1
    )


def test_ip_address_detection():
    assert (
        is_ip_address(
            "192.0.2.10"
        )
        is True
    )


def test_normal_domain_not_ip():
    assert (
        is_ip_address(
            "example.com"
        )
        is False
    )


def test_ip_feature():
    features = extract_url_features(
        "http://192.0.2.10/login"
    )

    assert (
        features["has_ip_address"]
        == 1
    )


def test_query_parameter_count():
    features = extract_url_features(
        "https://example.com/page?a=1&b=2&c=3"
    )

    assert (
        features["parameter_count"]
        == 3
    )


def test_no_query_parameters():
    features = extract_url_features(
        "https://example.com/page"
    )

    assert (
        features["parameter_count"]
        == 0
    )


def test_suspicious_token_count():
    count = count_suspicious_tokens(
        "https://example.com/"
        "secure-login/account/verify"
    )

    assert count == 4


def test_non_suspicious_tokens():
    count = count_suspicious_tokens(
        "https://example.com/"
        "about/company/history"
    )

    assert count == 0


def test_percent_encoding_count():
    count = (
        count_percent_encoded_sequences(
            "https://example.com/"
            "login%20secure%2Faccount"
        )
    )

    assert count == 2


def test_repeated_character_count():
    count = (
        count_repeated_characters(
            "https://example.com/"
            "aaa/1111"
        )
    )

    assert count == 2


def test_file_extension():
    extension = get_file_extension(
        "/download/report.pdf"
    )

    assert extension == ".pdf"


def test_suspicious_extension():
    assert (
        has_suspicious_extension(
            "/download/update.exe"
        )
        is True
    )


def test_normal_extension():
    assert (
        has_suspicious_extension(
            "/documents/report.pdf"
        )
        is False
    )


def test_special_character_count():
    count = count_special_characters(
        "https://example.com/"
        "login?id=12&ref=test"
    )

    assert count >= 3


def test_long_url_flag():
    long_path = (
        "a" * 120
    )

    features = extract_url_features(
        f"https://example.com/{long_path}"
    )

    assert (
        features["url_is_long"]
        == 1
    )


def test_short_url_flag():
    features = extract_url_features(
        "https://example.com/"
    )

    assert (
        features["url_is_long"]
        == 0
    )


def test_long_domain_flag():
    domain = (
        "abcdefghijklmnopqrstuvwxyzabcdef"
        ".com"
    )

    features = extract_url_features(
        f"https://{domain}/"
    )

    assert (
        features["domain_is_long"]
        == 1
    )


def test_fragment_not_counted_after_normalization():
    features = extract_url_features(
        "https://example.com/"
        "page#section"
    )

    assert (
        features["fragment_length"]
        == 0
    )


def test_invalid_url_raises_error():
    with pytest.raises(
        ValueError
    ):
        extract_url_features(
            "example.com"
        )