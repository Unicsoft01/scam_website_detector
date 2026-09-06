from pathlib import Path
import pandas as pd


BASE = Path("data/experiments/v1_1")

OUTPUT = BASE / "final_dataset_split_manifest.csv"


REQUIRED_COLUMNS = {
    "url",
    "registrable_domain",
    "binary_label",
    "scam_category",
    "source",
}


def find_candidate_files():
    candidates = []

    for path in BASE.glob("*.csv"):
        if path.name == OUTPUT.name:
            continue

        try:
            df = pd.read_csv(path, nrows=5)
        except Exception:
            continue

        columns = set(df.columns)

        if REQUIRED_COLUMNS.issubset(columns):
            candidates.append(path)

    return candidates


def choose_source():
    candidates = find_candidate_files()

    preferred_names = [
        "final_common_dataset.csv",
        "common_hybrid_dataset.csv",
        "hybrid_dataset.csv",
        "full_hybrid_dataset.csv",
        "feature_dataset.csv",
    ]

    for name in preferred_names:
        path = BASE / name

        if path in candidates:
            return path

    split_candidates = []

    for path in candidates:
        try:
            df = pd.read_csv(path, nrows=5)

            if "split" in df.columns:
                split_candidates.append(path)

        except Exception:
            pass

    if len(split_candidates) == 1:
        return split_candidates[0]

    print("\nSuitable CSV files found:")

    for path in candidates:
        print(" -", path)

    raise RuntimeError(
        "\nCould not safely determine the final dataset automatically.\n"
        "Create or identify the final common H/B dataset before Phase 34."
    )


def assign_split(data):
    """
    Creates a reproducible domain-level 70/15/15 split.

    This MUST only be used if a final split has not already
    been created during model development.
    """

    from sklearn.model_selection import train_test_split

    data = data.copy()

    data["registrable_domain"] = (
        data["registrable_domain"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    if data["registrable_domain"].duplicated().any():
        raise RuntimeError(
            "Duplicate registrable domains found. "
            "Final dataset must contain one independent domain per row."
        )

    train, temporary = train_test_split(
        data,
        test_size=0.30,
        random_state=42,
        stratify=data["binary_label"],
    )

    validation, testing = train_test_split(
        temporary,
        test_size=0.50,
        random_state=42,
        stratify=temporary["binary_label"],
    )

    train = train.copy()
    validation = validation.copy()
    testing = testing.copy()

    train["split"] = "training"
    validation["split"] = "validation"
    testing["split"] = "testing"

    return pd.concat(
        [train, validation, testing],
        ignore_index=True,
    )


def main():
    source = choose_source()

    print("SOURCE DATASET:")
    print(source)

    data = pd.read_csv(source)

    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise RuntimeError(
            f"Missing required columns: {sorted(missing)}"
        )

    if "split" not in data.columns:
        print(
            "\nWARNING: No existing split column found."
        )
        print(
            "Creating reproducible 70/15/15 domain-level split "
            "with random_state=42."
        )

        data = assign_split(data)

    allowed = {
        "training",
        "validation",
        "testing",
    }

    actual = set(
        data["split"]
        .dropna()
        .astype(str)
        .str.lower()
    )

    if not actual.issubset(allowed):
        raise RuntimeError(
            f"Unexpected split names: {sorted(actual)}"
        )

    for column in [
        "heuristic_eligible",
        "behavioural_eligible",
        "hybrid_eligible",
    ]:
        if column not in data.columns:
            data[column] = 1

    manifest_columns = [
        "url",
        "registrable_domain",
        "binary_label",
        "scam_category",
        "source",
        "split",
        "heuristic_eligible",
        "behavioural_eligible",
        "hybrid_eligible",
    ]

    manifest = data[
        manifest_columns
    ].copy()

    manifest.to_csv(
        OUTPUT,
        index=False,
    )

    print("\nFINAL SPLIT MANIFEST CREATED")
    print("============================")
    print("ROWS:", len(manifest))
    print(
        "\nSPLIT COUNTS:"
    )
    print(
        manifest["split"].value_counts()
    )

    print(
        "\nCLASS BY SPLIT:"
    )
    print(
        pd.crosstab(
            manifest["split"],
            manifest["binary_label"],
        )
    )

    print(
        "\nUNIQUE DOMAINS:",
        manifest["registrable_domain"].nunique(),
    )

    print(
        "\nSaved:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()