from pathlib import Path
import json

import joblib
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


MODEL_DIR = Path(
    "models/runtime/v1.1.0"
)

TEST_FILE = Path(
    "data/experiments/v1_1/"
    "final_hybrid_test_dataset.csv"
)

OUTPUT_JSON = (
    MODEL_DIR
    / "evaluation_results.json"
)

OUTPUT_PREDICTIONS = Path(
    "data/experiments/v1_1/"
    "final_test_predictions.csv"
)

OUTPUT_COMPARISON = Path(
    "data/experiments/v1_1/"
    "final_model_comparison.csv"
)

OUTPUT_CATEGORY = Path(
    "data/experiments/v1_1/"
    "final_category_performance.csv"
)


def load_features(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        obj = json.load(file)

    if isinstance(obj, list):
        return obj

    if isinstance(obj, dict):
        if "features" in obj:
            return obj["features"]

        if "selected_features" in obj:
            return obj[
                "selected_features"
            ]

    raise RuntimeError(
        f"Cannot read features from {path}"
    )


def evaluate(
    y_true,
    probabilities,
    threshold,
):
    predictions = (
        probabilities >= threshold
    ).astype(int)

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    tn, fp, fn, tp = (
        matrix.ravel()
    )

    if len(
        np.unique(y_true)
    ) == 2:
        auc = roc_auc_score(
            y_true,
            probabilities,
        )
    else:
        auc = None

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else None
    )

    return {
        "accuracy": float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),
        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": (
            float(auc)
            if auc is not None
            else None
        ),
        "false_positive_rate": (
            float(fpr)
            if fpr is not None
            else None
        ),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def main():
    required_files = [
        TEST_FILE,
        MODEL_DIR
        / "rf_heuristic.joblib",
        MODEL_DIR
        / "rf_behavioural.joblib",
        MODEL_DIR
        / "heuristic_features.json",
        MODEL_DIR
        / "behavioural_features.json",
        MODEL_DIR
        / "hybrid_fusion_config.json",
    ]

    for path in required_files:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file missing: {path}"
            )

    data = pd.read_csv(
        TEST_FILE
    )

    if data.empty:
        raise RuntimeError(
            "Final test dataset is empty."
        )

    heuristic_features = load_features(
        MODEL_DIR
        / "heuristic_features.json"
    )

    behavioural_features = load_features(
        MODEL_DIR
        / "behavioural_features.json"
    )

    with open(
        MODEL_DIR
        / "hybrid_fusion_config.json",
        "r",
        encoding="utf-8",
    ) as file:
        fusion = json.load(file)

    required_config = [
        "alpha",
        "heuristic_threshold",
        "behavioural_threshold",
        "hybrid_threshold",
    ]

    for key in required_config:
        if key not in fusion:
            raise RuntimeError(
                f"Missing fusion setting: {key}"
            )

    missing_h = [
        feature
        for feature
        in heuristic_features
        if feature
        not in data.columns
    ]

    missing_b = [
        feature
        for feature
        in behavioural_features
        if feature
        not in data.columns
    ]

    if missing_h:
        raise RuntimeError(
            "Missing heuristic features: "
            f"{missing_h}"
        )

    if missing_b:
        raise RuntimeError(
            "Missing behavioural features: "
            f"{missing_b}"
        )

    rf_h = joblib.load(
        MODEL_DIR
        / "rf_heuristic.joblib"
    )

    rf_b = joblib.load(
        MODEL_DIR
        / "rf_behavioural.joblib"
    )

    X_h = data[
        heuristic_features
    ]

    X_b = data[
        behavioural_features
    ]

    y_true = (
        data["binary_label"]
        .astype(int)
        .to_numpy()
    )

    p_h = (
        rf_h.predict_proba(
            X_h
        )[:, 1]
    )

    p_b = (
        rf_b.predict_proba(
            X_b
        )[:, 1]
    )

    alpha = float(
        fusion["alpha"]
    )

    p_hybrid = (
        alpha * p_h
        +
        (1.0 - alpha) * p_b
    )

    h_threshold = float(
        fusion[
            "heuristic_threshold"
        ]
    )

    b_threshold = float(
        fusion[
            "behavioural_threshold"
        ]
    )

    hybrid_threshold = float(
        fusion[
            "hybrid_threshold"
        ]
    )

    h_result = evaluate(
        y_true,
        p_h,
        h_threshold,
    )

    b_result = evaluate(
        y_true,
        p_b,
        b_threshold,
    )

    hybrid_result = evaluate(
        y_true,
        p_hybrid,
        hybrid_threshold,
    )

    results = {
        "model_version": "v1.1.0",
        "test_sample_count": (
            int(len(data))
        ),
        "unique_test_domains": (
            int(
                data[
                    "registrable_domain"
                ].nunique()
            )
        ),
        "class_distribution": {
            str(key): int(value)
            for key, value
            in data[
                "binary_label"
            ]
            .value_counts()
            .to_dict()
            .items()
        },
        "alpha": alpha,
        "heuristic_threshold": (
            h_threshold
        ),
        "behavioural_threshold": (
            b_threshold
        ),
        "hybrid_threshold": (
            hybrid_threshold
        ),
        "heuristic": h_result,
        "behavioural": b_result,
        "hybrid": hybrid_result,
        "post_test_tuning_permitted": (
            False
        ),
    }

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    predictions = data[
        [
            "url",
            "registrable_domain",
            "binary_label",
            "scam_category",
            "source",
        ]
    ].copy()

    predictions[
        "heuristic_probability"
    ] = p_h

    predictions[
        "behavioural_probability"
    ] = p_b

    predictions[
        "hybrid_probability"
    ] = p_hybrid

    predictions[
        "heuristic_prediction"
    ] = (
        p_h >= h_threshold
    ).astype(int)

    predictions[
        "behavioural_prediction"
    ] = (
        p_b >= b_threshold
    ).astype(int)

    predictions[
        "hybrid_prediction"
    ] = (
        p_hybrid
        >= hybrid_threshold
    ).astype(int)

    predictions.to_csv(
        OUTPUT_PREDICTIONS,
        index=False,
    )

    comparison = pd.DataFrame(
        [
            {
                "model": "RF-H",
                **h_result,
            },
            {
                "model": "RF-B",
                **b_result,
            },
            {
                "model": "Hybrid",
                **hybrid_result,
            },
        ]
    )

    comparison.to_csv(
        OUTPUT_COMPARISON,
        index=False,
    )

    scam_rows = (
        predictions[
            predictions[
                "binary_label"
            ] == 1
        ]
        .copy()
    )

    category_rows = []

    for category, group in (
        scam_rows.groupby(
            "scam_category"
        )
    ):
        n = len(group)

        category_rows.append(
            {
                "scam_category": (
                    category
                ),
                "n": n,
                "heuristic_recall": (
                    group[
                        "heuristic_prediction"
                    ].mean()
                ),
                "behavioural_recall": (
                    group[
                        "behavioural_prediction"
                    ].mean()
                ),
                "hybrid_recall": (
                    group[
                        "hybrid_prediction"
                    ].mean()
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    category_df.to_csv(
        OUTPUT_CATEGORY,
        index=False,
    )

    print(
        "\n================================"
    )
    print(
        "FINAL V1.1.0 TEST EVALUATION"
    )
    print(
        "================================"
    )

    print(
        "TEST ROWS:",
        len(data),
    )

    print(
        "UNIQUE TEST DOMAINS:",
        data[
            "registrable_domain"
        ].nunique(),
    )

    print(
        "\nCLASS DISTRIBUTION:"
    )
    print(
        data[
            "binary_label"
        ].value_counts()
    )

    print(
        "\nSCAM CATEGORY DISTRIBUTION:"
    )
    print(
        data[
            "scam_category"
        ].value_counts(
            dropna=False
        )
    )

    print(
        "\nRF-H:"
    )
    print(
        h_result
    )

    print(
        "\nRF-B:"
    )
    print(
        b_result
    )

    print(
        "\nHYBRID:"
    )
    print(
        hybrid_result
    )

    print(
        "\nFINAL TEST HAS NOW BEEN OPENED."
    )
    print(
        "DO NOT RETUNE V1.1.0."
    )

    print(
        "\nSaved:",
        OUTPUT_JSON,
    )

    print(
        "Saved:",
        OUTPUT_PREDICTIONS,
    )

    print(
        "Saved:",
        OUTPUT_COMPARISON,
    )

    print(
        "Saved:",
        OUTPUT_CATEGORY,
    )


if __name__ == "__main__":
    main()