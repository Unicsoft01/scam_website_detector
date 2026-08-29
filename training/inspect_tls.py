import sys

from app.collectors.tls_collector import (
    collect_tls_information,
)

from app.core.url_security import (
    is_public_destination,
    validate_url,
)


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print(
            "python -m training.inspect_tls "
            "https://example.com"
        )
        return

    submitted_url = sys.argv[1]

    print(
        "\nTLS/SSL INSPECTION"
    )

    print(
        "=" * 60
    )

    print(
        f"URL: {submitted_url}"
    )

    print()

    # STEP 1:
    # Validate the URL syntax.
    validation = validate_url(
        submitted_url
    )

    if not validation.is_valid:
        print(
            f"URL rejected: "
            f"{validation.reason}"
        )
        return

    normalized_url = (
        validation.normalized_url
    )

    # STEP 2:
    # Check that the destination is public.
    #
    # This MUST happen before TLS collection.
    allowed, reason = (
        is_public_destination(
            normalized_url
        )
    )

    if not allowed:
        print(
            "Destination blocked:"
        )

        print(
            reason
        )

        return

    # STEP 3:
    # TLS collection happens only after
    # the destination passes our safety check.
    try:
        result = (
            collect_tls_information(
                normalized_url
            )
        )

    except ValueError as error:
        print(
            f"Error: {error}"
        )
        return

    for key, value in (
        result.__dict__.items()
    ):
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()