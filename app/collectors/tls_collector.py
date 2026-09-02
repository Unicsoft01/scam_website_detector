import socket
import ssl
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlsplit

from app.core.url_security import (
    is_public_destination,
    normalize_url,
)


@dataclass
class TLSResult:
    hostname: str
    port: int

    uses_https: bool
    tls_connection_success: bool
    certificate_present: bool

    certificate_valid_now: Optional[bool]
    certificate_expired: Optional[bool]

    not_before: Optional[str]
    not_after: Optional[str]

    days_until_expiry: Optional[int]
    certificate_lifetime_days: Optional[int]

    issuer: Optional[str]
    subject: Optional[str]

    hostname_match: Optional[bool]

    certificate_error: Optional[str]


def _name_tuple_to_string(
    name_tuple
) -> Optional[str]:
    """
    Convert Python's certificate subject/issuer tuple
    into a readable string.
    """

    if not name_tuple:
        return None

    parts = []

    for rdn in name_tuple:
        for key, value in rdn:
            parts.append(
                f"{key}={value}"
            )

    return ", ".join(parts)


def _parse_certificate_date(
    value: Optional[str]
) -> Optional[datetime]:
    """
    Convert OpenSSL certificate date strings to timezone-aware
    datetime objects.
    """

    if not value:
        return None

    try:
        timestamp = ssl.cert_time_to_seconds(
            value
        )

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

    except Exception:
        return None


