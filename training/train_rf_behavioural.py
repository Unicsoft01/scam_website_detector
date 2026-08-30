import json
from hashlib import sha256
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
)

from sklearn.metrics import (
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
)

from sklearn.model_selection import (
    GridSearchCV,
    StratifiedGroupKFold,
)

from app.ml.behavioural_model import (
    RANDOM_STATE,
    evaluate_validation,
    feature_importance_table,
    prepare_selected_features,
    scam_probability,
    validate_training_labels,
)


TRAINING_INPUT = Path(
    "data/splits/behavioural/"
    "training.csv"
)

VALIDATION_INPUT = Path(
    "data/splits/behavioural/"
    "validation.csv"
)

SELECTED_FEATURES_INPUT = Path(
    "data/processed/"
    "feature_selection/"
    "behavioural_selected_features.json"
)


MODEL_OUTPUT = Path(
    "models/"
    "rf_behavioural.joblib"
)

OUTPUT_ROOT = Path(
    "data/processed/"
    "model_training"
)

TUNING_OUTPUT = (
    OUTPUT_ROOT
    / "behavioural_tuning_results.csv"
)

IMPORTANCE_OUTPUT = (
    OUTPUT_ROOT
    / "behavioural_feature_importance.csv"
)

VALIDATION_PREDICTIONS_OUTPUT = (
    OUTPUT_ROOT
    / "behavioural_validation_predictions.csv"
)

VALIDATION_METRICS_OUTPUT = (
    OUTPUT_ROOT
    / "behavioural_validation_metrics.json"
)

MANIFEST_OUTPUT = (
    OUTPUT_ROOT
    / "behavioural_training_manifest.txt"
)


# Keep the same RF family and the same
# principal search space used for RF-H.
PARAMETER_GRID = {
    "n_estimators": [
        200,
        400,
    ],

    "max_depth": [
        None,
        10,
        20,
    ],

    "min_samples_split": [
        2,
        5,
    ],

    "min_samples_leaf": [
        1,
        2,
    ],

    "max_features": [
        "sqrt",
    ],

    "class_weight": [
        "balanced",
        "balanced_subsample",
    ],
}


