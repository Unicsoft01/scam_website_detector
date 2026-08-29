from datetime import (
    datetime,
    timezone,
)

from app.collectors.http_collector import (
    collect_static_page,
)

from app.core.url_security import (
    is_public_destination,
    validate_url,
)

from app.features.domain_features import (
    extract_domain_dns_features,
)

from app.features.html_features import (
    extract_html_features,
)

from app.features.tls_features import (
    extract_tls_features,
)

from app.features.url_features import (
    extract_url_features,
)


def build_heuristic_observation(
    url: str,
    include_rdap: bool = True,
) -> dict:
    """
    Build a complete heuristic observation X_H.

    The function gathers evidence only.
    It does not classify the website.
    """

    collection_timestamp = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    validation = validate_url(
        url
    )

    if not validation.is_valid:
        return {
            "success": False,
            "submitted_url": url,
            "normalized_url": None,
            "collection_timestamp": (
                collection_timestamp
            ),
            "features": None,
            "metadata": {
                "failure_stage":
                    "url_validation",

                "error":
                    validation.reason,
            },
        }

    normalized_url = (
        validation.normalized_url
    )

    # ---------------------------------
    # PHASE 6: URL FEATURES
    # No network connection required.
    # ---------------------------------

    url_features = (
        extract_url_features(
            normalized_url
        )
    )

    # ---------------------------------
    # SAFETY GATE BEFORE NETWORK ACCESS
    # ---------------------------------

    allowed, safety_reason = (
        is_public_destination(
            normalized_url
        )
    )

    if not allowed:
        return {
            "success": False,
            "submitted_url": url,
            "normalized_url": (
                normalized_url
            ),
            "collection_timestamp": (
                collection_timestamp
            ),
            "features": {
                **url_features,
            },
            "metadata": {
                "failure_stage":
                    "destination_validation",

                "error":
                    safety_reason,
            },
        }

    # ---------------------------------
    # PHASE 7: DOMAIN/DNS/RDAP
    # ---------------------------------

    domain_data = (
        extract_domain_dns_features(
            normalized_url,
            include_rdap=(
                include_rdap
            ),
        )
    )

    domain_model_features = {
        "subdomain_count_domain": (
            domain_data[
                "subdomain_count"
            ]
        ),

        "is_ip_hostname": (
            domain_data[
                "is_ip_hostname"
            ]
        ),

        "dns_resolved": (
            domain_data[
                "dns_resolved"
            ]
        ),

        "a_count": (
            domain_data[
                "a_count"
            ]
        ),

        "aaaa_count": (
            domain_data[
                "aaaa_count"
            ]
        ),

        "mx_count": (
            domain_data[
                "mx_count"
            ]
        ),

        "ns_count": (
            domain_data[
                "ns_count"
            ]
        ),

        "has_a_record": (
            domain_data[
                "has_a_record"
            ]
        ),

        "has_aaaa_record": (
            domain_data[
                "has_aaaa_record"
            ]
        ),

        "has_mx_record": (
            domain_data[
                "has_mx_record"
            ]
        ),

        "has_ns_record": (
            domain_data[
                "has_ns_record"
            ]
        ),

        "rdap_available": (
            domain_data[
                "rdap_available"
            ]
        ),

        "domain_age_days": (
            domain_data[
                "domain_age_days"
            ]
        ),
    }

    # ---------------------------------
    # PHASE 8: TLS
    # ---------------------------------

    tls_data = (
        extract_tls_features(
            normalized_url
        )
    )

    tls_model_features = {
        key: tls_data[key]
        for key in [
            "uses_https",
            "tls_connection_success",
            "certificate_present",
            "certificate_valid_now",
            "certificate_expired",
            "hostname_match",
            "days_until_expiry",
            "certificate_lifetime_days",
        ]
    }

    # ---------------------------------
    # PHASE 9: STATIC HTTP COLLECTION
    # ---------------------------------

    http_result = (
        collect_static_page(
            normalized_url
        )
    )

    http_model_features = {
        "http_request_success": int(
            http_result.request_success
        ),

        "http_status_code": (
            http_result.status_code
        ),

        "http_redirect_count": (
            http_result.redirect_count
        ),

        "http_downloaded_bytes": (
            http_result.downloaded_bytes
        ),

        "http_response_too_large": int(
            http_result.response_too_large
        ),

        "http_content_type_allowed": int(
            http_result.content_type_allowed
        ),
    }

    # ---------------------------------
    # PHASE 10: HTML FEATURES
    # ---------------------------------

    html_features = {}

    html_available = bool(
        http_result.html
    )

    if html_available:
        html_features = (
            extract_html_features(
                http_result.final_url
                or normalized_url,
                http_result.html,
            )
        )

    # ---------------------------------
    # COMPLETE X_H
    # ---------------------------------

    x_h = {
        **url_features,
        **domain_model_features,
        **tls_model_features,
        **http_model_features,
        **html_features,
    }

    metadata = {
        "registrable_domain": (
            domain_data[
                "registrable_domain"
            ]
        ),

        "hostname": (
            domain_data[
                "hostname"
            ]
        ),

        "dns_error": (
            domain_data.get(
                "dns_error"
            )
        ),

        "rdap_error": (
            domain_data.get(
                "rdap_error"
            )
        ),

        "registration_date": (
            domain_data.get(
                "registration_date"
            )
        ),

        "expiration_date": (
            domain_data.get(
                "expiration_date"
            )
        ),

        "certificate_issuer": (
            tls_data.get(
                "certificate_issuer"
            )
        ),

        "certificate_subject": (
            tls_data.get(
                "certificate_subject"
            )
        ),

        "certificate_error": (
            tls_data.get(
                "certificate_error"
            )
        ),

        "final_url": (
            http_result.final_url
        ),

        "redirect_chain": (
            http_result.redirect_chain
        ),

        "http_error_type": (
            http_result.error_type
        ),

        "http_error_message": (
            http_result.error_message
        ),

        "html_available": (
            html_available
        ),
    }

    return {
        "success": True,
        "submitted_url": url,
        "normalized_url": (
            normalized_url
        ),
        "collection_timestamp": (
            collection_timestamp
        ),
        "features": x_h,
        "metadata": metadata,
    }