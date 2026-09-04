from pathlib import Path
from urllib.parse import urlparse
import urllib.request

import pandas as pd


INPUT_PATH = Path(
    "data/experiments/v1_1/scamferret_revalidation_candidates.csv"
)

OUTPUT_DIR = Path(
    "data/experiments/v1_1/scamferret_historical_html"
)

MANIFEST_PATH = Path(
    "data/experiments/v1_1/scamferret_historical_html_manifest.csv"
)


CATEGORY_MAP = {
    "cryptocurrency": "cryptocurrency",
    "investment": "investment",
    "online_shopping": "online_shopping_english",
    "technical_support": "technical_support",
}


BASE_URL = (
    "https://raw.githubusercontent.com/"
    "ScamFerret/artifact/master/"
    "dataset_training/scam_websites"
)


def hostname_from_url(url):
    try:
        host = urlparse(
            str(url)
        ).hostname

        if host:
            return host.lower().strip(".")

    except Exception:
        pass

    return None


def candidate_filenames(url, registrable_domain):
    """
    ScamFerret archive names normally use
    the hostname, followed by .html.gz.

    We try both:
    1. exact URL hostname
    2. registrable domain

    because some records use www/subdomains.
    """

    values = []

    host = hostname_from_url(url)

    if host:
        values.append(
            f"{host}.html.gz"
        )

        if host.startswith("www."):
            values.append(
                f"{host[4:]}.html.gz"
            )

    domain = str(
        registrable_domain
    ).lower().strip()

    if domain and domain != "nan":
        values.append(
            f"{domain}.html.gz"
        )

    # preserve order but remove duplicates
    return list(
        dict.fromkeys(values)
    )


def try_download(url, destination):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "scam-website-detector-research/1.0"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            data = response.read()

        destination.write_bytes(
            data
        )

        return True, None

    except Exception as exc:
        return False, str(exc)


def main():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}"
        )

    df = pd.read_csv(
        INPUT_PATH
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    for index, row in df.iterrows():

        category = str(
            row["scam_category"]
        ).strip()

        repo_category = CATEGORY_MAP.get(
            category
        )

        if not repo_category:

            results.append(
                {
                    "registrable_domain":
                        row["registrable_domain"],
                    "scam_category":
                        category,
                    "source_url":
                        row["url"],
                    "archive_found":
                        0,
                    "archive_filename":
                        None,
                    "archive_url":
                        None,
                    "local_path":
                        None,
                    "error":
                        "unsupported_category",
                }
            )

            continue

        filenames = candidate_filenames(
            row["url"],
            row["registrable_domain"],
        )

        found = False
        final_error = None

        print(
            f"[{index + 1}/{len(df)}] "
            f"{row['registrable_domain']}"
        )

        for filename in filenames:

            raw_url = (
                f"{BASE_URL}/"
                f"{repo_category}/"
                f"toppage_html/"
                f"{filename}"
            )

            category_dir = (
                OUTPUT_DIR /
                repo_category
            )

            category_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination = (
                category_dir /
                filename
            )

            print(
                f"    trying: {filename}"
            )

            success, error = try_download(
                raw_url,
                destination,
            )

            if success:

                print(
                    "    FOUND"
                )

                results.append(
                    {
                        "registrable_domain":
                            row[
                                "registrable_domain"
                            ],
                        "scam_category":
                            category,
                        "source_url":
                            row["url"],
                        "archive_found":
                            1,
                        "archive_filename":
                            filename,
                        "archive_url":
                            raw_url,
                        "local_path":
                            str(destination),
                        "error":
                            None,
                    }
                )

                found = True
                break

            final_error = error

        if not found:

            print(
                "    NOT FOUND"
            )

            results.append(
                {
                    "registrable_domain":
                        row[
                            "registrable_domain"
                        ],
                    "scam_category":
                        category,
                    "source_url":
                        row["url"],
                    "archive_found":
                        0,
                    "archive_filename":
                        None,
                    "archive_url":
                        None,
                    "local_path":
                        None,
                    "error":
                        final_error,
                }
            )

    manifest = pd.DataFrame(
        results
    )

    manifest.to_csv(
        MANIFEST_PATH,
        index=False,
    )

    print()
    print("=" * 68)
    print(
        "SCAMFERRET HISTORICAL HTML DOWNLOAD"
    )
    print("=" * 68)

    print(
        "TOTAL CANDIDATES:",
        len(manifest),
    )

    print(
        "ARCHIVES FOUND:",
        int(
            manifest[
                "archive_found"
            ].sum()
        ),
    )

    print(
        "ARCHIVES MISSING:",
        int(
            (
                manifest[
                    "archive_found"
                ] == 0
            ).sum()
        ),
    )

    print()
    print(
        "FOUND BY CATEGORY:"
    )

    print(
        pd.crosstab(
            manifest[
                "scam_category"
            ],
            manifest[
                "archive_found"
            ],
        )
    )

    print()
    print(
        f"MANIFEST: {MANIFEST_PATH}"
    )


if __name__ == "__main__":
    main()