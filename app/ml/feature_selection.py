from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


RANDOM_STATE = 42


@dataclass
class PreparedFeatureData:
    x_train: pd.DataFrame
    x_validation: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    medians: dict[str, float]
    excluded_all_missing: list[str]


@dataclass
class CandidateResult:
    feature_count: int
    selected_features: list[str]

    validation_accuracy: float
    validation_precision: float
    validation_recall: float
    validation_f1: float


def get_feature_columns(
    dataframe: pd.DataFrame,
    feature_type: str,
) -> list[str]:

    feature_type = (
        feature_type
        .strip()
        .lower()
    )

    if feature_type == "heuristic":

        prefix = "h_"

    elif feature_type == "behavioural":

        prefix = "b_"

    else:

        raise ValueError(
            (
                "feature_type must be "
                "'heuristic' or 'behavioural'."
            )
        )

    return [
        column
        for column in dataframe.columns
        if column.startswith(prefix)
    ]


def validate_feature_selection_input(
    dataframe: pd.DataFrame,
    feature_type: str,
) -> None:

    if dataframe.empty:

        raise ValueError(
            "Feature-selection dataset is empty."
        )

    if "binary_label" not in dataframe.columns:

        raise ValueError(
            "binary_label column is missing."
        )

    if dataframe[
        "binary_label"
    ].isna().any():

        raise ValueError(
            "binary_label contains missing values."
        )

    labels = set(
        pd.to_numeric(
            dataframe[
                "binary_label"
            ],
            errors="raise",
        )
        .astype(int)
        .unique()
    )

    if labels != {
        0,
        1,
    }:

        raise ValueError(
            (
                "Feature selection requires "
                "both binary classes 0 and 1. "
                f"Found: {sorted(labels)}"
            )
        )

    features = get_feature_columns(
        dataframe,
        feature_type,
    )

    if not features:

        raise ValueError(
            (
                f"No {feature_type} feature "
                "columns were found."
            )
        )


def prepare_train_validation_features(
    training: pd.DataFrame,
    validation: pd.DataFrame,
    feature_type: str,
) -> PreparedFeatureData:

    validate_feature_selection_input(
        training,
        feature_type,
    )

    validate_feature_selection_input(
        validation,
        feature_type,
    )

    train_features = get_feature_columns(
        training,
        feature_type,
    )

    validation_features = get_feature_columns(
        validation,
        feature_type,
    )

    if set(
        train_features
    ) != set(
        validation_features
    ):

        raise ValueError(
            (
                "Training and validation "
                "feature schemas do not match."
            )
        )

    features = sorted(
        train_features
    )

    x_train = training[
        features
    ].copy()

    x_validation = validation[
        features
    ].copy()

    y_train = pd.to_numeric(
        training[
            "binary_label"
        ],
        errors="raise",
    ).astype(int)

    y_validation = pd.to_numeric(
        validation[
            "binary_label"
        ],
        errors="raise",
    ).astype(int)

    medians = {}

    excluded_all_missing = []

    retained_features = []

    for feature in features:

        x_train[
            feature
        ] = pd.to_numeric(
            x_train[
                feature
            ],
            errors="coerce",
        )

        x_validation[
            feature
        ] = pd.to_numeric(
            x_validation[
                feature
            ],
            errors="coerce",
        )

        x_train[
            feature
        ] = x_train[
            feature
        ].replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        x_validation[
            feature
        ] = x_validation[
            feature
        ].replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        if x_train[
            feature
        ].notna().sum() == 0:

            excluded_all_missing.append(
                feature
            )

            continue

        median = float(
            x_train[
                feature
            ].median()
        )

        medians[
            feature
        ] = median

        x_train[
            feature
        ] = x_train[
            feature
        ].fillna(
            median
        )

        x_validation[
            feature
        ] = x_validation[
            feature
        ].fillna(
            median
        )

        retained_features.append(
            feature
        )

    if not retained_features:

        raise ValueError(
            (
                "No usable predictor features "
                "remain after preprocessing."
            )
        )

    x_train = x_train[
        retained_features
    ]

    x_validation = x_validation[
        retained_features
    ]

    return PreparedFeatureData(
        x_train=x_train,

        x_validation=x_validation,

        y_train=y_train,

        y_validation=y_validation,

        medians=medians,

        excluded_all_missing=(
            excluded_all_missing
        ),
    )


