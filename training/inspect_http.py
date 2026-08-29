import sys

from app.collectors.http_collector import (
    collect_static_page,
)


def main():
    if len(sys.argv) != 2:
        print("Usage:")

        print(
            "python -m training.inspect_http "
            "https://example.com"
        )

        return

    url = sys.argv[1]

    print(
        "\nSTATIC WEBPAGE COLLECTION"
    )

    print(
        "=" * 60
    )

    print(
        f"URL: {url}"
    )

    print()

    result = (
        collect_static_page(
            url
        )
    )

    print(
        f"requested_url: "
        f"{result.requested_url}"
    )

    print(
        f"final_url: "
        f"{result.final_url}"
    )

    print(
        f"request_success: "
        f"{result.request_success}"
    )

    print(
        f"status_code: "
        f"{result.status_code}"
    )

    print(
        f"content_type: "
        f"{result.content_type}"
    )

    print(
        f"content_length_header: "
        f"{result.content_length_header}"
    )

    print(
        f"downloaded_bytes: "
        f"{result.downloaded_bytes}"
    )

    print(
        f"redirect_count: "
        f"{result.redirect_count}"
    )

    print(
        f"redirect_chain: "
        f"{result.redirect_chain}"
    )

    print(
        f"response_too_large: "
        f"{result.response_too_large}"
    )

    print(
        f"content_type_allowed: "
        f"{result.content_type_allowed}"
    )

    print(
        f"error_type: "
        f"{result.error_type}"
    )

    print(
        f"error_message: "
        f"{result.error_message}"
    )

    if result.html:
        print(
            "\nHTML PREVIEW"
        )

        print(
            "-" * 60
        )

        preview = (
            result.html[:500]
        )

        print(
            preview
        )


if __name__ == "__main__":
    main()