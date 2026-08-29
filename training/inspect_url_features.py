import sys

from app.features.url_features import (
    extract_url_features,
)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage:"
        )

        print(
            "python -m "
            "training.inspect_url_features "
            "\"https://example.com/login?a=1\""
        )

        return

    url = sys.argv[1]

    try:
        features = (
            extract_url_features(
                url
            )
        )

    except ValueError as error:
        print(
            f"Error: {error}"
        )

        return

    print(
        "\nURL-LEVEL HEURISTIC FEATURES"
    )

    print(
        "=" * 60
    )

    print(
        f"URL: {url}"
    )

    print()

    for feature_name, value in (
        features.items()
    ):
        print(
            f"{feature_name}: {value}"
        )


if __name__ == "__main__":
    main()