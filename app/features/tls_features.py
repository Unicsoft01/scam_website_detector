from app.collectors.tls_collector import (
    collect_tls_information,
)


def extract_tls_features(
    url: str
) -> dict:
    """
    Convert TLS observations into structured heuristic features.
    """

    result = (
        collect_tls_information(
            url
        )
    )

    return {
        "uses_https": int(
            result.uses_https
        ),

        "tls_connection_success": int(
            result.tls_connection_success
        ),

        "certificate_present": int(
            result.certificate_present
        ),

        "certificate_valid_now": (
            None
            if result.certificate_valid_now
            is None
            else int(
                result.certificate_valid_now
            )
        ),

        "certificate_expired": (
            None
            if result.certificate_expired
            is None
            else int(
                result.certificate_expired
            )
        ),

        "hostname_match": (
            None
            if result.hostname_match
            is None
            else int(
                result.hostname_match
            )
        ),

        "days_until_expiry": (
            result.days_until_expiry
        ),

        "certificate_lifetime_days": (
            result.certificate_lifetime_days
        ),

        # Metadata rather than direct numeric RF-H features.
        "certificate_issuer": (
            result.issuer
        ),

        "certificate_subject": (
            result.subject
        ),

        "certificate_not_before": (
            result.not_before
        ),

        "certificate_not_after": (
            result.not_after
        ),

        "certificate_error": (
            result.certificate_error
        ),
    }