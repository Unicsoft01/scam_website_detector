from unittest.mock import patch

from app.collectors.tls_collector import (
    TLSResult,
)
from app.features.tls_features import (
    extract_tls_features,
)


@patch(
    "app.features.tls_features.collect_tls_information"
)
def test_tls_feature_conversion(
    mock_collect_tls,
):
    mock_collect_tls.return_value = TLSResult(
        hostname="example.com",
        port=443,

        uses_https=True,
        tls_connection_success=True,
        certificate_present=True,

        certificate_valid_now=True,
        certificate_expired=False,

        not_before=(
            "Jan 1 00:00:00 2026 GMT"
        ),

        not_after=(
            "Jan 1 00:00:00 2027 GMT"
        ),

        days_until_expiry=100,
        certificate_lifetime_days=365,

        issuer="Example CA",
        subject="example.com",

        hostname_match=True,

        certificate_error=None,
    )

    features = (
        extract_tls_features(
            "https://example.com"
        )
    )

    assert (
        features["uses_https"]
        == 1
    )

    assert (
        features[
            "tls_connection_success"
        ]
        == 1
    )

    assert (
        features[
            "certificate_present"
        ]
        == 1
    )

    assert (
        features[
            "certificate_valid_now"
        ]
        == 1
    )

    assert (
        features[
            "certificate_expired"
        ]
        == 0
    )

    assert (
        features[
            "hostname_match"
        ]
        == 1
    )

    assert (
        features[
            "days_until_expiry"
        ]
        == 100
    )