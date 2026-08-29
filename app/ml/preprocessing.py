from dataclasses import (
    asdict,
    dataclass,
)
from typing import Optional

import numpy as np
import pandas as pd


TARGET_COLUMN = "binary_label"


NON_FEATURE_COLUMNS = {
    "url",
    "original_url",
    "registrable_domain",
    "source",
    "source_category",
    "binary_label",
    "scam_category",
    "original_label",
    "live_status",
    "audit_timestamp",
}


HIGH_MISSING_THRESHOLD = 0.50

NEAR_CONSTANT_THRESHOLD = 0.99


@dataclass
class FeatureDiagnostic:
    feature: str

    dtype_before: str
    dtype_after: str

    row_count: int

    missing_count: int
    missing_percentage: float

    unique_non_missing: int

    is_constant: bool
    is_near_constant: bool
    is_highly_missing: bool

    dominant_value_percentage: Optional[float]

    infinite_values_replaced: int
    non_numeric_values_coerced: int

    q1: Optional[float]
    q3: Optional[float]
    iqr: Optional[float]

    lower_outlier_bound: Optional[float]
    upper_outlier_bound: Optional[float]

    outlier_count: int
    outlier_percentage: float


def feature_diagnostic_to_dict(
    diagnostic: FeatureDiagnostic,
) -> dict:
    return asdict(
        diagnostic
    )


def get_feature_columns(
    dataframe: pd.DataFrame,
    dataset_type: str,
) -> list[str]:
    """
    Return only columns intended as candidate ML predictors.

    dataset_type:
        heuristic
        behavioural
        hybrid
    """

    dataset_type = (
        dataset_type
        .strip()
        .lower()
    )

    if dataset_type == "heuristic":

        return [
            column
            for column in dataframe.columns
            if column.startswith("h_")
        ]

    if dataset_type == "behavioural":

        return [
            column
            for column in dataframe.columns
            if column.startswith("b_")
        ]

    if dataset_type == "hybrid":

        return [
            column
            for column in dataframe.columns
            if (
                column.startswith("h_")
                or column.startswith("b_")
            )
        ]

    raise ValueError(
        (
            "dataset_type must be "
            "'heuristic', 'behavioural' "
            "or 'hybrid'."
        )
    )


def validate_binary_label(
    dataframe: pd.DataFrame,
) -> None:
    """
    Confirm that the target exists and contains only 0 or 1.
    """

    if TARGET_COLUMN not in dataframe.columns:
        raise ValueError(
            (
                f"Required target column "
                f"'{TARGET_COLUMN}' is missing."
            )
        )

    if dataframe[
        TARGET_COLUMN
    ].isna().any():

        missing_count = int(
            dataframe[
                TARGET_COLUMN
            ]
            .isna()
            .sum()
        )

        raise ValueError(
            (
                "Ground-truth labels contain "
                f"{missing_count} missing values."
            )
        )

    labels = pd.to_numeric(
        dataframe[
            TARGET_COLUMN
        ],
        errors="coerce",
    )

    if labels.isna().any():

        raise ValueError(
            "binary_label contains non-numeric values."
        )

    unique_labels = set(
        labels.astype(int).unique()
    )

    if not unique_labels.issubset(
        {
            0,
            1,
        }
    ):

        raise ValueError(
            (
                "Invalid binary labels found: "
                f"{sorted(unique_labels)}"
            )
        )

    dataframe[
        TARGET_COLUMN
    ] = labels.astype(
        "int8"
    )


def remove_duplicate_urls(
    dataframe: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    int,
]:
    """
    Remove exact duplicate URL records.

    Conflicting labels for the same URL are treated
    as an error rather than silently choosing one.
    """

    if "url" not in dataframe.columns:

        raise ValueError(
            "Dataset does not contain a 'url' column."
        )

    duplicate_mask = dataframe[
        "url"
    ].duplicated(
        keep=False
    )

    duplicates = dataframe[
        duplicate_mask
    ]

    if not duplicates.empty:

        label_counts = (
            duplicates.groupby(
                "url"
            )[
                TARGET_COLUMN
            ]
            .nunique()
        )

        conflicting_urls = (
            label_counts[
                label_counts > 1
            ]
            .index
            .tolist()
        )

        if conflicting_urls:

            raise ValueError(
                (
                    "Duplicate URLs with conflicting "
                    "ground-truth labels found: "
                    f"{conflicting_urls[:10]}"
                )
            )

    before = len(
        dataframe
    )

    dataframe = (
        dataframe
        .drop_duplicates(
            subset=[
                "url"
            ],
            keep="first",
        )
        .copy()
    )

    removed = (
        before
        - len(
            dataframe
        )
    )

    return (
        dataframe,
        removed,
    )