def collect_tls_information(
    url: str,
    timeout: float = 7.0,
) -> TLSResult:
    """
    Collect TLS certificate information for an HTTPS URL.

    This function does not classify the website.
    It only records transport-security observations.
    """

    normalized = normalize_url(
        url
    )

    if normalized is None:
        raise ValueError(
            "URL must be a valid HTTP or HTTPS URL."
        )

    allowed, reason = (
        is_public_destination(
            normalized
        )
    )

    if not allowed:
        raise ValueError(
            "TLS collection blocked: "
            f"{reason}"
        )

    parsed = urlsplit(
        normalized
    )

    hostname = (
        parsed.hostname
        or ""
    )

    uses_https = (
        parsed.scheme.lower()
        == "https"
    )

    port = (
        parsed.port
        if parsed.port is not None
        else (
            443
            if uses_https
            else 80
        )
    )

    if not uses_https:
        return TLSResult(
            hostname=hostname,
            port=port,

            uses_https=False,
            tls_connection_success=False,
            certificate_present=False,

            certificate_valid_now=None,
            certificate_expired=None,

            not_before=None,
            not_after=None,

            days_until_expiry=None,
            certificate_lifetime_days=None,

            issuer=None,
            subject=None,

            hostname_match=None,

            certificate_error=(
                "URL does not use HTTPS"
            ),
        )

    context = (
        ssl.create_default_context()
    )

    try:
        with socket.create_connection(
            (hostname, port),
            timeout=timeout,
        ) as tcp_socket:

            with context.wrap_socket(
                tcp_socket,
                server_hostname=hostname,
            ) as tls_socket:

                certificate = (
                    tls_socket.getpeercert()
                )

                if not certificate:
                    return TLSResult(
                        hostname=hostname,
                        port=port,

                        uses_https=True,
                        tls_connection_success=True,
                        certificate_present=False,

                        certificate_valid_now=None,
                        certificate_expired=None,

                        not_before=None,
                        not_after=None,

                        days_until_expiry=None,
                        certificate_lifetime_days=None,

                        issuer=None,
                        subject=None,

                        hostname_match=None,

                        certificate_error=(
                            "Peer certificate not available"
                        ),
                    )

                not_before_raw = (
                    certificate.get(
                        "notBefore"
                    )
                )

                not_after_raw = (
                    certificate.get(
                        "notAfter"
                    )
                )

                not_before_dt = (
                    _parse_certificate_date(
                        not_before_raw
                    )
                )

                not_after_dt = (
                    _parse_certificate_date(
                        not_after_raw
                    )
                )

                now = datetime.now(
                    timezone.utc
                )

                certificate_valid_now = None
                certificate_expired = None
                days_until_expiry = None
                certificate_lifetime_days = None

                if (
                    not_before_dt
                    and not_after_dt
                ):
                    certificate_valid_now = (
                        not_before_dt
                        <= now
                        <= not_after_dt
                    )

                    certificate_expired = (
                        now
                        > not_after_dt
                    )

                    days_until_expiry = (
                        not_after_dt
                        - now
                    ).days

                    certificate_lifetime_days = (
                        not_after_dt
                        - not_before_dt
                    ).days

                hostname_match = True

                try:
                    ssl.match_hostname(
                        certificate,
                        hostname,
                    )

                except Exception:
                    hostname_match = False

                issuer = (
                    _name_tuple_to_string(
                        certificate.get(
                            "issuer"
                        )
                    )
                )

                subject = (
                    _name_tuple_to_string(
                        certificate.get(
                            "subject"
                        )
                    )
                )

                return TLSResult(
                    hostname=hostname,
                    port=port,

                    uses_https=True,
                    tls_connection_success=True,
                    certificate_present=True,

                    certificate_valid_now=(
                        certificate_valid_now
                    ),

                    certificate_expired=(
                        certificate_expired
                    ),

                    not_before=(
                        not_before_raw
                    ),

                    not_after=(
                        not_after_raw
                    ),

                    days_until_expiry=(
                        days_until_expiry
                    ),

                    certificate_lifetime_days=(
                        certificate_lifetime_days
                    ),

                    issuer=issuer,
                    subject=subject,

                    hostname_match=(
                        hostname_match
                    ),

                    certificate_error=None,
                )

    except ssl.SSLCertVerificationError as error:
        return TLSResult(
            hostname=hostname,
            port=port,

            uses_https=True,
            tls_connection_success=False,
            certificate_present=False,

            certificate_valid_now=False,
            certificate_expired=None,

            not_before=None,
            not_after=None,

            days_until_expiry=None,
            certificate_lifetime_days=None,

            issuer=None,
            subject=None,

            hostname_match=None,

            certificate_error=(
                f"CERTIFICATE_VERIFICATION_ERROR: "
                f"{error}"
            ),
        )

    except ssl.SSLError as error:
        return TLSResult(
            hostname=hostname,
            port=port,

            uses_https=True,
            tls_connection_success=False,
            certificate_present=False,

            certificate_valid_now=None,
            certificate_expired=None,

            not_before=None,
            not_after=None,

            days_until_expiry=None,
            certificate_lifetime_days=None,

            issuer=None,
            subject=None,

            hostname_match=None,

            certificate_error=(
                f"TLS_ERROR: {error}"
            ),
        )

    except socket.timeout:
        return TLSResult(
            hostname=hostname,
            port=port,

            uses_https=True,
            tls_connection_success=False,
            certificate_present=False,

            certificate_valid_now=None,
            certificate_expired=None,

            not_before=None,
            not_after=None,

            days_until_expiry=None,
            certificate_lifetime_days=None,

            issuer=None,
            subject=None,

            hostname_match=None,

            certificate_error="TIMEOUT",
        )

    except socket.gaierror as error:
        return TLSResult(
            hostname=hostname,
            port=port,

            uses_https=True,
            tls_connection_success=False,
            certificate_present=False,

            certificate_valid_now=None,
            certificate_expired=None,

            not_before=None,
            not_after=None,

            days_until_expiry=None,
            certificate_lifetime_days=None,

            issuer=None,
            subject=None,

            hostname_match=None,

            certificate_error=(
                f"DNS_ERROR: {error}"
            ),
        )

    except Exception as error:
        return TLSResult(
            hostname=hostname,
            port=port,

            uses_https=True,
            tls_connection_success=False,
            certificate_present=False,

            certificate_valid_now=None,
            certificate_expired=None,

            not_before=None,
            not_after=None,

            days_until_expiry=None,
            certificate_lifetime_days=None,

            issuer=None,
            subject=None,

            hostname_match=None,

            certificate_error=str(
                error
            ),
        )


def tls_result_to_dict(
    result: TLSResult
) -> dict:
    return asdict(
        result
    )