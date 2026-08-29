import sys

from app.services.behavioural_observation_service import (
    build_behavioural_observation,
)


def main():

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python -m "
            "training.inspect_behavioural_observation "
            "https://example.com"
        )

        return

    url = sys.argv[1]

    print(
        "\nCOMPLETE BEHAVIOURAL OBSERVATION X_B"
    )

    print(
        "=" * 70
    )

    print(
        f"URL: {url}"
    )

    print()

    result = (
        build_behavioural_observation(
            url
        )
    )

    print(
        f"success: "
        f"{result['success']}"
    )

    print(
        f"collection_timestamp: "
        f"{result['collection_timestamp']}"
    )

    print(
        "\nFEATURES"
    )

    print(
        "-" * 70
    )

    features = (
        result.get(
            "features"
        )
        or {}
    )

    for name, value in (
        features.items()
    ):

        print(
            f"{name}: {value}"
        )

    print(
        "\nMETADATA"
    )

    print(
        "-" * 70
    )

    metadata = (
        result.get(
            "metadata"
        )
        or {}
    )

    for name, value in (
        metadata.items()
    ):

        print(
            f"{name}: {value}"
        )


if __name__ == "__main__":
    main()