def _convert_feature_to_numeric(
    series: pd.Series,
) -> tuple[
    pd.Series,
    int,
    int,
]:
    """
    Convert a feature column to numeric form.

    Returns:
        cleaned_series,
        infinite_values_replaced,
        non_numeric_values_coerced
    """

    original_missing = (
        series.isna()
    )

    # Pandas BooleanDtype / Python booleans
    # become 1 and 0.
    if (
        pd.api.types.is_bool_dtype(
            series
        )
    ):
        numeric = series.astype(
            "Int8"
        )

    else:
        numeric = pd.to_numeric(
            series,
            errors="coerce",
        )

    newly_missing = (
        numeric.isna()
        & ~original_missing
    )

    non_numeric_values_coerced = int(
        newly_missing.sum()
    )

    numeric = numeric.astype(
        "float64"
    )

    infinite_mask = np.isinf(
        numeric.to_numpy(
            dtype=float,
            na_value=np.nan,
        )
    )

    infinite_values_replaced = int(
        infinite_mask.sum()
    )

    numeric = numeric.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    return (
        numeric,
        infinite_values_replaced,
        non_numeric_values_coerced,
    )


def _dominant_value_percentage(
    series: pd.Series,
) -> Optional[float]:

    non_missing = (
        series.dropna()
    )

    if non_missing.empty:
        return None

    counts = (
        non_missing
        .value_counts(
            normalize=True
        )
    )

    if counts.empty:
        return None

    return float(
        counts.iloc[0]
    )


def _outlier_statistics(
    series: pd.Series,
) -> dict:
    """
    Diagnostic only.

    Outliers are identified using the 1.5 × IQR rule.
    Values are NOT clipped or deleted in Phase 15.
    """

    values = (
        series
        .dropna()
        .astype(float)
    )

    if len(values) < 4:

        return {
            "q1": None,
            "q3": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
            "outlier_percentage": 0.0,
        }

    q1 = float(
        values.quantile(
            0.25
        )
    )

    q3 = float(
        values.quantile(
            0.75
        )
    )

    iqr = (
        q3
        - q1
    )

    lower = (
        q1
        - 1.5
        * iqr
    )

    upper = (
        q3
        + 1.5
        * iqr
    )

    outlier_mask = (
        (values < lower)
        | (values > upper)
    )

    outlier_count = int(
        outlier_mask.sum()
    )

    outlier_percentage = (
        outlier_count
        / len(values)
        * 100
    )

    return {
        "q1": q1,
        "q3": q3,
        "iqr": float(
            iqr
        ),
        "lower_bound": float(
            lower
        ),
        "upper_bound": float(
            upper
        ),
        "outlier_count":
            outlier_count,
        "outlier_percentage":
            float(
                outlier_percentage
            ),
    }


def clean_feature_column(
    dataframe: pd.DataFrame,
    feature: str,
) -> FeatureDiagnostic:
    """
    Convert one candidate predictor to numeric form
    and generate diagnostics.
    """

    dtype_before = str(
        dataframe[
            feature
        ].dtype
    )

    (
        cleaned,
        infinite_replaced,
        non_numeric_coerced,
    ) = _convert_feature_to_numeric(
        dataframe[
            feature
        ]
    )

    dataframe[
        feature
    ] = cleaned

    dtype_after = str(
        dataframe[
            feature
        ].dtype
    )

    row_count = len(
        dataframe
    )

    missing_count = int(
        cleaned.isna().sum()
    )

    if row_count:

        missing_percentage = (
            missing_count
            / row_count
            * 100
        )

    else:

        missing_percentage = 0.0

    unique_non_missing = int(
        cleaned.nunique(
            dropna=True
        )
    )

    is_constant = (
        unique_non_missing <= 1
    )

    dominant_ratio = (
        _dominant_value_percentage(
            cleaned
        )
    )

    is_near_constant = bool(
        dominant_ratio is not None
        and dominant_ratio
        >= NEAR_CONSTANT_THRESHOLD
    )

    missing_ratio = (
        missing_count
        / row_count
        if row_count
        else 0.0
    )

    is_highly_missing = bool(
        missing_ratio
        >= HIGH_MISSING_THRESHOLD
    )

    outliers = (
        _outlier_statistics(
            cleaned
        )
    )

    return FeatureDiagnostic(
        feature=feature,

        dtype_before=(
            dtype_before
        ),

        dtype_after=(
            dtype_after
        ),

        row_count=(
            row_count
        ),

        missing_count=(
            missing_count
        ),

        missing_percentage=round(
            missing_percentage,
            4,
        ),

        unique_non_missing=(
            unique_non_missing
        ),

        is_constant=(
            is_constant
        ),

        is_near_constant=(
            is_near_constant
        ),

        is_highly_missing=(
            is_highly_missing
        ),

        dominant_value_percentage=(
            round(
                dominant_ratio
                * 100,
                4,
            )
            if dominant_ratio
            is not None
            else None
        ),

        infinite_values_replaced=(
            infinite_replaced
        ),

        non_numeric_values_coerced=(
            non_numeric_coerced
        ),

        q1=outliers[
            "q1"
        ],

        q3=outliers[
            "q3"
        ],

        iqr=outliers[
            "iqr"
        ],

        lower_outlier_bound=(
            outliers[
                "lower_bound"
            ]
        ),

        upper_outlier_bound=(
            outliers[
                "upper_bound"
            ]
        ),

        outlier_count=(
            outliers[
                "outlier_count"
            ]
        ),

        outlier_percentage=round(
            outliers[
                "outlier_percentage"
            ],
            4,
        ),
    )