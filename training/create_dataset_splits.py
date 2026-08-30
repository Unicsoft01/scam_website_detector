from hashlib import sha256
from pathlib import Path

import pandas as pd

from app.ml.splitting import (
    create_grouped_split,
    validate_no_domain_leakage,
)


HYBRID_INPUT = Path(
    "data/processed/cleaned/"
    "hybrid_cleaned.csv"
)

HEURISTIC_INPUT = Path(
    "data/processed/cleaned/"
    "heuristic_cleaned.csv"
)

BEHAVIOURAL_INPUT = Path(
    "data/processed/cleaned/"
    "behavioural_cleaned.csv"
)


SPLIT_ROOT = Path(
    "data/splits"
)

ASSIGNMENTS_OUTPUT = (
    SPLIT_ROOT
    / "split_assignments.csv"
)

SUMMARY_OUTPUT = (
    SPLIT_ROOT
    / "split_summary.csv"
)

MANIFEST_OUTPUT = (
    SPLIT_ROOT
    / "split_manifest.txt"
)


def _read_dataset(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    try:
        dataframe = (
            pd.read_csv(
                path
            )
        )

    except pd.errors.EmptyDataError:

        raise ValueError(
            f"Dataset is empty: {path}"
        )

    if dataframe.empty:

        raise ValueError(
            (
                "Dataset contains no records: "
                f"{path}"
            )
        )

    return dataframe


def _file_sha256(
    path: Path,
) -> str:

    digest = sha256()

    with path.open(
        "rb"
    ) as file:

        for block in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            digest.update(
                block
            )

    return digest.hexdigest()


def _materialise_dataset(
    dataframe: pd.DataFrame,
    assignments: pd.DataFrame,
    dataset_name: str,
) -> None:

    assignment_columns = (
        assignments[
            [
                "url",
                "split",
            ]
        ]
        .drop_duplicates(
            subset=[
                "url"
            ]
        )
    )

    common = dataframe.merge(
        assignment_columns,
        on="url",
        how="inner",
        validate="one_to_one",
    )

    output_directory = (
        SPLIT_ROOT
        / dataset_name
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    mapping = {
        "training":
            "training.csv",

        "validation":
            "validation.csv",

        "testing":
            "testing.csv",
    }

    for (
        split_name,
        filename,
    ) in mapping.items():

        subset = common[
            common[
                "split"
            ]
            == split_name
        ].copy()

        subset.to_csv(
            output_directory
            / filename,

            index=False,
        )


def _build_summary(
    assignments: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    total = len(
        assignments
    )

    for split_name in [
        "training",
        "validation",
        "testing",
    ]:

        subset = assignments[
            assignments[
                "split"
            ]
            == split_name
        ]

        row = {
            "split":
                split_name,

            "rows":
                len(
                    subset
                ),

            "percentage":
                round(
                    (
                        len(subset)
                        / total
                        * 100
                    ),
                    2,
                ),

            "unique_domains":
                subset[
                    "registrable_domain"
                ]
                .nunique(),

            "legitimate_count":
                int(
                    (
                        subset[
                            "binary_label"
                        ]
                        == 0
                    ).sum()
                ),

            "scam_count":
                int(
                    (
                        subset[
                            "binary_label"
                        ]
                        == 1
                    ).sum()
                ),
        }

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    )


def _print_distribution(
    dataframe: pd.DataFrame,
    column: str,
) -> None:

    print()

    print(
        column.upper()
    )

    table = pd.crosstab(
        dataframe[
            "split"
        ],

        dataframe[
            column
        ],

        margins=True,
    )

    print(
        table.to_string()
    )


def main():

    print()

    print(
        "PHASE 16 — DOMAIN-GROUPED "
        "TRAIN / VALIDATION / TEST SPLIT"
    )

    print(
        "=" * 72
    )

    hybrid = _read_dataset(
        HYBRID_INPUT
    )

    heuristic = _read_dataset(
        HEURISTIC_INPUT
    )

    behavioural = _read_dataset(
        BEHAVIOURAL_INPUT
    )

    print(
        f"Common hybrid records: "
        f"{len(hybrid)}"
    )

    print(
        "Unique registrable domains: "
        f"{hybrid['registrable_domain'].nunique()}"
    )

    result = (
        create_grouped_split(
            hybrid
        )
    )

    assignments = (
        result.assignments
        .copy()
    )

    # -----------------------------------------
    # Keep only metadata in assignment file.
    # -----------------------------------------

    assignment_metadata = [
        column
        for column in [
            "url",
            "registrable_domain",
            "source",
            "source_category",
            "binary_label",
            "scam_category",
            "original_label",
            "split",
        ]
        if column
        in assignments.columns
    ]

    saved_assignments = (
        assignments[
            assignment_metadata
        ]
        .copy()
    )

    SPLIT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    saved_assignments.to_csv(
        ASSIGNMENTS_OUTPUT,
        index=False,
    )

    # -----------------------------------------
    # Materialise same URL assignment for
    # all three experimental configurations.
    # -----------------------------------------

    _materialise_dataset(
        heuristic,
        saved_assignments,
        "heuristic",
    )

    _materialise_dataset(
        behavioural,
        saved_assignments,
        "behavioural",
    )

    _materialise_dataset(
        hybrid,
        saved_assignments,
        "hybrid",
    )

    # -----------------------------------------
    # Validate domain separation again.
    # -----------------------------------------

    training = assignments[
        assignments[
            "split"
        ]
        == "training"
    ]

    validation = assignments[
        assignments[
            "split"
        ]
        == "validation"
    ]

    testing = assignments[
        assignments[
            "split"
        ]
        == "testing"
    ]

    validate_no_domain_leakage(
        training,
        validation,
        testing,
    )

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    summary = (
        _build_summary(
            assignments
        )
    )

    summary.to_csv(
        SUMMARY_OUTPUT,
        index=False,
    )

    # -----------------------------------------
    # Reproducibility manifest
    # -----------------------------------------

    manifest = [
        "PHASE 16 SPLIT MANIFEST",
        "=" * 72,

        (
            "Principal split dataset: "
            f"{HYBRID_INPUT}"
        ),

        (
            "Hybrid input SHA256: "
            f"{_file_sha256(HYBRID_INPUT)}"
        ),

        (
            "Heuristic input SHA256: "
            f"{_file_sha256(HEURISTIC_INPUT)}"
        ),

        (
            "Behavioural input SHA256: "
            f"{_file_sha256(BEHAVIOURAL_INPUT)}"
        ),

        (
            "Selected candidate seed: "
            f"{result.random_seed}"
        ),

        (
            "Metadata balance score: "
            f"{result.score:.8f}"
        ),

        "Target ratio: 70/15/15",
        "Grouping variable: registrable_domain",

        (
            "Candidate split selection used "
            "only size/label/category/source "
            "metadata balance."
        ),

        (
            "No model performance was used "
            "to choose the split."
        ),

        (
            "Final test set must not be used "
            "for preprocessing fitting, feature "
            "selection, hyperparameter tuning, "
            "alpha selection or threshold selection."
        ),
    ]

    MANIFEST_OUTPUT.write_text(
        "\n".join(
            manifest
        ),
        encoding="utf-8",
    )

    print()

    print(
        summary.to_string(
            index=False
        )
    )

    _print_distribution(
        assignments,
        "binary_label",
    )

    _print_distribution(
        assignments,
        "scam_category",
    )

    _print_distribution(
        assignments,
        "source",
    )

    print()

    print(
        "Domain overlap validation: PASSED"
    )

    print()

    print(
        f"Selected seed: "
        f"{result.random_seed}"
    )

    print(
        f"Balance score: "
        f"{result.score:.8f}"
    )

    print()

    print(
        f"Assignments saved to: "
        f"{ASSIGNMENTS_OUTPUT}"
    )

    print(
        f"Summary saved to: "
        f"{SUMMARY_OUTPUT}"
    )

    print(
        f"Manifest saved to: "
        f"{MANIFEST_OUTPUT}"
    )


if __name__ == "__main__":
    main()