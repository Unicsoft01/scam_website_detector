from unittest.mock import patch

from app.collectors.http_collector import (
    HTTPCollectionResult,
)

from app.services.heuristic_observation_service import (
    build_heuristic_observation,
)


@patch(
    "app.services.heuristic_observation_service."
    "is_public_destination"
)
@patch(
    "app.services.heuristic_observation_service."
    "extract_domain_dns_features"
)
@patch(
    "app.services.heuristic_observation_service."
    "extract_tls_features"
)
@patch(
    "app.services.heuristic_observation_service."
    "collect_static_page"
)
def test_complete_heuristic_observation(
    mock_http,
    mock_tls,
    mock_domain,
    mock_public,
):
    mock_public.return_value = (
        True,
        "Public destination",
    )

    mock_domain.return_value = {
        "hostname":
            "example.com",

        "registrable_domain":
            "example.com",

        "subdomain_count": 0,
        "is_ip_hostname": 0,

        "dns_resolved": 1,

        "a_count": 1,
        "aaaa_count": 0,
        "mx_count": 1,
        "ns_count": 2,

        "has_a_record": 1,
        "has_aaaa_record": 0,
        "has_mx_record": 1,
        "has_ns_record": 1,

        "rdap_available": 1,

        "domain_age_days":
            5000,

        "dns_error": None,
        "rdap_error": None,

        "registration_date":
            "2012-01-01",

        "expiration_date":
            "2030-01-01",
    }

    mock_tls.return_value = {
        "uses_https": 1,

        "tls_connection_success":
            1,

        "certificate_present":
            1,

        "certificate_valid_now":
            1,

        "certificate_expired":
            0,

        "hostname_match":
            1,

        "days_until_expiry":
            100,

        "certificate_lifetime_days":
            365,

        "certificate_issuer":
            "Example CA",

        "certificate_subject":
            "example.com",

        "certificate_error":
            None,
    }

    mock_http.return_value = (
        HTTPCollectionResult(
            requested_url=(
                "https://example.com/"
            ),

            final_url=(
                "https://example.com/"
            ),

            request_success=True,

            status_code=200,

            content_type=(
                "text/html"
            ),

            content_length_header=100,

            downloaded_bytes=100,

            html="""
            <html>
                <body>
                    <form action="/login">
                        <input
                            type="password"
                            name="password"
                        >
                    </form>

                    <a href="/about">
                        About
                    </a>
                </body>
            </html>
            """,

            redirect_count=0,

            redirect_chain=[
                "https://example.com/"
            ],

            response_too_large=False,

            content_type_allowed=True,

            error_type=None,
            error_message=None,
        )
    )

    observation = (
        build_heuristic_observation(
            "https://example.com"
        )
    )

    assert (
        observation["success"]
        is True
    )

    features = (
        observation[
            "features"
        ]
    )

    assert (
        features[
            "uses_https"
        ]
        == 1
    )

    assert (
        features[
            "dns_resolved"
        ]
        == 1
    )

    assert (
        features[
            "form_count"
        ]
        == 1
    )

    assert (
        features[
            "password_field_count"
        ]
        == 1
    )

    assert (
        observation[
            "metadata"
        ][
            "html_available"
        ]
        is True
    )



#    Test the safety gate
@patch(
    "app.services.heuristic_observation_service."
    "is_public_destination"
)
def test_private_destination_is_blocked(
    mock_public,
):
    mock_public.return_value = (
        False,
        "Private destination blocked",
    )

    observation = (
        build_heuristic_observation(
            "http://127.0.0.1"
        )
    )

    assert (
        observation["success"]
        is False
    )

    assert (
        observation[
            "metadata"
        ][
            "failure_stage"
        ]
        == "destination_validation"
    )