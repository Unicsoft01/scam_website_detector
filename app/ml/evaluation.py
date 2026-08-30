from dataclasses import dataclass
import time

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class EvaluationMetrics:
    configuration: str
    threshold: float

    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

    false_positive_rate: float
    false_negative_rate: float

    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int

    sample_count: int


def validate_binary_labels(
    labels,
) -> np.ndarray:

    y = np.asarray(
        labels,
        dtype=int,
    )

    if y.ndim != 1:

        raise ValueError(
            "Labels must be one-dimensional."
        )

    unique = set(
        np.unique(
            y
        )
    )

    if unique != {
        0,
        1,
    }:

        raise ValueError(
            (
                "Evaluation requires both "
                "binary classes 0 and 1. "
                f"Found: {sorted(unique)}"
            )
        )

    return y


def validate_probabilities(
    probabilities,
    name: str = "probabilities",
) -> np.ndarray:

    values = np.asarray(
        probabilities,
        dtype=float,
    )

    if values.ndim != 1:

        raise ValueError(
            (
                f"{name} must be "
                "one-dimensional."
            )
        )

    if not np.all(
        np.isfinite(
            values
        )
    ):

        raise ValueError(
            f"{name} contains missing values."
        )

    if np.any(
        values < 0.0
    ) or np.any(
        values > 1.0
    ):

        raise ValueError(
            (
                f"{name} contains values "
                "outside [0, 1]."
            )
        )

    return values


def predictions_from_threshold(
    probabilities,
    threshold: float,
) -> np.ndarray:

    if not (
        0.0 <= threshold <= 1.0
    ):

        raise ValueError(
            (
                "Threshold must be between "
                "0 and 1."
            )
        )

    probabilities = (
        validate_probabilities(
            probabilities
        )
    )

    return (
        probabilities
        >= threshold
    ).astype(int)


def evaluate_configuration(
    configuration: str,
    y_true,
    probabilities,
    threshold: float,
) -> EvaluationMetrics:

    y = validate_binary_labels(
        y_true
    )

    p = validate_probabilities(
        probabilities
    )

    if len(
        y
    ) != len(
        p
    ):

        raise ValueError(
            (
                "Labels and probabilities "
                "must contain the same "
                "number of observations."
            )
        )

    predictions = (
        predictions_from_threshold(
            p,
            threshold,
        )
    )

    matrix = confusion_matrix(
        y,
        predictions,
        labels=[
            0,
            1,
        ],
    )

    (
        true_negative,
        false_positive,
        false_negative,
        true_positive,
    ) = matrix.ravel()

    negative_total = (
        true_negative
        + false_positive
    )

    positive_total = (
        true_positive
        + false_negative
    )

    false_positive_rate = (
        false_positive
        / negative_total
        if negative_total
        else 0.0
    )

    false_negative_rate = (
        false_negative
        / positive_total
        if positive_total
        else 0.0
    )

    return EvaluationMetrics(
        configuration=configuration,

        threshold=float(
            threshold
        ),

        accuracy=float(
            accuracy_score(
                y,
                predictions,
            )
        ),

        precision=float(
            precision_score(
                y,
                predictions,
                zero_division=0,
            )
        ),

        recall=float(
            recall_score(
                y,
                predictions,
                zero_division=0,
            )
        ),

        f1=float(
            f1_score(
                y,
                predictions,
                zero_division=0,
            )
        ),

        roc_auc=float(
            roc_auc_score(
                y,
                p,
            )
        ),

        false_positive_rate=float(
            false_positive_rate
        ),

        false_negative_rate=float(
            false_negative_rate
        ),

        true_negative=int(
            true_negative
        ),

        false_positive=int(
            false_positive
        ),

        false_negative=int(
            false_negative
        ),

        true_positive=int(
            true_positive
        ),

        sample_count=int(
            len(
                y
            )
        ),
    )


