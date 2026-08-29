import ipaddress
import re
from pathlib import PurePosixPath
from urllib.parse import parse_qsl, urlsplit

import tldextract

from app.core.url_security import normalize_url


DOMAIN_EXTRACTOR = tldextract.TLDExtract(
    suffix_list_urls=()
)


SUSPICIOUS_TOKENS = {
    "login",
    "signin",
    "verify",
    "verification",
    "secure",
    "security",
    "account",
    "update",
    "confirm",
    "password",
    "bank",
    "wallet",
    "payment",
    "invoice",
    "support",
    "crypto",
    "bitcoin",
    "investment",
    "bonus",
    "free",
    "gift",
    "prize",
    "urgent",
    "recover",
    "recovery",
    "authenticate",
}


SUSPICIOUS_EXTENSIONS = {
    ".exe",
    ".scr",
    ".bat",
    ".cmd",
    ".msi",
    ".apk",
    ".jar",
    ".zip",
    ".rar",
    ".7z",
    ".iso",
}


SPECIAL_CHARACTERS = set(
    "@?=&%_~!$^*()+{}[]|\\;:,<>"
)


def count_special_characters(value: str) -> int:
    """
    Count selected special characters in a URL string.
    """

    return sum(
        1
        for character in value
        if character in SPECIAL_CHARACTERS
    )


def count_percent_encoded_sequences(
    value: str
) -> int:
    """
    Count percent-encoded sequences such as %20 or %2F.
    """

    pattern = r"%[0-9A-Fa-f]{2}"

    return len(
        re.findall(
            pattern,
            value
        )
    )


def count_repeated_characters(
    value: str
) -> int:
    """
    Count character runs where the same character appears
    three or more times consecutively.

    Example:
    aaa
    ----
    1111
    """

    pattern = r"(.)\1{2,}"

    matches = re.findall(
        pattern,
        value
    )

    return len(matches)


def is_ip_address(
    hostname: str
) -> bool:
    """
    Return True when hostname is an IPv4 or IPv6 literal.
    """

    if not hostname:
        return False

    try:
        ipaddress.ip_address(
            hostname
        )

        return True

    except ValueError:
        return False


def get_domain_parts(
    hostname: str
) -> tuple[str, str, str]:
    """
    Return:
        subdomain
        domain
        suffix
    """

    if not hostname:
        return "", "", ""

    if is_ip_address(hostname):
        return "", hostname, ""

    extracted = DOMAIN_EXTRACTOR(
        hostname
    )

    return (
        extracted.subdomain or "",
        extracted.domain or "",
        extracted.suffix or "",
    )


def count_subdomains(
    hostname: str
) -> int:
    """
    Count subdomain labels.

    Example:
    login.secure.example.com
    gives 2:
        login
        secure
    """

    subdomain, _, _ = (
        get_domain_parts(
            hostname
        )
    )

    if not subdomain:
        return 0

    return len(
        [
            part
            for part in subdomain.split(".")
            if part
        ]
    )


def extract_tokens(
    value: str
) -> list[str]:
    """
    Split a URL into lowercase lexical tokens.
    """

    return [
        token
        for token in re.split(
            r"[^A-Za-z0-9]+",
            value.lower()
        )
        if token
    ]


def count_suspicious_tokens(
    value: str
) -> int:
    """
    Count occurrences of predefined suspicious lexical tokens.
    """

    tokens = extract_tokens(
        value
    )

    return sum(
        1
        for token in tokens
        if token in SUSPICIOUS_TOKENS
    )


def get_file_extension(
    path: str
) -> str:
    """
    Return the final file extension from a URL path.
    """

    if not path:
        return ""

    suffix = PurePosixPath(
        path
    ).suffix

    return suffix.lower()


def has_suspicious_extension(
    path: str
) -> bool:
    """
    Check whether the URL path ends in a suspicious file extension.
    """

    extension = get_file_extension(
        path
    )

    return (
        extension
        in SUSPICIOUS_EXTENSIONS
    )


def extract_url_features(
    url: str
) -> dict:
    """
    Extract URL-level heuristic features without contacting
    the destination website.
    """

    normalized = normalize_url(
        url
    )

    if normalized is None:
        raise ValueError(
            "URL must be a valid HTTP or HTTPS URL."
        )

    parsed = urlsplit(
        normalized
    )

    hostname = (
        parsed.hostname
        or ""
    ).lower()

    path = parsed.path or "/"

    query = parsed.query or ""

    fragment = parsed.fragment or ""

    subdomain, domain, suffix = (
        get_domain_parts(
            hostname
        )
    )

    if suffix:
        registrable_domain = (
            f"{domain}.{suffix}"
        )

    else:
        registrable_domain = domain

    parameters = parse_qsl(
        query,
        keep_blank_values=True
    )

    features = {
        "url_length": len(
            normalized
        ),

        "hostname_length": len(
            hostname
        ),

        "domain_length": len(
            registrable_domain
        ),

        "path_length": len(
            path
        ),

        "query_length": len(
            query
        ),

        "fragment_length": len(
            fragment
        ),

        "dot_count": normalized.count(
            "."
        ),

        "hyphen_count": normalized.count(
            "-"
        ),

        "digit_count": sum(
            character.isdigit()
            for character in normalized
        ),

        "special_character_count": (
            count_special_characters(
                normalized
            )
        ),

        "underscore_count": normalized.count(
            "_"
        ),

        "at_symbol_count": normalized.count(
            "@"
        ),

        "percent_encoded_count": (
            count_percent_encoded_sequences(
                normalized
            )
        ),

        "subdomain_count": (
            count_subdomains(
                hostname
            )
        ),

        "has_ip_address": int(
            is_ip_address(
                hostname
            )
        ),

        "parameter_count": len(
            parameters
        ),

        "repeated_character_count": (
            count_repeated_characters(
                normalized
            )
        ),

        "suspicious_token_count": (
            count_suspicious_tokens(
                normalized
            )
        ),

        "has_suspicious_extension": int(
            has_suspicious_extension(
                path
            )
        ),

        "domain_is_long": int(
            len(registrable_domain) > 30
        ),

        "url_is_long": int(
            len(normalized) > 100
        ),
    }

    return features