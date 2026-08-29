import ipaddress
import socket
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

import tldextract


DOMAIN_EXTRACTOR = tldextract.TLDExtract(
    suffix_list_urls=()
)


ALLOWED_SCHEMES = {
    "http",
    "https",
}


@dataclass
class URLValidationResult:
    is_valid: bool
    normalized_url: Optional[str]
    reason: Optional[str]


def normalize_url(value: str) -> Optional[str]:
    """
    Normalize a URL conservatively.

    Returns the normalized URL when valid enough for further
    validation, otherwise returns None.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        parsed = urlsplit(value)
    except Exception:
        return None

    scheme = parsed.scheme.lower()

    if scheme not in ALLOWED_SCHEMES:
        return None

    hostname = parsed.hostname

    if not hostname:
        return None

    hostname = hostname.lower().rstrip(".")

    try:
        port = parsed.port
    except ValueError:
        return None

    # Remove default ports.
    if (
        scheme == "http"
        and port == 80
    ):
        port = None

    if (
        scheme == "https"
        and port == 443
    ):
        port = None

    # Preserve optional user information for now.
    userinfo = ""

    if parsed.username:
        userinfo = parsed.username

        if parsed.password:
            userinfo += f":{parsed.password}"

        userinfo += "@"

    netloc = userinfo + hostname

    if port is not None:
        netloc += f":{port}"

    path = parsed.path or "/"

    normalized = urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            "",
        )
    )

    return normalized


def validate_url(value: str) -> URLValidationResult:
    """
    Perform syntactic URL validation before DNS/network checks.
    """

    if value is None:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL is required.",
        )

    value = str(value).strip()

    if not value:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL is empty.",
        )

    try:
        parsed = urlsplit(value)
    except Exception:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL could not be parsed.",
        )

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="Only HTTP and HTTPS URLs are allowed.",
        )

    if not parsed.hostname:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL does not contain a valid hostname.",
        )

    try:
        parsed.port
    except ValueError:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL contains an invalid port.",
        )

    normalized = normalize_url(value)

    if normalized is None:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL could not be normalized.",
        )

    return URLValidationResult(
        is_valid=True,
        normalized_url=normalized,
        reason=None,
    )


def is_disallowed_ip(ip_value: str) -> bool:
    """
    Return True if an IP address is unsuitable for external scanning.
    """

    try:
        ip = ipaddress.ip_address(ip_value)
    except ValueError:
        return True

    return any(
        [
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_multicast,
            ip.is_reserved,
            ip.is_unspecified,
        ]
    )


def resolve_hostname(hostname: str) -> list[str]:
    """
    Resolve a hostname to its IPv4/IPv6 addresses.

    Raises socket.gaierror if DNS resolution fails.
    """

    results = socket.getaddrinfo(
        hostname,
        None,
        type=socket.SOCK_STREAM,
    )

    addresses = []

    for result in results:
        sockaddr = result[4]

        if not sockaddr:
            continue

        address = sockaddr[0]

        if address not in addresses:
            addresses.append(address)

    return addresses


def is_public_destination(
    url: str
) -> tuple[bool, str]:
    """
    Confirm that a URL resolves only to public destinations.

    Returns:
        (True, message) if allowed
        (False, reason) otherwise
    """

    validation = validate_url(url)

    if not validation.is_valid:
        return (
            False,
            validation.reason
            or "Invalid URL.",
        )

    parsed = urlsplit(
        validation.normalized_url
    )

    hostname = parsed.hostname

    if not hostname:
        return (
            False,
            "Hostname is missing.",
        )

    # Direct IP literal.
    try:
        ipaddress.ip_address(hostname)

        if is_disallowed_ip(hostname):
            return (
                False,
                "Private, local, reserved, or otherwise "
                "non-public IP addresses are not allowed.",
            )

        return (
            True,
            "Destination is a public IP address.",
        )

    except ValueError:
        pass

    # Hostname-based destination.
    lowered = hostname.lower()

    if lowered == "localhost":
        return (
            False,
            "Localhost is not allowed.",
        )

    if lowered.endswith(".localhost"):
        return (
            False,
            "Localhost domains are not allowed.",
        )

    try:
        addresses = resolve_hostname(
            hostname
        )

    except socket.gaierror:
        return (
            False,
            "Hostname could not be resolved.",
        )

    except Exception:
        return (
            False,
            "Hostname resolution failed.",
        )

    if not addresses:
        return (
            False,
            "Hostname did not resolve to an IP address.",
        )

    for address in addresses:
        if is_disallowed_ip(address):
            return (
                False,
                (
                    "Hostname resolves to a private, local, "
                    "reserved, or otherwise non-public address: "
                    f"{address}"
                ),
            )

    return (
        True,
        "Destination resolves only to public IP addresses.",
    )


def get_registrable_domain(
    url: str
) -> Optional[str]:
    """
    Extract the registrable domain for comparison purposes.
    """

    validation = validate_url(url)

    if not validation.is_valid:
        return None

    parsed = urlsplit(
        validation.normalized_url
    )

    hostname = parsed.hostname

    if not hostname:
        return None

    try:
        ipaddress.ip_address(hostname)

        return hostname.lower()

    except ValueError:
        pass

    extracted = DOMAIN_EXTRACTOR(
        hostname
    )

    if (
        extracted.domain
        and extracted.suffix
    ):
        return (
            f"{extracted.domain}."
            f"{extracted.suffix}"
        ).lower()

    return hostname.lower()


def validate_redirect_target(
    redirect_url: str
) -> tuple[bool, str]:
    """
    Apply the same destination-safety checks to a redirect target.
    """

    return is_public_destination(
        redirect_url
    )