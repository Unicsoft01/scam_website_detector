import json
from hashlib import sha256
from pathlib import Path

import pandas as pd

from app.ml.hybrid_fusion import (
    calibrate_fusion,
    choose_best_fusion,
    classify_probabilities,
    evaluate_fusion,
    fuse_probabilities,
)


HEURISTIC_PREDICTIONS = Path(
    "data/processed/model_training/"
    "heuristic_validation_predictions.csv"
)

BEHAVIOURAL_PREDICTIONS = Path(
    "data/processed/model_training/"
    "behavioural_validation_predictions.csv"
)

CALIBRATION_OUTPUT = Path(
    "data/processed/model_training/"
    "hybrid_calibration_results.csv"
)

PREDICTIONS_OUTPUT = Path(
    "data/processed/model_training/"
    "hybrid_validation_predictions.csv"
)

METRICS_OUTPUT = Path(
    "data/processed/model_training/"
    "hybrid_validation_metrics.json"
)

MANIFEST_OUTPUT = Path(
    "data/processed/model_training/"
    "hybrid_fusion_manifest.txt"
)

CONFIG_OUTPUT = Path(
    "models/"
    "hybrid_fusion_config.json"
)


def _read_csv(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(
            (
                "Required Phase 18/19 "
                f"prediction file missing: {path}"
            )
        )

    try:

        dataframe = pd.read_csv(
            path
        )

    except pd.errors.EmptyDataError:

        raise ValueError(
            f"Prediction file is empty: {path}"
        )

    if dataframe.empty:

        raise ValueError(
            f"Prediction file has no rows: {path}"
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


def _prepare_common_validation(
    heuristic: pd.DataFrame,
    behavioural: pd.DataFrame,
) -> pd.DataFrame:

    required_h = {
        "url",
        "binary_label",
        "rf_h_probability",
    }

    required_b = {
        "url",
        "binary_label",
        "rf_b_probability",
    }

    missing_h = (
        required_h
        - set(
            heuristic.columns
        )
    )

    missing_b = (
        required_b
        - set(
            behavioural.columns
        )
    )

    if missing_h:

        raise ValueError(
            (
                "Heuristic prediction file "
                f"missing: {sorted(missing_h)}"
            )
        )

    if missing_b:

        raise ValueError(
            (
                "Behavioural prediction file "
                f"missing: {sorted(missing_b)}"
            )
        )

    if heuristic[
        "url"
    ].duplicated().any():

        raise ValueError(
            (
                "Duplicate URLs found in "
                "heuristic validation predictions."
            )
        )

    if behavioural[
        "url"
    ].duplicated().any():

        raise ValueError(
            (
                "Duplicate URLs found in "
                "behavioural validation predictions."
            )
        )

    merged = heuristic.merge(
        behavioural[
            [
                "url",
                "binary_label",
                "rf_b_probability",
            ]
        ],

        on="url",

        how="inner",

        suffixes=(
            "_h",
            "_b",
        ),

        validate="one_to_one",
    )

    if len(
        merged
    ) != len(
        heuristic
    ):

        raise ValueError(
            (
                "Heuristic and behavioural "
                "validation URL populations "
                "are not identical."
            )
        )

    if len(
        merged
    ) != len(
        behavioural
    ):

        raise ValueError(
            (
                "Heuristic and behavioural "
                "validation URL populations "
                "are not identical."
            )
        )

    if not (
        merged[
            "binary_label_h"
        ].astype(int)
        ==
        merged[
            "binary_label_b"
        ].astype(int)
    ).all():

        raise ValueError(
            (
                "Conflicting labels found "
                "between RF-H and RF-B "
                "validation predictions."
            )
        )

    merged[
        "binary_label"
    ] = merged[
        "binary_label_h"
    ].astype(int)

    merged = merged.drop(
        columns=[
            "binary_label_h",
            "binary_label_b",
        ]
    )

    if merged[
        "rf_h_probability"
    ].isna().any():

        raise ValueError(
            (
                "Missing RF-H validation "
                "probabilities detected."
            )
        )

    if merged[
        "rf_b_probability"
    ].isna().any():

        raise ValueError(
            (
                "Missing RF-B validation "
                "probabilities detected. "
                "Hybrid calibration requires "
                "the common complete subset."
            )
        )

    labels = set(
        merged[
            "binary_label"
        ].unique()
    )

    if labels != {
        0,
        1,
    }:

        raise ValueError(
            (
                "Hybrid validation requires "
                "both classes 0 and 1. "
                f"Found: {sorted(labels)}"
            )
        )

    return merged


def main():

    print()

    print(
        "PHASE 20 — HYBRID EVIDENCE FUSION"
    )

    print(
        "=" * 72
    )

    heuristic = _read_csv(
        HEURISTIC_PREDICTIONS
    )

    behavioural = _read_csv(
        BEHAVIOURAL_PREDICTIONS
    )

    common = (
        _prepare_common_validation(
            heuristic,
            behavioural,
        )
    )

    print(
        f"Common validation records: "
        f"{len(common)}"
    )

    print(
        "Legitimate validation records: "
        f"{int((common['binary_label'] == 0).sum())}"
    )

    print(
        "Scam validation records: "
        f"{int((common['binary_label'] == 1).sum())}"
    )

    print()

    print(
        "Calibrating alpha and threshold "
        "using validation data only..."
    )

    calibration = (
        calibrate_fusion(
            y_true=(
                common[
                    "binary_label"
                ].values
            ),

            heuristic_probability=(
                common[
                    "rf_h_probability"
                ].values
            ),

            behavioural_probability=(
                common[
                    "rf_b_probability"
                ].values
            ),
        )
    )

    best = (
        choose_best_fusion(
            calibration
        )
    )

    alpha = float(
        best[
            "alpha"
        ]
    )

    threshold = float(
        best[
            "threshold"
        ]
    )

    hybrid_probability = (
        fuse_probabilities(
            common[
                "rf_h_probability"
            ].values,

            common[
                "rf_b_probability"
            ].values,

            alpha=alpha,
        )
    )

    metrics = (
        evaluate_fusion(
            y_true=(
                common[
                    "binary_label"
                ].values
            ),

            hybrid_probability=(
                hybrid_probability
            ),

            alpha=alpha,

            threshold=threshold,
        )
    )

    predictions = (
        classify_probabilities(
            hybrid_probability,
            threshold=threshold,
        )
    )

    print()

    print(
        "SELECTED VALIDATION CONFIGURATION"
    )

    print(
        "-" * 72
    )

    print(
        f"Alpha:     {alpha:.2f}"
    )

    print(
        f"Threshold: {threshold:.2f}"
    )

    print()

    print(
        "VALIDATION RESULTS"
    )

    print(
        "-" * 72
    )

    print(
        f"Accuracy:  {metrics.accuracy:.4f}"
    )

    print(
        f"Precision: {metrics.precision:.4f}"
    )

    print(
        f"Recall:    {metrics.recall:.4f}"
    )

    print(
        f"F1:        {metrics.f1:.4f}"
    )

    print(
        f"ROC-AUC:   {metrics.roc_auc:.4f}"
    )

    print(
        f"FPR:       "
        f"{metrics.false_positive_rate:.4f}"
    )

    print(
        f"FNR:       "
        f"{metrics.false_negative_rate:.4f}"
    )

    print()

    print(
        (
            f"TN={metrics.true_negative}  "
            f"FP={metrics.false_positive}"
        )
    )

    print(
        (
            f"FN={metrics.false_negative}  "
            f"TP={metrics.true_positive}"
        )
    )

    CALIBRATION_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    calibration.to_csv(
        CALIBRATION_OUTPUT,
        index=False,
    )

    validation_output = (
        common.copy()
    )

    validation_output[
        "hybrid_probability"
    ] = hybrid_probability

    validation_output[
        "hybrid_prediction"
    ] = predictions

    validation_output.to_csv(
        PREDICTIONS_OUTPUT,
        index=False,
    )

    metrics_payload = {
        "alpha":
            alpha,

        "threshold":
            threshold,

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

        "calibration_partition":
            "validation",

        "test_set_used":
            False,
    }

    METRICS_OUTPUT.write_text(
        json.dumps(
            metrics_payload,
            indent=2,
        ),

        encoding="utf-8",
    )

    CONFIG_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    config_payload = {
        "fusion_method":
            "weighted_probability_average",

        "formula":
            (
                "P_Hybrid = alpha * P_H "
                "+ (1-alpha) * P_B"
            ),

        "alpha":
            alpha,

        "heuristic_weight":
            alpha,

        "behavioural_weight":
            (
                1.0
                - alpha
            ),

        "classification_threshold":
            threshold,

        "positive_class":
            1,

        "positive_class_name":
            "scam",

        "alpha_selected_on":
            "validation",

        "threshold_selected_on":
            "validation",

        "test_set_used_for_calibration":
            False,

        "missing_behaviour_policy":
            (
                "Do not substitute zero. "
                "Principal hybrid evaluation "
                "requires both evidence channels; "
                "production may return explicitly "
                "labelled heuristic fallback."
            ),

        "heuristic_validation_predictions_sha256":
            _sha256(
                HEURISTIC_PREDICTIONS
            ),

        "behavioural_validation_predictions_sha256":
            _sha256(
                BEHAVIOURAL_PREDICTIONS
            ),
    }

    CONFIG_OUTPUT.write_text(
        json.dumps(
            config_payload,
            indent=2,
        ),

        encoding="utf-8",
    )

    manifest = [
        "PHASE 20 HYBRID FUSION MANIFEST",
        "=" * 72,

        (
            "Fusion: "
            "P_Hybrid = alpha*P_H "
            "+ (1-alpha)*P_B"
        ),

        (
            f"Selected alpha: "
            f"{alpha:.8f}"
        ),

        (
            f"Selected threshold: "
            f"{threshold:.8f}"
        ),

        (
            "Alpha selection partition: "
            "validation"
        ),

        (
            "Threshold selection partition: "
            "validation"
        ),

        (
            "Final test set used during "
            "calibration: NO"
        ),

        (
            "Principal hybrid analysis "
            "requires complete P_H and P_B."
        ),

        (
            "Missing behavioural evidence "
            "is never replaced with zero."
        ),

        (
            "RF-H validation prediction SHA256: "
            f"{_sha256(HEURISTIC_PREDICTIONS)}"
        ),

        (
            "RF-B validation prediction SHA256: "
            f"{_sha256(BEHAVIOURAL_PREDICTIONS)}"
        ),

        (
            f"Validation F1: "
            f"{metrics.f1:.8f}"
        ),

        (
            f"Validation recall: "
            f"{metrics.recall:.8f}"
        ),

        (
            f"Validation FPR: "
            f"{metrics.false_positive_rate:.8f}"
        ),

        "",
        (
            "Alpha and threshold are frozen "
            "after Phase 20 and must not be "
            "changed after examining the "
            "final test results."
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
        f"Calibration table: "
        f"{CALIBRATION_OUTPUT}"
    )

    print(
        f"Validation predictions: "
        f"{PREDICTIONS_OUTPUT}"
    )

    print(
        f"Metrics: "
        f"{METRICS_OUTPUT}"
    )

    print(
        f"Frozen configuration: "
        f"{CONFIG_OUTPUT}"
    )

    print(
        f"Manifest: "
        f"{MANIFEST_OUTPUT}"
    )


if __name__ == "__main__":
    main()