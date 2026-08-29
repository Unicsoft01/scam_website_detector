from pathlib import Path

import pandas as pd

from app.features.url_features import (
    extract_url_features,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


MASTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_url_index.csv"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "url_level_features.csv"
)


ERROR_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "url_feature_errors.csv"
)


def main():
    if not MASTER_FILE.exists():
        raise FileNotFoundError(
            f"Master dataset not found: "
            f"{MASTER_FILE}"
        )

    df = pd.read_csv(
        MASTER_FILE
    )

    feature_rows = []
    error_rows = []

    total = len(df)

    print(
        f"Extracting URL features "
        f"for {total:,} records..."
    )

    for index, row in (
        df.iterrows()
    ):
        url = row["url"]

        try:
            features = (
                extract_url_features(
                    url
                )
            )

            output_row = {
                "url": url,
                "registrable_domain": (
                    row[
                        "registrable_domain"
                    ]
                ),
                "source": (
                    row["source"]
                ),
                "source_category": (
                    row[
                        "source_category"
                    ]
                ),
                "binary_label": (
                    row["binary_label"]
                ),
                "scam_category": (
                    row["scam_category"]
                ),
            }

            output_row.update(
                features
            )

            feature_rows.append(
                output_row
            )

        except Exception as error:
            error_rows.append(
                {
                    "url": url,
                    "error": str(error),
                }
            )

        if (
            (index + 1) % 1000
            == 0
        ):
            print(
                f"Processed "
                f"{index + 1:,}"
                f"/{total:,}"
            )

    feature_df = pd.DataFrame(
        feature_rows
    )

    error_df = pd.DataFrame(
        error_rows
    )

    feature_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    error_df.to_csv(
        ERROR_FILE,
        index=False
    )

    print(
        "\nURL feature extraction complete."
    )

    print(
        f"Successful records: "
        f"{len(feature_df):,}"
    )

    print(
        f"Failed records: "
        f"{len(error_df):,}"
    )

    print(
        f"\nFeature dataset:\n"
        f"{OUTPUT_FILE}"
    )

    print(
        f"\nError report:\n"
        f"{ERROR_FILE}"
    )


if __name__ == "__main__":
    main()