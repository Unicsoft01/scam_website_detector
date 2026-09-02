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

MAX_URL_LENGTH = 2048


# Defence-in-depth only. A port not listed here is not
# automatically considered safe; destination checks still apply.
BLOCKED_PORTS = {
    0,
    20,
    21,
    22,
    23,
    25,
    53,
    110,
    135,
    137,
    138,
    139,
    143,
    445,
    465,
    587,
    993,
    995,
    1433,
    1521,
    2375,
    2376,
    3306,
    3389,
    5432,
    6379,
    8086,
    9200,
    11211,
    27017,
}


@dataclass
class URLValidationResult:
    is_valid: bool
    normalized_url: Optional[str]
    reason: Optional[str]


def _contains_control_characters(value: str) -> bool:
    return any(
        ord(character) < 32
        or ord(character) == 127
        for character in value
    )


def _is_valid_hostname(hostname: str) -> bool:
    hostname = hostname.strip().rstrip(".")

    if not hostname:
        return False

    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        pass

    try:
        ascii_hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return False

    if len(ascii_hostname) > 253:
        return False

    labels = ascii_hostname.split(".")

    if any(not label for label in labels):
        return False

    for label in labels:
        if len(label) > 63:
            return False

        if label.startswith("-") or label.endswith("-"):
            return False

        for character in label:
            if not (
                character.isalnum()
                or character == "-"
            ):
                return False

    return True


def _normalized_netloc(
    hostname: str,
    port: Optional[int],
) -> str:
    try:
        ip = ipaddress.ip_address(hostname)

        if isinstance(ip, ipaddress.IPv6Address):
            netloc = f"[{hostname}]"
        else:
            netloc = hostname

    except ValueError:
        netloc = hostname

    if port is not None:
        netloc += f":{port}"

    return netloc


def normalize_url(value: str) -> Optional[str]:
    """
    Normalize a URL conservatively.

    Returns the normalized URL when suitable for further validation,
    otherwise returns None.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    if len(value) > MAX_URL_LENGTH:
        return None

    if _contains_control_characters(value):
        return None

    try:
        parsed = urlsplit(value)
    except Exception:
        return None

    scheme = parsed.scheme.lower()

    if scheme not in ALLOWED_SCHEMES:
        return None

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        return None

    hostname = parsed.hostname

    if not hostname:
        return None

    hostname = hostname.lower().rstrip(".")

    if not _is_valid_hostname(hostname):
        return None

    try:
        port = parsed.port
    except ValueError:
        return None

    if port is not None:
        if not 1 <= port <= 65535:
            return None

        if port in BLOCKED_PORTS:
            return None

    if scheme == "http" and port == 80:
        port = None

    if scheme == "https" and port == 443:
        port = None

    netloc = _normalized_netloc(
        hostname,
        port,
    )

    path = parsed.path or "/"

    return urlunsplit(
        (
            scheme,
            netloc,
            path,
            parsed.query,
            "",
        )
    )


def validate_url(value: str) -> URLValidationResult:
    """
    Perform conservative syntactic URL validation before DNS/network
    checks.
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

    if len(value) > MAX_URL_LENGTH:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL exceeds the permitted length.",
        )

    if _contains_control_characters(value):
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL contains invalid control characters.",
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

    hostname = parsed.hostname

    if not hostname:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL does not contain a valid hostname.",
        )

    if (
        parsed.username is not None
        or parsed.password is not None
    ):
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason=(
                "URLs containing embedded credentials "
                "are not permitted."
            ),
        )

    hostname = hostname.lower().rstrip(".")

    if not _is_valid_hostname(hostname):
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL contains a malformed hostname.",
        )

    try:
        port = parsed.port
    except ValueError:
        return URLValidationResult(
            is_valid=False,
            normalized_url=None,
            reason="URL contains an invalid port.",
        )

    if port is not None:
        if not 1 <= port <= 65535:
            return URLValidationResult(
                is_valid=False,
                normalized_url=None,
                reason="URL contains an invalid port.",
            )

        if port in BLOCKED_PORTS:
            return URLValidationResult(
                is_valid=False,
                normalized_url=None,
                reason=(
                    "The requested network port is "
                    "not permitted for website analysis."
                ),
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
    Resolve a hostname to all discovered IPv4/IPv6 addresses.
    """

    results = socket.getaddrinfo(
        hostname,
        None,
        type=socket.SOCK_STREAM,
    )

    addresses: list[str] = []

    for result in results:
        sockaddr = result[4]

        if not sockaddr:
            continue

        address = sockaddr[0]

        if address not in addresses:
            addresses.append(address)

    return addresses


def is_public_destination(
    url: str,
) -> tuple[bool, str]:
    """
    Confirm that a URL currently resolves only to public destinations.

    This reduces SSRF exposure but does not by itself eliminate DNS
    rebinding/TOCTOU risk. Callers must also revalidate redirects and
    browser requests and should use network isolation where practical.
    """

    validation = validate_url(url)

    if not validation.is_valid:
        return (
            False,
            validation.reason or "Invalid URL.",
        )

    parsed = urlsplit(validation.normalized_url)
    hostname = parsed.hostname

    if not hostname:
        return (
            False,
            "Hostname is missing.",
        )

    try:
        ipaddress.ip_address(hostname)

        if is_disallowed_ip(hostname):
            return (
                False,
                (
                    "Private, local, reserved, or otherwise "
                    "non-public IP addresses are not allowed."
                ),
            )

        return (
            True,
            "Destination is a public IP address.",
        )

    except ValueError:
        pass

    lowered = hostname.lower()

    if (
        lowered == "localhost"
        or lowered.endswith(".localhost")
    ):
        return (
            False,
            "Localhost destinations are not allowed.",
        )

    try:
        addresses = resolve_hostname(hostname)

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
    url: str,
) -> Optional[str]:
    """
    Extract the registrable domain for comparison purposes.
    """

    validation = validate_url(url)

    if not validation.is_valid:
        return None

    parsed = urlsplit(validation.normalized_url)
    hostname = parsed.hostname

    if not hostname:
        return None

    try:
        ipaddress.ip_address(hostname)
        return hostname.lower()

    except ValueError:
        pass

    extracted = DOMAIN_EXTRACTOR(hostname)

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
    redirect_url: str,
) -> tuple[bool, str]:
    """
    Apply the same validation and public-destination checks to every
    redirect target.
    """

    return is_public_destination(
        redirect_url
    )