def _read_csv(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(
            (
                "Required input file does not "
                f"exist: {path}"
            )
        )

    try:

        dataframe = pd.read_csv(
            path
        )

    except pd.errors.EmptyDataError:

        raise ValueError(
            f"Input dataset is empty: {path}"
        )

    if dataframe.empty:

        raise ValueError(
            (
                "Input dataset contains no rows: "
                f"{path}"
            )
        )

    return dataframe


def _sha256(
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


def _read_feature_selection() -> dict:

    if not SELECTED_FEATURES_INPUT.exists():

        raise FileNotFoundError(
            (
                "Phase 17 behavioural "
                "selected-feature file "
                "does not exist: "
                f"{SELECTED_FEATURES_INPUT}"
            )
        )

    payload = json.loads(
        SELECTED_FEATURES_INPUT.read_text(
            encoding="utf-8"
        )
    )

    required = {
        "selected_features",
        "training_medians",
        "training_sha256",
        "validation_sha256",
    }

    missing = (
        required
        - set(
            payload
        )
    )

    if missing:

        raise ValueError(
            (
                "Phase 17 behavioural "
                "feature-selection file is "
                "missing fields: "
                f"{sorted(missing)}"
            )
        )

    if not payload[
        "selected_features"
    ]:

        raise ValueError(
            (
                "Phase 17 behavioural "
                "selected-feature list is empty."
            )
        )

    return payload


def _validate_phase17_hashes(
    payload: dict,
) -> None:

    training_hash = _sha256(
        TRAINING_INPUT
    )

    validation_hash = _sha256(
        VALIDATION_INPUT
    )

    if (
        training_hash
        != payload[
            "training_sha256"
        ]
    ):

        raise ValueError(
            (
                "Behavioural training split "
                "has changed since Phase 17."
            )
        )

    if (
        validation_hash
        != payload[
            "validation_sha256"
        ]
    ):

        raise ValueError(
            (
                "Behavioural validation split "
                "has changed since Phase 17."
            )
        )


def _validate_domain_labels(
    training: pd.DataFrame,
) -> None:

    if (
        "registrable_domain"
        not in training.columns
    ):

        raise ValueError(
            (
                "registrable_domain is required "
                "for grouped RF-B tuning."
            )
        )

    if training[
        "registrable_domain"
    ].isna().any():

        raise ValueError(
            (
                "registrable_domain contains "
                "missing values."
            )
        )

    conflicts = (
        training.groupby(
            "registrable_domain"
        )[
            "binary_label"
        ]
        .nunique()
    )

    conflicts = conflicts[
        conflicts > 1
    ]

    if not conflicts.empty:

        raise ValueError(
            (
                "Some registrable domains "
                "contain conflicting labels."
            )
        )


def _choose_cv_splits(
    training: pd.DataFrame,
) -> int:

    domain_labels = (
        training[
            [
                "registrable_domain",
                "binary_label",
            ]
        ]
        .drop_duplicates(
            subset=[
                "registrable_domain"
            ]
        )
    )

    counts = (
        domain_labels[
            "binary_label"
        ]
        .value_counts()
    )

    legitimate_domains = int(
        counts.get(
            0,
            0,
        )
    )

    scam_domains = int(
        counts.get(
            1,
            0,
        )
    )

    minimum_class_domains = min(
        legitimate_domains,
        scam_domains,
    )

    if minimum_class_domains < 3:

        raise ValueError(
            (
                "RF-B tuning requires at least "
                "three unique registrable domains "
                "from each binary class inside "
                "the training partition. "
                f"Legitimate domains: "
                f"{legitimate_domains}; "
                f"Scam domains: "
                f"{scam_domains}."
            )
        )

    return min(
        5,
        minimum_class_domains,
    )


def _build_scoring() -> dict:

    return {
        "f1":
            make_scorer(
                f1_score,
                zero_division=0,
            ),

        "precision":
            make_scorer(
                precision_score,
                zero_division=0,
            ),

        "recall":
            make_scorer(
                recall_score,
                zero_division=0,
            ),
    }


def main():

    print()

    print(
        "PHASE 19 — RF-B BEHAVIOURAL "
        "MODEL TRAINING"
    )

    print(
        "=" * 72
    )

    training = _read_csv(
        TRAINING_INPUT
    )

    validation = _read_csv(
        VALIDATION_INPUT
    )

    feature_selection = (
        _read_feature_selection()
    )

    _validate_phase17_hashes(
        feature_selection
    )

    _validate_domain_labels(
        training
    )

    selected_features = (
        feature_selection[
            "selected_features"
        ]
    )

    training_medians = (
        feature_selection[
            "training_medians"
        ]
    )

    x_train = (
        prepare_selected_features(
            dataframe=training,

            selected_features=(
                selected_features
            ),

            training_medians=(
                training_medians
            ),
        )
    )

    x_validation = (
        prepare_selected_features(
            dataframe=validation,

            selected_features=(
                selected_features
            ),

            training_medians=(
                training_medians
            ),
        )
    )

    y_train = (
        validate_training_labels(
            training[
                "binary_label"
            ]
        )
    )

    y_validation = (
        validate_training_labels(
            validation[
                "binary_label"
            ]
        )
    )

    groups = training[
        "registrable_domain"
    ].astype(str)

    cv_splits = (
        _choose_cv_splits(
            training
        )
    )

    print(
        f"Training rows: "
        f"{len(training)}"
    )

    print(
        f"Validation rows: "
        f"{len(validation)}"
    )

    print(
        "Unique training domains: "
        f"{groups.nunique()}"
    )

    print(
        "Selected behavioural features: "
        f"{len(selected_features)}"
    )

    print(
        f"Grouped CV folds: "
        f"{cv_splits}"
    )

    print()

    print(
        "Starting training-only "
        "hyperparameter search..."
    )

    cross_validator = (
        StratifiedGroupKFold(
            n_splits=cv_splits,

            shuffle=True,

            random_state=(
                RANDOM_STATE
            ),
        )
    )

    base_model = (
        RandomForestClassifier(
            random_state=(
                RANDOM_STATE
            ),

            n_jobs=-1,
        )
    )

    search = GridSearchCV(
        estimator=base_model,

        param_grid=(
            PARAMETER_GRID
        ),

        scoring=(
            _build_scoring()
        ),

        refit="f1",

        cv=cross_validator,

        n_jobs=-1,

        return_train_score=False,

        error_score="raise",

        verbose=1,
    )

    search.fit(
        x_train,
        y_train,
        groups=groups,
    )

    best_model = (
        search.best_estimator_
    )

    print()

    print(
        "Hyperparameter search complete."
    )

    print(
        f"Best training CV F1: "
        f"{search.best_score_:.4f}"
    )

    print()

    print(
        "Best parameters:"
    )

    for (
        parameter,
        value,
    ) in (
        search.best_params_
        .items()
    ):

        print(
            f"  {parameter}: {value}"
        )

    # -----------------------------------------
    # Save tuning results.
    # -----------------------------------------

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    tuning_results = pd.DataFrame(
        search.cv_results_
    )

    useful_columns = [
        column
        for column in [
            "rank_test_f1",
            "mean_test_f1",
            "std_test_f1",
            "mean_test_precision",
            "mean_test_recall",
            "mean_fit_time",
            "param_n_estimators",
            "param_max_depth",
            "param_min_samples_split",
            "param_min_samples_leaf",
            "param_max_features",
            "param_class_weight",
            "params",
        ]
        if column
        in tuning_results.columns
    ]

    (
        tuning_results[
            useful_columns
        ]
        .sort_values(
            by="rank_test_f1"
        )
        .to_csv(
            TUNING_OUTPUT,
            index=False,
        )
    )

    # -----------------------------------------
    # Validation probabilities P_B.
    # -----------------------------------------

    validation_probability = (
        scam_probability(
            best_model,
            x_validation,
        )
    )

    validation_result = (
        evaluate_validation(
            y_true=y_validation,

            scam_probabilities=(
                validation_probability
            ),

            threshold=0.50,
        )
    )

    validation_prediction = (
        validation_probability
        >= 0.50
    ).astype(int)

    print()

    print(
        "VALIDATION RESULTS "
        "(threshold = 0.50)"
    )

    print(
        "-" * 72
    )

    print(
        f"Accuracy:  "
        f"{validation_result.accuracy:.4f}"
    )

    print(
        f"Precision: "
        f"{validation_result.precision:.4f}"
    )

    print(
        f"Recall:    "
        f"{validation_result.recall:.4f}"
    )

    print(
        f"F1:        "
        f"{validation_result.f1:.4f}"
    )

    print(
        f"ROC-AUC:   "
        f"{validation_result.roc_auc:.4f}"
    )

    print()

    print(
        "Confusion matrix:"
    )

    print(
        (
            f"TN={validation_result.true_negative}  "
            f"FP={validation_result.false_positive}"
        )
    )

    print(
        (
            f"FN={validation_result.false_negative}  "
            f"TP={validation_result.true_positive}"
        )
    )

    # -----------------------------------------
    # Save validation predictions.
    # -----------------------------------------

    prediction_columns = {}

    for column in [
        "url",
        "registrable_domain",
        "source",
        "scam_category",
        "binary_label",
    ]:

        if column in validation.columns:

            prediction_columns[
                column
            ] = validation[
                column
            ].values

    prediction_columns[
        "rf_b_probability"
    ] = validation_probability

    prediction_columns[
        "rf_b_prediction_at_0_5"
    ] = validation_prediction

    validation_predictions = (
        pd.DataFrame(
            prediction_columns
        )
    )

    validation_predictions.to_csv(
        VALIDATION_PREDICTIONS_OUTPUT,
        index=False,
    )

    # -----------------------------------------
    # Feature importance.
    # -----------------------------------------

    importance = (
        feature_importance_table(
            best_model,
            selected_features,
        )
    )

    importance.to_csv(
        IMPORTANCE_OUTPUT,
        index=False,
    )

    # -----------------------------------------
    # Validation metrics.
    # -----------------------------------------

    metrics_payload = {
        "threshold_used_for_diagnostics":
            0.50,

        "accuracy":
            validation_result.accuracy,

        "precision":
            validation_result.precision,

        "recall":
            validation_result.recall,

        "f1":
            validation_result.f1,

        "roc_auc":
            validation_result.roc_auc,

        "true_negative":
            validation_result.true_negative,

        "false_positive":
            validation_result.false_positive,

        "false_negative":
            validation_result.false_negative,

        "true_positive":
            validation_result.true_positive,

        "best_training_cv_f1":
            float(
                search.best_score_
            ),

        "best_parameters":
            search.best_params_,

        "grouped_cv_folds":
            cv_splits,

        "selected_feature_count":
            len(
                selected_features
            ),
    }

    VALIDATION_METRICS_OUTPUT.write_text(
        json.dumps(
            metrics_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    # -----------------------------------------
    # Save RF-B bundle.
    # -----------------------------------------

    MODEL_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_bundle = {
        "model_name":
            "RF-B",

        "model_type":
            "RandomForestClassifier",

        "target":
            "binary_label",

        "positive_class":
            1,

        "positive_class_name":
            "scam",

        "estimator":
            best_model,

        "selected_features":
            selected_features,

        "training_medians":
            training_medians,

        "random_state":
            RANDOM_STATE,

        "best_parameters":
            search.best_params_,

        "training_cv_f1":
            float(
                search.best_score_
            ),

        "validation_metrics":
            metrics_payload,

        "phase17_selection_file":
            str(
                SELECTED_FEATURES_INPUT
            ),

        "training_sha256":
            _sha256(
                TRAINING_INPUT
            ),

        "validation_sha256":
            _sha256(
                VALIDATION_INPUT
            ),
    }

    joblib.dump(
        model_bundle,
        MODEL_OUTPUT,
    )

    # -----------------------------------------
    # Manifest.
    # -----------------------------------------

    manifest_lines = [
        "PHASE 19 RF-B TRAINING MANIFEST",
        "=" * 72,

        "Model: RandomForestClassifier",

        (
            "Probability output: "
            "P_B = P(y=1 | X_B)"
        ),

        "Positive class: 1 = scam website",

        (
            "Selected behavioural features: "
            f"{len(selected_features)}"
        ),

        (
            "Training rows: "
            f"{len(training)}"
        ),

        (
            "Validation rows: "
            f"{len(validation)}"
        ),

        (
            "Unique training domains: "
            f"{groups.nunique()}"
        ),

        (
            "Grouped CV folds: "
            f"{cv_splits}"
        ),

        (
            "Random state: "
            f"{RANDOM_STATE}"
        ),

        (
            "Training CV best F1: "
            f"{search.best_score_:.8f}"
        ),

        (
            "Validation F1 at threshold 0.50: "
            f"{validation_result.f1:.8f}"
        ),

        (
            "Validation ROC-AUC: "
            f"{validation_result.roc_auc:.8f}"
        ),

        (
            "Training SHA256: "
            f"{_sha256(TRAINING_INPUT)}"
        ),

        (
            "Validation SHA256: "
            f"{_sha256(VALIDATION_INPUT)}"
        ),

        "",
        "Best parameters:",
    ]

    for (
        parameter,
        value,
    ) in search.best_params_.items():

        manifest_lines.append(
            (
                f"{parameter}: "
                f"{value}"
            )
        )

    manifest_lines.extend(
        [
            "",

            (
                "Final test set used during "
                "RF-B training or tuning: NO"
            ),

            (
                "Probability threshold tuned "
                "during Phase 19: NO"
            ),

            (
                "Validation threshold 0.50 "
                "was used for diagnostic "
                "classification metrics only."
            ),

            (
                "RF-B uses the same classifier "
                "family as RF-H so the principal "
                "comparison focuses on evidence "
                "type rather than different "
                "learning algorithms."
            ),
        ]
    )

    MANIFEST_OUTPUT.write_text(
        "\n".join(
            manifest_lines
        ),
        encoding="utf-8",
    )

    print()

    print(
        "Top behavioural feature importance:"
    )

    print(
        importance.head(
            15
        ).to_string(
            index=False
        )
    )

    print()

    print(
        f"RF-B model saved: "
        f"{MODEL_OUTPUT}"
    )

    print(
        f"Tuning results: "
        f"{TUNING_OUTPUT}"
    )

    print(
        f"Feature importance: "
        f"{IMPORTANCE_OUTPUT}"
    )

    print(
        f"Validation predictions: "
        f"{VALIDATION_PREDICTIONS_OUTPUT}"
    )

    print(
        f"Validation metrics: "
        f"{VALIDATION_METRICS_OUTPUT}"
    )

    print(
        f"Training manifest: "
        f"{MANIFEST_OUTPUT}"
    )


if __name__ == "__main__":
    main()