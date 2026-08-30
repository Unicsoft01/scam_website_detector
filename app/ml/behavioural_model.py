from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
)

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


RANDOM_STATE = 42


@dataclass
class BehaviouralValidationResult:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int


def prepare_selected_features(
    dataframe: pd.DataFrame,
    selected_features: list[str],
    training_medians: dict[str, float],
) -> pd.DataFrame:
    """
    Prepare RF-B input using preprocessing
    values learned from training only.
    """

    missing_columns = [
        feature
        for feature in selected_features
        if feature not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(
            (
                "Required RF-B features are "
                "missing from the dataset: "
                f"{missing_columns}"
            )
        )

    x = dataframe[
        selected_features
    ].copy()

    for feature in selected_features:

        x[feature] = pd.to_numeric(
            x[feature],
            errors="coerce",
        )

        x[feature] = x[
            feature
        ].replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        if feature not in training_medians:

            raise ValueError(
                (
                    "No saved training median "
                    "exists for behavioural "
                    f"feature: {feature}"
                )
            )

        median = float(
            training_medians[
                feature
            ]
        )

        x[feature] = x[
            feature
        ].fillna(
            median
        )

    if x.isna().any().any():

        raise ValueError(
            (
                "RF-B feature matrix still "
                "contains missing values."
            )
        )

    return x


def validate_training_labels(
    labels: pd.Series,
) -> pd.Series:

    y = pd.to_numeric(
        labels,
        errors="raise",
    ).astype(int)

    unique = set(
        y.unique()
    )

    if unique != {
        0,
        1,
    }:

        raise ValueError(
            (
                "RF-B training requires both "
                "classes 0 and 1. "
                f"Found: {sorted(unique)}"
            )
        )

    return y


def build_random_forest(
    **parameters: Any,
) -> RandomForestClassifier:

    defaults = {
        "n_estimators": 300,
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "max_features": "sqrt",
        "class_weight": "balanced",
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
    }

    defaults.update(
        parameters
    )

    return RandomForestClassifier(
        **defaults
    )


def scam_probability(
    model: RandomForestClassifier,
    x: pd.DataFrame,
) -> np.ndarray:
    """
    Return P_B = P(y=1 | X_B).
    """

    if not hasattr(
        model,
        "classes_",
    ):

        raise ValueError(
            "RF-B model has not been fitted."
        )

    classes = list(
        model.classes_
    )

    if 1 not in classes:

        raise ValueError(
            (
                "Fitted RF-B model does not "
                "contain scam class 1."
            )
        )

    scam_index = classes.index(
        1
    )

    probabilities = (
        model.predict_proba(
            x
        )[
            :,
            scam_index
        ]
    )

    return probabilities.astype(
        float
    )


def evaluate_validation(
    y_true: pd.Series,
    scam_probabilities: np.ndarray,
    threshold: float = 0.50,
) -> BehaviouralValidationResult:

    if not (
        0.0
        <= threshold
        <= 1.0
    ):

        raise ValueError(
            (
                "Classification threshold "
                "must be between 0 and 1."
            )
        )

    predictions = (
        scam_probabilities
        >= threshold
    ).astype(int)

    matrix = confusion_matrix(
        y_true,
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

    try:

        auc = float(
            roc_auc_score(
                y_true,
                scam_probabilities,
            )
        )

    except ValueError:

        auc = float(
            "nan"
        )

    return BehaviouralValidationResult(
        accuracy=float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),

        precision=float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        recall=float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        f1=float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),

        roc_auc=auc,

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


def feature_importance_table(
    model: RandomForestClassifier,
    feature_names: list[str],
) -> pd.DataFrame:

    if not hasattr(
        model,
        "feature_importances_",
    ):

        raise ValueError(
            "RF-B model has not been fitted."
        )

    if len(
        model.feature_importances_
    ) != len(
        feature_names
    ):

        raise ValueError(
            (
                "Feature-importance length "
                "does not match feature names."
            )
        )

    dataframe = pd.DataFrame(
        {
            "feature":
                feature_names,

            "importance":
                model.feature_importances_,
        }
    )

    dataframe = (
        dataframe
        .sort_values(
            by=[
                "importance",
                "feature",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    dataframe[
        "rank"
    ] = (
        dataframe.index
        + 1
    )

    return dataframe[
        [
            "rank",
            "feature",
            "importance",
        ]
    ]