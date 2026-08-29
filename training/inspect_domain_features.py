import sys

from app.features.domain_features import (
    extract_domain_dns_features,
)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage:"
        )

        print(
            "python -m "
            "training.inspect_domain_features "
            "https://example.com"
        )

        return

    url = sys.argv[1]

    print(
        "\nDOMAIN AND DNS FEATURES"
    )

    print(
        "=" * 60
    )

    print(
        f"URL: {url}"
    )

    print()

    try:
        features = (
            extract_domain_dns_features(
                url
            )
        )

    except Exception as error:
        print(
            f"Error: {error}"
        )

        return

    for name, value in (
        features.items()
    ):
        print(
            f"{name}: {value}"
        )


if __name__ == "__main__":
    main()