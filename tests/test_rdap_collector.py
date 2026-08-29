from unittest.mock import Mock, patch

from app.collectors.rdap_collector import (
    collect_rdap_information,
)


@patch(
    "app.collectors.rdap_collector.httpx.Client"
)
def test_rdap_success(
    mock_client_class
):
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "events": [
            {
                "eventAction": "registration",
                "eventDate": (
                    "2020-01-01T00:00:00Z"
                ),
            },
            {
                "eventAction": "expiration",
                "eventDate": (
                    "2030-01-01T00:00:00Z"
                ),
            },
        ]
    }

    mock_client = Mock()

    mock_client.__enter__ = Mock(
        return_value=mock_client
    )

    mock_client.__exit__ = Mock(
        return_value=False
    )

    mock_client.get.return_value = (
        mock_response
    )

    mock_client_class.return_value = (
        mock_client
    )

    result = (
        collect_rdap_information(
            "example.com"
        )
    )

    assert (
        result.rdap_available
        is True
    )

    assert (
        result.registration_date
        is not None
    )

    assert (
        result.domain_age_days
        is not None
    )


@patch(
    "app.collectors.rdap_collector.httpx.Client"
)
def test_rdap_non_200(
    mock_client_class
):
    mock_response = Mock()

    mock_response.status_code = 404

    mock_client = Mock()

    mock_client.__enter__ = Mock(
        return_value=mock_client
    )

    mock_client.__exit__ = Mock(
        return_value=False
    )

    mock_client.get.return_value = (
        mock_response
    )

    mock_client_class.return_value = (
        mock_client
    )

    result = (
        collect_rdap_information(
            "example.invalid"
        )
    )

    assert (
        result.rdap_available
        is False
    )

    assert (
        result.domain_age_days
        is None
    )