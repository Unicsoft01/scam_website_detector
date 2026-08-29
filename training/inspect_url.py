import sys
from urllib.parse import urlsplit

from app.core.url_security import (
    get_registrable_domain,
    is_public_destination,
    normalize_url,
    validate_url,
)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage:"
        )

        print(
            "python training\\inspect_url.py "
            "https://example.com"
        )

        return

    submitted_url = sys.argv[1]

    print(
        "\nURL INSPECTION"
    )

    print(
        "=" * 60
    )

    print(
        f"Submitted URL: "
        f"{submitted_url}"
    )

    validation = validate_url(
        submitted_url
    )

    print(
        f"Valid syntax: "
        f"{validation.is_valid}"
    )

    if not validation.is_valid:
        print(
            f"Reason: "
            f"{validation.reason}"
        )

        return

    normalized = (
        validation.normalized_url
    )

    print(
        f"Normalized URL: "
        f"{normalized}"
    )

    parsed = urlsplit(
        normalized
    )

    print(
        f"Scheme: "
        f"{parsed.scheme}"
    )

    print(
        f"Hostname: "
        f"{parsed.hostname}"
    )

    print(
        f"Port: "
        f"{parsed.port}"
    )

    print(
        f"Path: "
        f"{parsed.path}"
    )

    print(
        f"Query: "
        f"{parsed.query}"
    )

    print(
        f"Fragment: "
        f"{parsed.fragment}"
    )

    print(
        f"Registrable domain: "
        f"{get_registrable_domain(normalized)}"
    )

    allowed, reason = (
        is_public_destination(
            normalized
        )
    )

    print(
        f"Public destination: "
        f"{allowed}"
    )

    print(
        f"Destination result: "
        f"{reason}"
    )


if __name__ == "__main__":
    main()