def calibrate_single_model_threshold(
    y_true,
    probabilities,
    threshold_values=None,
) -> pd.DataFrame:
    """
    Validation-only baseline threshold
    calibration for RF-H or RF-B.
    """

    y = validate_binary_labels(
        y_true
    )

    p = validate_probabilities(
        probabilities
    )

    if threshold_values is None:

        threshold_values = [
            round(
                value,
                2,
            )
            for value in np.arange(
                0.30,
                0.7001,
                0.05,
            )
        ]

    rows = []

    for threshold in threshold_values:

        result = (
            evaluate_configuration(
                configuration="validation",
                y_true=y,
                probabilities=p,
                threshold=threshold,
            )
        )

        rows.append(
            {
                "threshold":
                    threshold,

                "accuracy":
                    result.accuracy,

                "precision":
                    result.precision,

                "recall":
                    result.recall,

                "f1":
                    result.f1,

                "roc_auc":
                    result.roc_auc,

                "false_positive_rate":
                    result.false_positive_rate,

                "false_negative_rate":
                    result.false_negative_rate,
            }
        )

    return pd.DataFrame(
        rows
    )


def choose_baseline_threshold(
    calibration: pd.DataFrame,
) -> float:
    """
    Primary:
      F1

    Tie-breakers:
      recall
      lower FPR
      threshold nearest 0.50
    """

    if calibration.empty:

        raise ValueError(
            "Calibration table is empty."
        )

    data = calibration.copy()

    data[
        "distance_from_0_5"
    ] = (
        data[
            "threshold"
        ]
        - 0.50
    ).abs()

    data = (
        data
        .sort_values(
            by=[
                "f1",
                "recall",
                "false_positive_rate",
                "distance_from_0_5",
            ],
            ascending=[
                False,
                False,
                True,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    return float(
        data.iloc[
            0
        ][
            "threshold"
        ]
    )


def category_recall_table(
    labels,
    predictions,
    categories,
    configuration: str,
) -> pd.DataFrame:

    dataframe = pd.DataFrame(
        {
            "binary_label":
                np.asarray(
                    labels,
                    dtype=int,
                ),

            "prediction":
                np.asarray(
                    predictions,
                    dtype=int,
                ),

            "scam_category":
                np.asarray(
                    categories,
                    dtype=object,
                ),
        }
    )

    # Only positive/scam observations
    # belong in scam-category recall.
    dataframe = dataframe[
        dataframe[
            "binary_label"
        ] == 1
    ].copy()

    rows = []

    desired_categories = [
        "phishing",
        "online_shopping",
        "cryptocurrency",
        "investment",
        "technical_support",
    ]

    for category in desired_categories:

        subset = dataframe[
            dataframe[
                "scam_category"
            ] == category
        ]

        support = int(
            len(
                subset
            )
        )

        if support == 0:

            recall = np.nan

            true_positive = 0

            false_negative = 0

        else:

            true_positive = int(
                (
                    subset[
                        "prediction"
                    ]
                    == 1
                ).sum()
            )

            false_negative = int(
                (
                    subset[
                        "prediction"
                    ]
                    == 0
                ).sum()
            )

            recall = (
                true_positive
                / support
            )

        rows.append(
            {
                "configuration":
                    configuration,

                "scam_category":
                    category,

                "support":
                    support,

                "true_positive":
                    true_positive,

                "false_negative":
                    false_negative,

                "recall":
                    recall,
            }
        )

    return pd.DataFrame(
        rows
    )


def time_callable_per_record_ms(
    function,
    number_of_records: int,
    repeats: int = 10,
) -> dict:

    if number_of_records < 1:

        raise ValueError(
            (
                "number_of_records must "
                "be at least 1."
            )
        )

    if repeats < 1:

        raise ValueError(
            "repeats must be at least 1."
        )

    # One warm-up execution.
    function()

    per_record_times = []

    for _ in range(
        repeats
    ):

        start = time.perf_counter()

        function()

        elapsed_seconds = (
            time.perf_counter()
            - start
        )

        elapsed_ms = (
            elapsed_seconds
            * 1000.0
        )

        per_record_ms = (
            elapsed_ms
            / number_of_records
        )

        per_record_times.append(
            per_record_ms
        )

    return {
        "mean_ms_per_record":
            float(
                np.mean(
                    per_record_times
                )
            ),

        "median_ms_per_record":
            float(
                np.median(
                    per_record_times
                )
            ),

        "min_ms_per_record":
            float(
                np.min(
                    per_record_times
                )
            ),

        "max_ms_per_record":
            float(
                np.max(
                    per_record_times
                )
            ),

        "std_ms_per_record":
            float(
                np.std(
                    per_record_times
                )
            ),

        "repeats":
            int(
                repeats
            ),
    }