def calculate_mi_ranking(
    x_train: pd.DataFrame,
    y_train: pd.Series,
) -> pd.DataFrame:

    if x_train.empty:

        raise ValueError(
            "Training feature matrix is empty."
        )

    if x_train.isna().any().any():

        raise ValueError(
            (
                "Training features still contain "
                "missing values before MI."
            )
        )

    scores = mutual_info_classif(
        x_train,
        y_train,
        random_state=RANDOM_STATE,
    )

    ranking = pd.DataFrame(
        {
            "feature":
                x_train.columns,

            "mutual_information":
                scores,
        }
    )

    ranking = (
        ranking
        .sort_values(
            by=[
                "mutual_information",
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

    ranking[
        "rank"
    ] = (
        ranking.index
        + 1
    )

    ranking[
        "selected_candidate"
    ] = False

    return ranking[
        [
            "rank",
            "feature",
            "mutual_information",
            "selected_candidate",
        ]
    ]


def build_candidate_counts(
    number_of_features: int,
) -> list[int]:

    if number_of_features < 1:

        raise ValueError(
            (
                "number_of_features must "
                "be at least 1."
            )
        )

    # For very small feature spaces,
    # test each possible size.
    if number_of_features <= 10:

        return list(
            range(
                1,
                number_of_features + 1,
            )
        )

    candidates = {
        5,
        10,
        15,
        20,
        25,
        30,
        40,
        50,
        number_of_features,
    }

    candidates = {
        value
        for value in candidates
        if (
            value >= 1
            and value
            <= number_of_features
        )
    }

    return sorted(
        candidates
    )


def evaluate_candidate_feature_count(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_validation: pd.DataFrame,
    y_validation: pd.Series,
    ranked_features: list[str],
    feature_count: int,
) -> CandidateResult:

    if feature_count < 1:

        raise ValueError(
            "feature_count must be at least 1."
        )

    if feature_count > len(
        ranked_features
    ):

        raise ValueError(
            (
                "feature_count is larger than "
                "the ranked feature list."
            )
        )

    selected = ranked_features[
        :feature_count
    ]

    # This is a fixed development evaluator,
    # not the final tuned RF-H or RF-B model.
    model = RandomForestClassifier(
        n_estimators=200,

        random_state=RANDOM_STATE,

        class_weight="balanced",

        n_jobs=-1,
    )

    model.fit(
        x_train[
            selected
        ],
        y_train,
    )

    predictions = model.predict(
        x_validation[
            selected
        ]
    )

    return CandidateResult(
        feature_count=(
            feature_count
        ),

        selected_features=(
            selected
        ),

        validation_accuracy=float(
            accuracy_score(
                y_validation,
                predictions,
            )
        ),

        validation_precision=float(
            precision_score(
                y_validation,
                predictions,
                zero_division=0,
            )
        ),

        validation_recall=float(
            recall_score(
                y_validation,
                predictions,
                zero_division=0,
            )
        ),

        validation_f1=float(
            f1_score(
                y_validation,
                predictions,
                zero_division=0,
            )
        ),
    )


def evaluate_candidate_counts(
    prepared: PreparedFeatureData,
    ranking: pd.DataFrame,
) -> pd.DataFrame:

    ranked_features = (
        ranking[
            "feature"
        ]
        .tolist()
    )

    candidate_counts = (
        build_candidate_counts(
            len(
                ranked_features
            )
        )
    )

    rows = []

    for count in candidate_counts:

        result = (
            evaluate_candidate_feature_count(
                x_train=(
                    prepared.x_train
                ),

                y_train=(
                    prepared.y_train
                ),

                x_validation=(
                    prepared.x_validation
                ),

                y_validation=(
                    prepared.y_validation
                ),

                ranked_features=(
                    ranked_features
                ),

                feature_count=(
                    count
                ),
            )
        )

        rows.append(
            {
                "feature_count":
                    result.feature_count,

                "validation_accuracy":
                    result.validation_accuracy,

                "validation_precision":
                    result.validation_precision,

                "validation_recall":
                    result.validation_recall,

                "validation_f1":
                    result.validation_f1,
            }
        )

    return pd.DataFrame(
        rows
    )


def choose_best_candidate(
    candidate_results: pd.DataFrame,
) -> int:
    """
    Primary criterion: validation F1.

    Tie-breakers:
    1. validation recall
    2. fewer features
    """

    required = {
        "feature_count",
        "validation_f1",
        "validation_recall",
    }

    missing = (
        required
        - set(
            candidate_results.columns
        )
    )

    if missing:

        raise ValueError(
            (
                "Candidate result columns "
                f"missing: {sorted(missing)}"
            )
        )

    if candidate_results.empty:

        raise ValueError(
            "No candidate results exist."
        )

    ordered = (
        candidate_results
        .sort_values(
            by=[
                "validation_f1",
                "validation_recall",
                "feature_count",
            ],

            ascending=[
                False,
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    return int(
        ordered.iloc[
            0
        ][
            "feature_count"
        ]
    )