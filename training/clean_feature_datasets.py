from pathlib import Path

import pandas as pd

from app.ml.preprocessing import (
    clean_feature_column,
    feature_diagnostic_to_dict,
    get_feature_columns,
    remove_duplicate_urls,
    validate_binary_label,
)


DATASETS = {
    "heuristic": {
        "input": Path(
            "data/processed/"
            "heuristic_dataset.csv"
        ),

        "output": Path(
            "data/processed/cleaned/"
            "heuristic_cleaned.csv"
        ),

        "report": Path(
            "data/interim/"
            "preprocessing/"
            "heuristic_feature_report.csv"
        ),

        "log": Path(
            "data/interim/"
            "preprocessing/"
            "heuristic_cleaning_log.csv"
        ),
    },

    "behavioural": {
        "input": Path(
            "data/processed/"
            "behavioural_dataset.csv"
        ),

        "output": Path(
            "data/processed/cleaned/"
            "behavioural_cleaned.csv"
        ),

        "report": Path(
            "data/interim/"
            "preprocessing/"
            "behavioural_feature_report.csv"
        ),

        "log": Path(
            "data/interim/"
            "preprocessing/"
            "behavioural_cleaning_log.csv"
        ),
    },

    "hybrid": {
        "input": Path(
            "data/processed/"
            "hybrid_dataset.csv"
        ),

        "output": Path(
            "data/processed/cleaned/"
            "hybrid_cleaned.csv"
        ),

        "report": Path(
            "data/interim/"
            "preprocessing/"
            "hybrid_feature_report.csv"
        ),

        "log": Path(
            "data/interim/"
            "preprocessing/"
            "hybrid_cleaning_log.csv"
        ),
    },
}


