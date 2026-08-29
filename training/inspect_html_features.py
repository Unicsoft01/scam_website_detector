import sys

from app.collectors.http_collector import (
    collect_static_page,
)

from app.features.html_features import (
    extract_html_features,
)


def main():
    if len(sys.argv) != 2:
        print("Usage:")

        print(
            "python -m "
            "training.inspect_html_features "
            "https://example.com"
        )

        return

    url = sys.argv[1]

    print(
        "\nSTATIC HTML HEURISTIC FEATURES"
    )

    print(
        "=" * 60
    )

    print(
        f"URL: {url}"
    )

    print()

    collection = (
        collect_static_page(
            url
        )
    )

    if not collection.request_success:
        print(
            "HTML collection failed."
        )

        print(
            f"error_type: "
            f"{collection.error_type}"
        )

        print(
            f"error_message: "
            f"{collection.error_message}"
        )

        return

    if not collection.html:
        print(
            "No HTML was available "
            "for feature extraction."
        )

        print(
            f"status_code: "
            f"{collection.status_code}"
        )

        print(
            f"content_type: "
            f"{collection.content_type}"
        )

        return

    features = (
        extract_html_features(
            collection.final_url
            or url,
            collection.html,
        )
    )

    print(
        f"final_url: "
        f"{collection.final_url}"
    )

    print(
        f"status_code: "
        f"{collection.status_code}"
    )

    print()

    for name, value in (
        features.items()
    ):
        print(
            f"{name}: {value}"
        )


if __name__ == "__main__":
    main()