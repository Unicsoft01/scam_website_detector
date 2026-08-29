import ssl

from unittest.mock import (
    MagicMock,
    patch,
)

from app.collectors.tls_collector import (
    collect_tls_information,
)


def test_http_url_has_no_tls():
    result = (
        collect_tls_information(
            "http://example.com"
        )
    )

    assert (
        result.uses_https
        is False
    )

    assert (
        result.tls_connection_success
        is False
    )

    assert (
        result.certificate_present
        is False
    )

    assert (
        result.certificate_valid_now
        is None
    )




@patch(
    "app.collectors.tls_collector.socket.create_connection"
)
@patch(
    "app.collectors.tls_collector.ssl.create_default_context"
)
def test_valid_tls_certificate(
    mock_create_context,
    mock_create_connection,
):
    mock_tcp = MagicMock()

    mock_create_connection.return_value.__enter__.return_value = (
        mock_tcp
    )

    mock_tls_socket = MagicMock()

    mock_tls_socket.getpeercert.return_value = {
        "subject": (
            (
                (
                    "commonName",
                    "example.com",
                ),
            ),
        ),

        "issuer": (
            (
                (
                    "organizationName",
                    "Example CA",
                ),
            ),
        ),

        "notBefore": (
            "Jan  1 00:00:00 2026 GMT"
        ),

        "notAfter": (
            "Jan  1 00:00:00 2028 GMT"
        ),

        "subjectAltName": (
            (
                "DNS",
                "example.com",
            ),
        ),
    }

    mock_context = (
        MagicMock()
    )

    mock_context.wrap_socket.return_value.__enter__.return_value = (
        mock_tls_socket
    )

    mock_create_context.return_value = (
        mock_context
    )

    result = (
        collect_tls_information(
            "https://example.com"
        )
    )

    assert (
        result.uses_https
        is True
    )

    assert (
        result.tls_connection_success
        is True
    )

    assert (
        result.certificate_present
        is True
    )

    assert (
        result.hostname_match
        is True
    )

    assert (
        result.certificate_lifetime_days
        is not None
    )

# Test an expired or verification-invalid certificate safely
@patch(
    "app.collectors.tls_collector.socket.create_connection"
)
@patch(
    "app.collectors.tls_collector.ssl.create_default_context"
)
def test_certificate_verification_error(
    mock_create_context,
    mock_create_connection,
):
    mock_tcp = MagicMock()

    mock_create_connection.return_value.__enter__.return_value = (
        mock_tcp
    )

    mock_context = (
        MagicMock()
    )

    mock_context.wrap_socket.side_effect = (
        ssl.SSLCertVerificationError(
            1,
            "certificate verify failed"
        )
    )

    mock_create_context.return_value = (
        mock_context
    )

    result = (
        collect_tls_information(
            "https://example.com"
        )
    )

    assert (
        result.uses_https
        is True
    )

    assert (
        result.tls_connection_success
        is False
    )

    assert (
        result.certificate_present
        is False
    )

    assert (
        result.certificate_error
        is not None
    )    