def _ensure_parent(
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def process_dataset(
    dataset_type: str,
    configuration: dict,
) -> None:

    input_path = (
        configuration[
            "input"
        ]
    )

    output_path = (
        configuration[
            "output"
        ]
    )

    report_path = (
        configuration[
            "report"
        ]
    )

    log_path = (
        configuration[
            "log"
        ]
    )

    print()

    print(
        "=" * 72
    )

    print(
        f"{dataset_type.upper()} DATASET"
    )

    print(
        "=" * 72
    )

    if not input_path.exists():

        print(
            "SKIPPED — input file "
            f"does not exist: "
            f"{input_path}"
        )

        return

    try:
        dataframe = pd.read_csv(
            input_path
        )

    except pd.errors.EmptyDataError:

        print(
            "SKIPPED — input file "
            "is empty."
        )

        return

    if dataframe.empty:

        print(
            "SKIPPED — dataset "
            "contains no rows."
        )

        return

    original_rows = len(
        dataframe
    )

    original_columns = len(
        dataframe.columns
    )

    # -----------------------------------------
    # LABEL VALIDATION
    # -----------------------------------------

    validate_binary_label(
        dataframe
    )

    # -----------------------------------------
    # URL DUPLICATES
    # -----------------------------------------

    (
        dataframe,
        duplicate_urls_removed,
    ) = remove_duplicate_urls(
        dataframe
    )

    # -----------------------------------------
    # FEATURE SELECTION BY PREFIX
    # -----------------------------------------

    features = get_feature_columns(
        dataframe,
        dataset_type,
    )

    if not features:

        raise ValueError(
            (
                f"No candidate feature columns "
                f"found for {dataset_type}."
            )
        )

    # -----------------------------------------
    # DUPLICATED COMPLETE FEATURE RECORDS
    # -----------------------------------------

    duplicate_feature_rows = int(
        dataframe[
            features
        ]
        .duplicated(
            keep=False
        )
        .sum()
    )

    # Important:
    # We report these but DO NOT automatically
    # delete them. Different URLs can genuinely
    # have identical feature vectors.

    # -----------------------------------------
    # FEATURE CLEANING AND DIAGNOSTICS
    # -----------------------------------------

    diagnostics = []

    for feature in features:

        diagnostic = (
            clean_feature_column(
                dataframe,
                feature,
            )
        )

        diagnostics.append(
            feature_diagnostic_to_dict(
                diagnostic
            )
        )

    report = pd.DataFrame(
        diagnostics
    )

    # -----------------------------------------
    # DATASET-WIDE COUNTS
    # -----------------------------------------

    constant_count = int(
        report[
            "is_constant"
        ].sum()
    )

    near_constant_count = int(
        report[
            "is_near_constant"
        ].sum()
    )

    highly_missing_count = int(
        report[
            "is_highly_missing"
        ].sum()
    )

    total_infinite_replaced = int(
        report[
            "infinite_values_replaced"
        ].sum()
    )

    total_non_numeric_coerced = int(
        report[
            "non_numeric_values_coerced"
        ].sum()
    )

    # -----------------------------------------
    # SAVE CLEANED DATASET
    # -----------------------------------------

    _ensure_parent(
        output_path
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )

    # -----------------------------------------
    # SAVE FEATURE REPORT
    # -----------------------------------------

    _ensure_parent(
        report_path
    )

    report.to_csv(
        report_path,
        index=False,
    )

    # -----------------------------------------
    # SAVE CLEANING LOG
    # -----------------------------------------

    cleaning_log = pd.DataFrame(
        [
            {
                "dataset":
                    dataset_type,

                "input_rows":
                    original_rows,

                "output_rows":
                    len(
                        dataframe
                    ),

                "input_columns":
                    original_columns,

                "output_columns":
                    len(
                        dataframe.columns
                    ),

                "candidate_features":
                    len(
                        features
                    ),

                "duplicate_urls_removed":
                    duplicate_urls_removed,

                "duplicate_feature_rows":
                    duplicate_feature_rows,

                "constant_features":
                    constant_count,

                "near_constant_features":
                    near_constant_count,

                "highly_missing_features":
                    highly_missing_count,

                "infinite_values_replaced":
                    total_infinite_replaced,

                "non_numeric_values_coerced":
                    total_non_numeric_coerced,

                "rows_with_missing_features":
                    int(
                        dataframe[
                            features
                        ]
                        .isna()
                        .any(
                            axis=1
                        )
                        .sum()
                    ),
            }
        ]
    )

    _ensure_parent(
        log_path
    )

    cleaning_log.to_csv(
        log_path,
        index=False,
    )

    print(
        f"Input rows: "
        f"{original_rows}"
    )

    print(
        f"Output rows: "
        f"{len(dataframe)}"
    )

    print(
        f"Candidate features: "
        f"{len(features)}"
    )

    print(
        "Duplicate URLs removed: "
        f"{duplicate_urls_removed}"
    )

    print(
        "Duplicate feature rows "
        "(reported, not removed): "
        f"{duplicate_feature_rows}"
    )

    print(
        "Constant features: "
        f"{constant_count}"
    )

    print(
        "Near-constant features: "
        f"{near_constant_count}"
    )

    print(
        "Highly missing features: "
        f"{highly_missing_count}"
    )

    print(
        "Infinite values replaced: "
        f"{total_infinite_replaced}"
    )

    print(
        "Non-numeric feature values "
        "converted to missing: "
        f"{total_non_numeric_coerced}"
    )

    print()

    print(
        f"Cleaned dataset: "
        f"{output_path}"
    )

    print(
        f"Feature report: "
        f"{report_path}"
    )

    print(
        f"Cleaning log: "
        f"{log_path}"
    )


def main():

    print(
        "\nPHASE 15 — DATA CLEANING "
        "AND PREPROCESSING"
    )

    for (
        dataset_type,
        configuration,
    ) in DATASETS.items():

        process_dataset(
            dataset_type,
            configuration,
        )


if __name__ == "__main__":
    main()