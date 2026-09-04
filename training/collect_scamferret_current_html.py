from pathlib import Path
from urllib.parse import urlsplit
import gzip
import time

import pandas as pd

from app.collectors.http_collector import collect_static_page
from app.core.url_security import is_public_destination, validate_url
from app.services.live_availability_service import _hostname_dns_status


INPUT_FILE = Path(
    "data/experiments/v1_1/scamferret_revalidation_candidates.csv"
)

OUTPUT_DIR = Path(
    "data/experiments/v1_1/scamferret_current_html"
)

MANIFEST_FILE = Path(
    "data/experiments/v1_1/scamferret_current_html_manifest.csv"
)

DELAY_SECONDS = 1.0


def safe_filename(url: str) -> str:
    """
    Build a filesystem-safe filename from the URL hostname.
    """

    hostname = urlsplit(url).hostname or "unknown"

    hostname = hostname.lower()

    replacements = {
        "/": "_",
        "\\": "_",
        ":": "_",
        "?": "_",
        "*": "_",
        '"': "_",
        "<": "_",
        ">": "_",
        "|": "_",
    }

    for old, new in replacements.items():
        hostname = hostname.replace(old, new)

    return f"{hostname}.current.html.gz"


def collect_current_html(url: str) -> dict:
    """
    Collect current HTML using the same validation,
    DNS and public-destination controls used by the
    live-availability audit.
    """

    record = {
        "submitted_url": url,
        "normalized_url": None,
        "collection_status": None,
        "status_code": None,
        "final_url": None,
        "content_type": None,
        "downloaded_bytes": 0,
        "redirect_count": 0,
        "html_saved": 0,
        "local_path": None,
        "error_type": None,
        "error_message": None,
    }

    # -------------------------------
    # URL validation
    # -------------------------------

    validation = validate_url(url)

    if not validation.is_valid:
        record["collection_status"] = "blocked"
        record["error_type"] = "invalid_url"
        record["error_message"] = validation.reason
        return record

    normalized_url = validation.normalized_url

    record["normalized_url"] = normalized_url

    # -------------------------------
    # DNS/public-IP preflight
    # -------------------------------

    dns_status, dns_reason = _hostname_dns_status(
        normalized_url
    )

    if dns_status != "ok":
        record["collection_status"] = dns_status
        record["error_type"] = dns_status
        record["error_message"] = dns_reason
        return record

    # -------------------------------
    # Public-destination policy
    # -------------------------------

    allowed, reason = is_public_destination(
        normalized_url
    )

    if not allowed:
        record["collection_status"] = "blocked"
        record["error_type"] = "unsafe_destination"
        record["error_message"] = reason
        return record

    # -------------------------------
    # Existing controlled collector
    # -------------------------------

    try:
        result = collect_static_page(
            normalized_url
        )

    except Exception as error:
        record["collection_status"] = "collector_exception"
        record["error_type"] = type(error).__name__
        record["error_message"] = str(error)
        return record

    record["status_code"] = result.status_code
    record["final_url"] = result.final_url
    record["content_type"] = result.content_type
    record["downloaded_bytes"] = result.downloaded_bytes
    record["redirect_count"] = result.redirect_count
    record["error_type"] = result.error_type
    record["error_message"] = result.error_message

    # -------------------------------
    # Classify collection result
    # -------------------------------

    if result.response_too_large:
        record["collection_status"] = "oversized_response"
        return record

    if (
        result.request_success
        and not result.content_type_allowed
    ):
        record["collection_status"] = "non_html"
        return record

    if not result.request_success:
        record["collection_status"] = "collection_failed"
        return record

    if not (
        result.status_code is not None
        and 200 <= result.status_code < 400
        and result.html
    ):
        record["collection_status"] = "inaccessible"
        return record

    record["collection_status"] = "accessible"

    # HTML is returned to main() for saving.
    record["_html"] = result.html

    return record


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    dataframe = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Loaded {len(dataframe)} "
        "ScamFerret revalidation candidates."
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest_rows = []

    for index, row in dataframe.iterrows():

        url = str(row["url"])
        domain = str(row["registrable_domain"])
        category = str(row["scam_category"])

        print(
            f"[{index + 1}/{len(dataframe)}] "
            f"{domain} ({category})"
        )

        result = collect_current_html(
            url
        )

        html = result.pop(
            "_html",
            None,
        )

        if (
            result["collection_status"] == "accessible"
            and html
        ):
            category_directory = (
                OUTPUT_DIR / category
            )

            category_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            filename = safe_filename(
                result["final_url"]
                or url
            )

            output_path = (
                category_directory
                / filename
            )

            try:
                if isinstance(html, str):
                    html_bytes = html.encode(
                        "utf-8",
                        errors="replace",
                    )
                else:
                    html_bytes = bytes(html)

                with gzip.open(
                    output_path,
                    "wb",
                ) as file:
                    file.write(
                        html_bytes
                    )

                result["html_saved"] = 1

                result["local_path"] = str(
                    output_path
                )

            except Exception as error:
                result["html_saved"] = 0
                result["collection_status"] = (
                    "save_failed"
                )
                result["error_type"] = (
                    type(error).__name__
                )
                result["error_message"] = (
                    str(error)
                )

        result["registrable_domain"] = domain
        result["scam_category"] = category

        manifest_rows.append(
            result
        )

        # Save progress after every URL.
        pd.DataFrame(
            manifest_rows
        ).to_csv(
            MANIFEST_FILE,
            index=False,
        )

        print(
            "   status="
            f"{result['collection_status']} "
            "saved="
            f"{result['html_saved']}"
        )

        time.sleep(
            DELAY_SECONDS
        )

    manifest = pd.DataFrame(
        manifest_rows
    )

    print("\n==============================")
    print("COLLECTION COMPLETE")
    print("==============================")

    print(
        "TOTAL:",
        len(manifest),
    )

    print(
        "HTML SAVED:",
        int(
            manifest["html_saved"].sum()
        ),
    )

    print(
        "NOT SAVED:",
        int(
            (
                manifest["html_saved"] == 0
            ).sum()
        ),
    )

    print("\nSTATUS:")
    print(
        manifest[
            "collection_status"
        ].value_counts(
            dropna=False
        )
    )

    print("\nBY CATEGORY:")
    print(
        pd.crosstab(
            manifest["scam_category"],
            manifest["html_saved"],
        )
    )

    print(
        "\nManifest:",
        MANIFEST_FILE,
    )

    print(
        "HTML directory:",
        OUTPUT_DIR,
    )


if __name__ == "__main__":
    main()