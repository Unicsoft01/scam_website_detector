from pathlib import Path

import pandas as pd


FILES = {
    "heuristic":
        Path(
            "data/processed/"
            "heuristic_dataset.csv"
        ),

    "behavioural":
        Path(
            "data/processed/"
            "behavioural_dataset.csv"
        ),

    "hybrid":
        Path(
            "data/processed/"
            "hybrid_dataset.csv"
        ),
}


REQUIRED_METADATA = {
    "url",
    "source",
    "binary_label",
    "scam_category",
}


def inspect_dataset(
    name: str,
    path: Path,
) -> None:

    print()

    print(
        "=" * 72
    )

    print(
        name.upper()
    )

    print(
        "=" * 72
    )

    if not path.exists():

        print(
            f"Missing: {path}"
        )

        return

    df = pd.read_csv(
        path
    )

    print(
        f"Path: {path}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    missing_metadata = (
        REQUIRED_METADATA
        - set(
            df.columns
        )
    )

    print(
        "Required metadata missing: "
        f"{sorted(missing_metadata)}"
    )

    duplicate_urls = (
        df["url"]
        .duplicated()
        .sum()
        if "url" in df.columns
        else "N/A"
    )

    print(
        "Duplicate URLs: "
        f"{duplicate_urls}"
    )

    if "binary_label" in df.columns:

        print()

        print(
            "Label distribution:"
        )

        print(
            df[
                "binary_label"
            ]
            .value_counts(
                dropna=False
            )
            .to_string()
        )

    if "scam_category" in df.columns:

        print()

        print(
            "Category distribution:"
        )

        print(
            df[
                "scam_category"
            ]
            .value_counts(
                dropna=False
            )
            .to_string()
        )

    feature_prefix = (
        "h_"
        if name == "heuristic"
        else (
            "b_"
            if name == "behavioural"
            else None
        )
    )

    if feature_prefix:

        features = [
            column
            for column in df.columns
            if column.startswith(
                feature_prefix
            )
        ]

        print()

        print(
            f"Feature columns: "
            f"{len(features)}"
        )

        if features:

            missing_percentage = (
                df[
                    features
                ]
                .isna()
                .mean()
                .sort_values(
                    ascending=False
                )
                * 100
            )

            print()

            print(
                "Highest feature missingness:"
            )

            print(
                missing_percentage
                .head(10)
                .round(2)
                .to_string()
            )

    elif name == "hybrid":

        h_features = [
            column
            for column in df.columns
            if column.startswith(
                "h_"
            )
        ]

        b_features = [
            column
            for column in df.columns
            if column.startswith(
                "b_"
            )
        ]

        print(
            "Heuristic feature columns: "
            f"{len(h_features)}"
        )

        print(
            "Behavioural feature columns: "
            f"{len(b_features)}"
        )


def main():

    print(
        "\nFEATURE DATASET VALIDATION"
    )

    for name, path in (
        FILES.items()
    ):
        inspect_dataset(
            name,
            path,
        )


if __name__ == "__main__":
    main()