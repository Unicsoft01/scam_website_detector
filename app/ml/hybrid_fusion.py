from dataclasses import dataclass

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
class FusionMetrics:
    alpha: float
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


def validate_probability_array(
    probabilities,
    name: str,
) -> np.ndarray:

    values = np.asarray(
        probabilities,
        dtype=float,
    )

    if values.ndim != 1:

        raise ValueError(
            f"{name} must be one-dimensional."
        )

    finite = values[
        np.isfinite(
            values
        )
    ]

    if finite.size:

        if np.any(
            finite < 0.0
        ) or np.any(
            finite > 1.0
        ):

            raise ValueError(
                (
                    f"{name} contains values "
                    "outside [0, 1]."
                )
            )

    return values


def fuse_probabilities(
    heuristic_probability,
    behavioural_probability,
    alpha: float,
) -> np.ndarray:
    """
    Compute:

        P_Hybrid =
        alpha * P_H
        + (1-alpha) * P_B

    Missing values remain missing.
    """

    if not (
        0.0 <= alpha <= 1.0
    ):

        raise ValueError(
            "alpha must be between 0 and 1."
        )

    p_h = validate_probability_array(
        heuristic_probability,
        "heuristic_probability",
    )

    p_b = validate_probability_array(
        behavioural_probability,
        "behavioural_probability",
    )

    if len(
        p_h
    ) != len(
        p_b
    ):

        raise ValueError(
            (
                "Heuristic and behavioural "
                "probability arrays must have "
                "the same length."
            )
        )

    result = np.full(
        len(
            p_h
        ),
        np.nan,
        dtype=float,
    )

    complete_mask = (
        np.isfinite(
            p_h
        )
        &
        np.isfinite(
            p_b
        )
    )

    result[
        complete_mask
    ] = (
        alpha
        * p_h[
            complete_mask
        ]
        +
        (
            1.0
            - alpha
        )
        * p_b[
            complete_mask
        ]
    )

    return result


def classify_probabilities(
    probabilities,
    threshold: float,
) -> np.ndarray:

    if not (
        0.0 <= threshold <= 1.0
    ):

        raise ValueError(
            (
                "Classification threshold "
                "must be between 0 and 1."
            )
        )

    values = validate_probability_array(
        probabilities,
        "probabilities",
    )

    predictions = np.full(
        len(
            values
        ),
        -1,
        dtype=int,
    )

    valid = np.isfinite(
        values
    )

    predictions[
        valid
    ] = (
        values[
            valid
        ]
        >= threshold
    ).astype(int)

    return predictions


