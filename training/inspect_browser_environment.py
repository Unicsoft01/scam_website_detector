import sys

from app.collectors.browser_environment import (
    observe_public_url,
)


def main():
    if len(sys.argv) != 2:
        print("Usage:")

        print(
            "python -m "
            "training.inspect_browser_environment "
            "https://example.com"
        )

        return

    url = sys.argv[1]

    print(
        "\nCONTROLLED BROWSER OBSERVATION"
    )

    print(
        "=" * 70
    )

    print(
        f"URL: {url}"
    )

    print()

    result = (
        observe_public_url(
            url
        )
    )

    print(
        f"success: "
        f"{result.success}"
    )

    print(
        f"final_url: "
        f"{result.final_url}"
    )

    print(
        f"main_status_code: "
        f"{result.main_status_code}"
    )

    print(
        f"navigation_count: "
        f"{len(result.navigation_urls)}"
    )

    print(
        f"request_count: "
        f"{len(result.request_urls)}"
    )

    print(
        f"blocked_request_count: "
        f"{len(result.blocked_requests)}"
    )

    print(
        f"failed_request_count: "
        f"{len(result.failed_requests)}"
    )

    print(
        f"popup_count: "
        f"{result.popup_count}"
    )

    print(
        f"dialog_count: "
        f"{result.dialog_count}"
    )

    print(
        f"download_count: "
        f"{result.download_count}"
    )

    print(
        f"page_error_count: "
        f"{result.page_error_count}"
    )

    print(
        f"error_type: "
        f"{result.error_type}"
    )

    print(
        f"error_message: "
        f"{result.error_message}"
    )

    print(
        "\nNAVIGATIONS"
    )

    print(
        "-" * 70
    )

    for navigation in (
        result.navigation_urls
    ):
        print(
            navigation
        )

    print(
        "\nFIRST 15 NETWORK REQUESTS"
    )

    print(
        "-" * 70
    )

    for request_url in (
        result.request_urls[:15]
    ):
        print(
            request_url
        )

    if result.blocked_requests:
        print(
            "\nBLOCKED REQUESTS"
        )

        print(
            "-" * 70
        )

        for blocked in (
            result.blocked_requests[:15]
        ):
            print(
                blocked
            )


if __name__ == "__main__":
    main()