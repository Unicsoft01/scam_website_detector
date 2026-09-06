from pathlib import Path
import pandas as pd


BASE = Path(
    "data/experiments/v1_1"
)

MANIFEST = (
    BASE
    / "final_dataset_split_manifest.csv"
)

OUTPUT = (
    BASE
    / "final_hybrid_test_dataset.csv"
)


def find_feature_dataset():
    required_metadata = {
        "url",
        "registrable_domain",
        "binary_label",
        "scam_category",
        "source",
    }

    candidates = []

    for path in BASE.glob("*.csv"):
        if path.name in {
            MANIFEST.name,
            OUTPUT.name,
        }:
            continue

        try:
            df = pd.read_csv(
                path,
                nrows=5,
            )
        except Exception:
            continue

        if not required_metadata.issubset(
            set(df.columns)
        ):
            continue

        # Feature datasets normally have
        # substantially more than the metadata fields.
        if len(df.columns) > 12:
            candidates.append(path)

    preferred = [
        "final_common_dataset.csv",
        "common_hybrid_dataset.csv",
        "full_hybrid_dataset.csv",
        "hybrid_dataset.csv",
    ]

    for name in preferred:
        path = BASE / name

        if path in candidates:
            return path

    if len(candidates) == 1:
        return candidates[0]

    print(
        "\nCandidate feature datasets:"
    )

    for path in candidates:
        print(" -", path)

    raise RuntimeError(
        "Unable to uniquely identify final common feature dataset."
    )


def main():
    if not MANIFEST.exists():
        raise FileNotFoundError(
            "Final split manifest does not exist."
        )

    manifest = pd.read_csv(
        MANIFEST
    )

    feature_file = (
        find_feature_dataset()
    )

    print(
        "FEATURE DATASET:",
        feature_file,
    )

    features = pd.read_csv(
        feature_file
    )

    common_test = manifest[
        (
            manifest["split"]
            == "testing"
        )
        &
        (
            manifest[
                "heuristic_eligible"
            ] == 1
        )
        &
        (
            manifest[
                "behavioural_eligible"
            ] == 1
        )
        &
        (
            manifest[
                "hybrid_eligible"
            ] == 1
        )
    ].copy()

    if common_test.empty:
        raise RuntimeError(
            "No common hybrid-evaluable test rows found."
        )

    final = common_test[
        [
            "url",
            "registrable_domain",
        ]
    ].merge(
        features,
        on=[
            "url",
            "registrable_domain",
        ],
        how="inner",
        suffixes=("", "_feature"),
    )

    if final.empty:
        raise RuntimeError(
            "Test rows did not match the feature dataset."
        )

    final.to_csv(
        OUTPUT,
        index=False,
    )

    print(
        "\nFINAL COMMON TEST DATASET CREATED"
    )

    print(
        "ROWS:",
        len(final),
    )

    print(
        "UNIQUE DOMAINS:",
        final[
            "registrable_domain"
        ].nunique(),
    )

    print(
        "\nCLASS DISTRIBUTION:"
    )

    print(
        final[
            "binary_label"
        ].value_counts()
    )

    print(
        "\nSaved:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()