def evaluate_fusion(
    y_true,
    hybrid_probability,
    alpha: float,
    threshold: float,
) -> FusionMetrics:

    y = np.asarray(
        y_true,
        dtype=int,
    )

    probabilities = (
        validate_probability_array(
            hybrid_probability,
            "hybrid_probability",
        )
    )

    if len(
        y
    ) != len(
        probabilities
    ):

        raise ValueError(
            (
                "Labels and probabilities "
                "must have equal length."
            )
        )

    valid = np.isfinite(
        probabilities
    )

    if valid.sum() == 0:

        raise ValueError(
            (
                "No complete hybrid "
                "probabilities are available."
            )
        )

    y_valid = y[
        valid
    ]

    p_valid = probabilities[
        valid
    ]

    if set(
        np.unique(
            y_valid
        )
    ) != {
        0,
        1,
    }:

        raise ValueError(
            (
                "Hybrid evaluation requires "
                "both binary classes."
            )
        )

    predictions = (
        p_valid
        >= threshold
    ).astype(int)

    matrix = confusion_matrix(
        y_valid,
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

    try:

        auc = float(
            roc_auc_score(
                y_valid,
                p_valid,
            )
        )

    except ValueError:

        auc = float(
            "nan"
        )

    return FusionMetrics(
        alpha=float(
            alpha
        ),

        threshold=float(
            threshold
        ),

        accuracy=float(
            accuracy_score(
                y_valid,
                predictions,
            )
        ),

        precision=float(
            precision_score(
                y_valid,
                predictions,
                zero_division=0,
            )
        ),

        recall=float(
            recall_score(
                y_valid,
                predictions,
                zero_division=0,
            )
        ),

        f1=float(
            f1_score(
                y_valid,
                predictions,
                zero_division=0,
            )
        ),

        roc_auc=auc,

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
    )


def build_alpha_grid() -> list[float]:

    return [
        round(
            value,
            2,
        )
        for value in np.arange(
            0.0,
            1.0001,
            0.1,
        )
    ]


def build_threshold_grid() -> list[float]:

    return [
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


def calibrate_fusion(
    y_true,
    heuristic_probability,
    behavioural_probability,
    alpha_values=None,
    threshold_values=None,
) -> pd.DataFrame:

    if alpha_values is None:

        alpha_values = (
            build_alpha_grid()
        )

    if threshold_values is None:

        threshold_values = (
            build_threshold_grid()
        )

    rows = []

    for alpha in alpha_values:

        hybrid_probability = (
            fuse_probabilities(
                heuristic_probability,
                behavioural_probability,
                alpha,
            )
        )

        for threshold in threshold_values:

            metrics = evaluate_fusion(
                y_true=y_true,

                hybrid_probability=(
                    hybrid_probability
                ),

                alpha=alpha,

                threshold=threshold,
            )

            rows.append(
                {
                    "alpha":
                        metrics.alpha,

                    "threshold":
                        metrics.threshold,

                    "accuracy":
                        metrics.accuracy,

                    "precision":
                        metrics.precision,

                    "recall":
                        metrics.recall,

                    "f1":
                        metrics.f1,

                    "roc_auc":
                        metrics.roc_auc,

                    "false_positive_rate":
                        metrics.false_positive_rate,

                    "false_negative_rate":
                        metrics.false_negative_rate,

                    "true_negative":
                        metrics.true_negative,

                    "false_positive":
                        metrics.false_positive,

                    "false_negative":
                        metrics.false_negative,

                    "true_positive":
                        metrics.true_positive,
                }
            )

    return pd.DataFrame(
        rows
    )


def choose_best_fusion(
    calibration_results: pd.DataFrame,
) -> pd.Series:
    """
    Primary criterion:
        validation F1

    Tie-breakers:
        1. higher recall
        2. lower FPR
        3. threshold nearer 0.50
        4. alpha nearer 0.50
    """

    if calibration_results.empty:

        raise ValueError(
            "Calibration results are empty."
        )

    required = {
        "alpha",
        "threshold",
        "f1",
        "recall",
        "false_positive_rate",
    }

    missing = (
        required
        - set(
            calibration_results.columns
        )
    )

    if missing:

        raise ValueError(
            (
                "Calibration results are "
                "missing columns: "
                f"{sorted(missing)}"
            )
        )

    dataframe = (
        calibration_results
        .copy()
    )

    dataframe[
        "threshold_distance_from_0_5"
    ] = (
        dataframe[
            "threshold"
        ]
        - 0.50
    ).abs()

    dataframe[
        "alpha_distance_from_0_5"
    ] = (
        dataframe[
            "alpha"
        ]
        - 0.50
    ).abs()

    ordered = (
        dataframe
        .sort_values(
            by=[
                "f1",
                "recall",
                "false_positive_rate",
                "threshold_distance_from_0_5",
                "alpha_distance_from_0_5",
            ],

            ascending=[
                False,
                False,
                True,
                True,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    return ordered.iloc[
        0
    ]


def production_decision(
    heuristic_probability: float,
    behavioural_probability,
    alpha: float,
    threshold: float,
) -> dict:
    """
    Production decision policy.

    Full hybrid output is produced only
    when both evidence channels exist.

    If behavioural evidence is missing,
    return a heuristic fallback status
    rather than silently substituting 0.
    """

    p_h = float(
        heuristic_probability
    )

    if not (
        0.0 <= p_h <= 1.0
    ):

        raise ValueError(
            "P_H must be within [0, 1]."
        )

    behavioural_missing = (
        behavioural_probability is None
    )

    if not behavioural_missing:

        try:

            behavioural_missing = bool(
                np.isnan(
                    behavioural_probability
                )
            )

        except TypeError:

            behavioural_missing = False

    if behavioural_missing:

        return {
            "decision_mode":
                "heuristic_fallback",

            "hybrid_available":
                False,

            "heuristic_probability":
                p_h,

            "behavioural_probability":
                None,

            "hybrid_probability":
                None,

            "predicted_label":
                int(
                    p_h
                    >= threshold
                ),

            "evidence_status":
                (
                    "Behavioural evidence "
                    "unavailable; result is "
                    "not a full hybrid decision."
                ),
        }

    p_b = float(
        behavioural_probability
    )

    if not (
        0.0 <= p_b <= 1.0
    ):

        raise ValueError(
            "P_B must be within [0, 1]."
        )

    fused = float(
        alpha
        * p_h
        +
        (
            1.0
            - alpha
        )
        * p_b
    )

    return {
        "decision_mode":
            "hybrid",

        "hybrid_available":
            True,

        "heuristic_probability":
            p_h,

        "behavioural_probability":
            p_b,

        "hybrid_probability":
            fused,

        "predicted_label":
            int(
                fused
                >= threshold
            ),

        "evidence_status":
            "Complete hybrid evidence.",
    }