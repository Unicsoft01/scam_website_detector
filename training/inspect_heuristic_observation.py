import sys

from app.services.heuristic_observation_service import (
    build_heuristic_observation,
)


def main():
    if len(sys.argv) != 2:
        print("Usage:")

        print(
            "python -m "
            "training.inspect_heuristic_observation "
            "https://example.com"
        )

        return

    url = sys.argv[1]

    print(
        "\nCOMPLETE HEURISTIC OBSERVATION X_H"
    )

    print(
        "=" * 70
    )

    print(
        f"URL: {url}"
    )

    print()

    observation = (
        build_heuristic_observation(
            url
        )
    )

    print(
        f"success: "
        f"{observation['success']}"
    )

    print(
        f"normalized_url: "
        f"{observation['normalized_url']}"
    )

    print(
        f"collection_timestamp: "
        f"{observation['collection_timestamp']}"
    )

    print(
        "\nFEATURES"
    )

    print(
        "-" * 70
    )

    features = (
        observation.get(
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
        observation.get(
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