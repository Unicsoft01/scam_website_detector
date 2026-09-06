from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    auc,
)


# ============================================================
# PATHS
# ============================================================

BASE = Path("data/experiments/v1_1")

MODEL_DIR = Path(
    "models/runtime/v1.1.0"
)

FIGURE_DIR = Path(
    "reports/figures/v1_1"
)

PREDICTIONS_FILE = (
    BASE
    / "final_test_predictions.csv"
)

COMPARISON_FILE = (
    BASE
    / "final_model_comparison.csv"
)

CATEGORY_FILE = (
    BASE
    / "final_category_performance.csv"
)

PERFORMANCE_FILE = (
    BASE
    / "performance_test_results.csv"
)

PERFORMANCE_SUMMARY_FILE = (
    BASE
    / "performance_test_summary.csv"
)

EVALUATION_JSON = (
    MODEL_DIR
    / "evaluation_results.json"
)


# ============================================================
# SETTINGS
# ============================================================

DPI = 300

MIN_CATEGORY_N = 5

TOP_FEATURES = 15


# ============================================================
# UTILITIES
# ============================================================

def save_figure(
    figure,
    filename,
):
    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = (
        FIGURE_DIR
        / filename
    )

    figure.tight_layout()

    figure.savefig(
        output,
        dpi=DPI,
        bbox_inches="tight",
    )

    plt.close(
        figure
    )

    print(
        "CREATED:",
        output,
    )


def load_predictions():
    if not PREDICTIONS_FILE.exists():
        print(
            "SKIPPED prediction-based figures:"
            " final_test_predictions.csv not found."
        )

        return None

    try:
        data = pd.read_csv(
            PREDICTIONS_FILE
        )

    except Exception as exc:
        print(
            "SKIPPED prediction-based figures:",
            exc,
        )

        return None

    if data.empty:
        print(
            "SKIPPED prediction-based figures:"
            " prediction file is empty."
        )

        return None

    return data


def require_columns(
    dataframe,
    columns,
    figure_name,
):
    missing = [
        column
        for column in columns
        if column
        not in dataframe.columns
    ]

    if missing:
        print(
            f"SKIPPED {figure_name}: "
            f"missing columns {missing}"
        )

        return False

    return True


def load_feature_names(path):

    if not path.exists():
        return None

    try:

        # CSV feature metadata
        if path.suffix.lower() == ".csv":

            data = pd.read_csv(path)

            possible_columns = [
                "feature",
                "features",
                "feature_name",
                "name"
            ]

            for column in possible_columns:
                if column in data.columns:
                    return (
                        data[column]
                        .astype(str)
                        .tolist()
                    )

            return None


        # JSON feature metadata
        if path.suffix.lower() == ".json":

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                obj = json.load(file)


            if isinstance(obj, list):
                return obj


            if isinstance(obj, dict):

                if "features" in obj:
                    return obj["features"]

                if "selected_features" in obj:
                    return obj["selected_features"]


    except Exception:

        return None


    return None


# ============================================================
# FIGURE 1-3:
# CONFUSION MATRICES
# ============================================================

def plot_confusion_matrix(
    data,
    prediction_column,
    title,
    filename,
):
    required = [
        "binary_label",
        prediction_column,
    ]

    if not require_columns(
        data,
        required,
        title,
    ):
        return

    clean = data[
        required
    ].dropna().copy()

    if clean.empty:
        print(
            f"SKIPPED {title}: "
            "no usable rows."
        )

        return

    y_true = (
        clean[
            "binary_label"
        ]
        .astype(int)
        .to_numpy()
    )

    y_pred = (
        clean[
            prediction_column
        ]
        .astype(int)
        .to_numpy()
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    )

    figure, axis = plt.subplots(
        figsize=(6.5, 5.5)
    )

    image = axis.imshow(
        matrix,
    )

    figure.colorbar(
        image,
        ax=axis,
        fraction=0.046,
        pad=0.04,
    )

    axis.set_xticks(
        [0, 1]
    )

    axis.set_yticks(
        [0, 1]
    )

    axis.set_xticklabels(
        [
            "Legitimate",
            "Scam",
        ]
    )

    axis.set_yticklabels(
        [
            "Legitimate",
            "Scam",
        ]
    )

    axis.set_xlabel(
        "Predicted class"
    )

    axis.set_ylabel(
        "Actual class"
    )

    axis.set_title(
        title
    )

    maximum = (
        matrix.max()
        if matrix.size
        else 0
    )

    threshold = (
        maximum / 2
        if maximum
        else 0
    )

    for row in range(2):
        for column in range(2):
            value = matrix[
                row,
                column,
            ]

            text_color = (
                "white"
                if value > threshold
                else "black"
            )

            axis.text(
                column,
                row,
                str(value),
                ha="center",
                va="center",
                color=text_color,
                fontsize=13,
                fontweight="bold",
            )

    save_figure(
        figure,
        filename,
    )


# ============================================================
# FIGURE 4:
# METRIC COMPARISON
# ============================================================

def load_comparison_metrics():
    if COMPARISON_FILE.exists():
        try:
            data = pd.read_csv(
                COMPARISON_FILE
            )

            required = {
                "model",
                "accuracy",
                "precision",
                "recall",
                "f1",
            }

            if required.issubset(
                set(data.columns)
            ):
                return data

        except Exception:
            pass

    if not EVALUATION_JSON.exists():
        return None

    try:
        with open(
            EVALUATION_JSON,
            "r",
            encoding="utf-8",
        ) as file:
            results = json.load(
                file
            )

    except Exception:
        return None

    rows = []

    mappings = [
        (
            "RF-H",
            "heuristic",
        ),
        (
            "RF-B",
            "behavioural",
        ),
        (
            "Hybrid",
            "hybrid",
        ),
    ]

    for display_name, key in mappings:
        metrics = results.get(
            key
        )

        if not isinstance(
            metrics,
            dict,
        ):
            continue

        rows.append(
            {
                "model": display_name,
                **metrics,
            }
        )

    if not rows:
        return None

    return pd.DataFrame(
        rows
    )


def plot_metric_comparison():
    data = load_comparison_metrics()

    if data is None:
        print(
            "SKIPPED metric comparison: "
            "final model metrics not found."
        )

        return

    metrics = [
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]

    if not all(
        metric in data.columns
        for metric in metrics
    ):
        print(
            "SKIPPED metric comparison: "
            "required metric columns missing."
        )

        return

    models = (
        data[
            "model"
        ]
        .astype(str)
        .tolist()
    )

    x = np.arange(
        len(models)
    )

    number_of_metrics = len(
        metrics
    )

    width = 0.18

    figure, axis = plt.subplots(
        figsize=(9, 6)
    )

    for index, metric in enumerate(
        metrics
    ):
        offset = (
            index
            - (
                number_of_metrics - 1
            ) / 2
        ) * width

        values = (
            pd.to_numeric(
                data[metric],
                errors="coerce",
            )
            .fillna(0)
            .to_numpy()
        )

        bars = axis.bar(
            x + offset,
            values,
            width,
            label=metric.capitalize(),
        )

        for bar, value in zip(
            bars,
            values,
        ):
            axis.text(
                bar.get_x()
                + bar.get_width() / 2,
                min(
                    value + 0.02,
                    1.03,
                ),
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    axis.set_xticks(
        x
    )

    axis.set_xticklabels(
        models
    )

    axis.set_ylim(
        0,
        1.10,
    )

    axis.set_ylabel(
        "Score"
    )

    axis.set_xlabel(
        "Detection configuration"
    )

    axis.set_title(
        "Final Model Performance Comparison"
    )

    axis.legend(
        frameon=False,
    )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "04_model_metric_comparison.png",
    )


# ============================================================
# FIGURE 5:
# ROC CURVES
# ============================================================

def plot_roc_curves(
    data,
):
    required = [
        "binary_label",
        "heuristic_probability",
        "behavioural_probability",
        "hybrid_probability",
    ]

    if not require_columns(
        data,
        required,
        "ROC curves",
    ):
        return

    clean = data[
        required
    ].dropna().copy()

    if clean[
        "binary_label"
    ].nunique() < 2:
        print(
            "SKIPPED ROC curves: "
            "test data does not contain both classes."
        )

        return

    y_true = (
        clean[
            "binary_label"
        ]
        .astype(int)
        .to_numpy()
    )

    series = [
        (
            "RF-H",
            "heuristic_probability",
        ),
        (
            "RF-B",
            "behavioural_probability",
        ),
        (
            "Hybrid",
            "hybrid_probability",
        ),
    ]

    figure, axis = plt.subplots(
        figsize=(7, 6)
    )

    for label, column in series:
        probabilities = (
            pd.to_numeric(
                clean[column],
                errors="coerce",
            )
            .to_numpy()
        )

        fpr, tpr, _ = roc_curve(
            y_true,
            probabilities,
        )

        roc_auc = auc(
            fpr,
            tpr,
        )

        axis.plot(
            fpr,
            tpr,
            linewidth=2,
            label=(
                f"{label} "
                f"(AUC = {roc_auc:.3f})"
            ),
        )

    axis.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        linewidth=1,
        label="Chance",
    )

    axis.set_xlim(
        0,
        1,
    )

    axis.set_ylim(
        0,
        1.02,
    )

    axis.set_xlabel(
        "False Positive Rate"
    )

    axis.set_ylabel(
        "True Positive Rate"
    )

    axis.set_title(
        "ROC Curves for Final Detection Models"
    )

    axis.legend(
        loc="lower right",
        frameon=False,
    )

    axis.grid(
        alpha=0.25,
    )

    save_figure(
        figure,
        "05_roc_curves.png",
    )


# ============================================================
# FIGURE 6:
# FALSE POSITIVE RATE
# ============================================================

def plot_false_positive_rate():
    data = load_comparison_metrics()

    if data is None:
        print(
            "SKIPPED false-positive-rate chart: "
            "metrics unavailable."
        )

        return

    column = None

    if (
        "false_positive_rate"
        in data.columns
    ):
        column = (
            "false_positive_rate"
        )

    elif "fpr" in data.columns:
        column = "fpr"

    if column is None:
        print(
            "SKIPPED false-positive-rate chart: "
            "FPR column unavailable."
        )

        return

    values = pd.to_numeric(
        data[column],
        errors="coerce",
    )

    valid = values.notna()

    if not valid.any():
        print(
            "SKIPPED false-positive-rate chart: "
            "no usable values."
        )

        return

    labels = (
        data.loc[
            valid,
            "model",
        ]
        .astype(str)
        .tolist()
    )

    values = values[
        valid
    ].to_numpy()

    figure, axis = plt.subplots(
        figsize=(7, 5)
    )

    bars = axis.bar(
        labels,
        values,
    )

    for bar, value in zip(
        bars,
        values,
    ):
        axis.text(
            bar.get_x()
            + bar.get_width() / 2,
            min(
                value + 0.02,
                1.03,
            ),
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )

    axis.set_ylim(
        0,
        max(
            1.0,
            float(
                np.nanmax(
                    values
                )
            ) + 0.10,
        ),
    )

    axis.set_ylabel(
        "False Positive Rate"
    )

    axis.set_xlabel(
        "Detection configuration"
    )

    axis.set_title(
        "False Positive Rate by Detection Model"
    )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "06_false_positive_rate.png",
    )


# ============================================================
# FIGURE 7:
# RESPONSE-TIME COMPARISON
# ============================================================

def plot_response_times():
    if not PERFORMANCE_FILE.exists():
        print(
            "SKIPPED response-time chart: "
            "performance_test_results.csv not found."
        )

        return

    try:
        data = pd.read_csv(
            PERFORMANCE_FILE
        )

    except Exception as exc:
        print(
            "SKIPPED response-time chart:",
            exc,
        )

        return

    possible = [
        (
            "Validation",
            "validation_time_ms",
        ),
        (
            "Heuristic",
            "heuristic_time_ms",
        ),
        (
            "Behavioural",
            "behavioural_time_ms",
        ),
        (
            "Fusion",
            "fusion_time_ms",
        ),
        (
            "Total hybrid scan",
            "total_scan_time_ms",
        ),
    ]

    rows = []

    for label, column in possible:
        if column not in data.columns:
            continue

        values = pd.to_numeric(
            data[column],
            errors="coerce",
        ).dropna()

        if values.empty:
            continue

        rows.append(
            {
                "stage": label,
                "n": int(
                    len(values)
                ),
                "median_ms": float(
                    values.median()
                ),
                "p95_ms": float(
                    values.quantile(
                        0.95
                    )
                ),
            }
        )

    if not rows:
        print(
            "SKIPPED response-time chart: "
            "no recognised timing columns."
        )

        return

    summary = pd.DataFrame(
        rows
    )

    summary.to_csv(
        BASE
        / "phase35_response_time_summary.csv",
        index=False,
    )

    x = np.arange(
        len(summary)
    )

    width = 0.36

    figure, axis = plt.subplots(
        figsize=(9, 6)
    )

    axis.bar(
        x - width / 2,
        summary[
            "median_ms"
        ],
        width,
        label="Median",
    )

    axis.bar(
        x + width / 2,
        summary[
            "p95_ms"
        ],
        width,
        label="P95",
    )

    axis.set_xticks(
        x
    )

    axis.set_xticklabels(
        summary[
            "stage"
        ],
        rotation=20,
        ha="right",
    )

    axis.set_ylabel(
        "Response time (ms)"
    )

    axis.set_xlabel(
        "Processing stage"
    )

    axis.set_title(
        "Operational Response-Time Comparison"
    )

    axis.legend(
        frameon=False,
    )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "07_response_time_comparison.png",
    )


# ============================================================
# FIGURE 8-9:
# FEATURE IMPORTANCE
# ============================================================

def plot_feature_importance(
    model_path,
    feature_path,
    title,
    filename,
):
    if not model_path.exists():
        print(
            f"SKIPPED {title}: "
            f"{model_path.name} not found."
        )

        return

    features = load_feature_names(
        feature_path
    )

    if not features:
        print(
            f"SKIPPED {title}: "
            "feature list unavailable."
        )

        return

    try:
        model = joblib.load(
            model_path
        )

    except Exception as exc:
        print(
            f"SKIPPED {title}: "
            f"could not load model: {exc}"
        )

        return

    if not hasattr(
        model,
        "feature_importances_",
    ):
        print(
            f"SKIPPED {title}: "
            "model has no feature_importances_."
        )

        return

    importance = np.asarray(
        model.feature_importances_,
        dtype=float,
    )

    if len(
        importance
    ) != len(
        features
    ):
        print(
            f"SKIPPED {title}: "
            "feature count does not match model."
        )

        return

    frame = pd.DataFrame(
        {
            "feature": features,
            "importance": importance,
        }
    )

    frame = frame.sort_values(
        "importance",
        ascending=False,
    )

    full_output = (
        BASE
        / filename.replace(
            ".png",
            ".csv",
        )
    )

    frame.to_csv(
        full_output,
        index=False,
    )

    top = (
        frame.head(
            TOP_FEATURES
        )
        .sort_values(
            "importance",
            ascending=True,
        )
    )

    figure, axis = plt.subplots(
        figsize=(9, 6)
    )

    axis.barh(
        top[
            "feature"
        ],
        top[
            "importance"
        ],
    )

    axis.set_xlabel(
        "Random Forest feature importance"
    )

    axis.set_ylabel(
        "Feature"
    )

    axis.set_title(
        title
    )

    axis.grid(
        axis="x",
        alpha=0.25,
    )

    save_figure(
        figure,
        filename,
    )


# ============================================================
# FIGURE 10:
# PER-CATEGORY RECALL
# ============================================================

def plot_category_recall(
    data,
):
    required = [
        "binary_label",
        "scam_category",
        "heuristic_prediction",
        "behavioural_prediction",
        "hybrid_prediction",
    ]

    if not require_columns(
        data,
        required,
        "per-category recall",
    ):
        return

    scam = data[
        data[
            "binary_label"
        ] == 1
    ].copy()

    if scam.empty:
        print(
            "SKIPPED per-category recall: "
            "no scam observations."
        )

        return

    rows = []

    for category, group in scam.groupby(
        "scam_category",
        dropna=False,
    ):
        n = len(
            group
        )

        if n < MIN_CATEGORY_N:
            continue

        rows.append(
            {
                "category": str(
                    category
                ),
                "n": n,
                "RF-H": float(
                    pd.to_numeric(
                        group[
                            "heuristic_prediction"
                        ],
                        errors="coerce",
                    ).mean()
                ),
                "RF-B": float(
                    pd.to_numeric(
                        group[
                            "behavioural_prediction"
                        ],
                        errors="coerce",
                    ).mean()
                ),
                "Hybrid": float(
                    pd.to_numeric(
                        group[
                            "hybrid_prediction"
                        ],
                        errors="coerce",
                    ).mean()
                ),
            }
        )

    if not rows:
        print(
            "SKIPPED per-category recall: "
            f"no category has at least "
            f"{MIN_CATEGORY_N} test observations."
        )

        return

    summary = pd.DataFrame(
        rows
    )

    summary.to_csv(
        BASE
        / "phase35_category_recall_summary.csv",
        index=False,
    )

    x = np.arange(
        len(summary)
    )

    width = 0.25

    figure, axis = plt.subplots(
        figsize=(10, 6)
    )

    axis.bar(
        x - width,
        summary["RF-H"],
        width,
        label="RF-H",
    )

    axis.bar(
        x,
        summary["RF-B"],
        width,
        label="RF-B",
    )

    axis.bar(
        x + width,
        summary["Hybrid"],
        width,
        label="Hybrid",
    )

    labels = [
        f"{row['category']}\n(n={row['n']})"
        for _, row
        in summary.iterrows()
    ]

    axis.set_xticks(
        x
    )

    axis.set_xticklabels(
        labels
    )

    axis.set_ylim(
        0,
        1.05,
    )

    axis.set_ylabel(
        "Recall"
    )

    axis.set_xlabel(
        "Scam category"
    )

    axis.set_title(
        "Recall by Scam Category"
    )

    axis.legend(
        frameon=False,
    )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "10_per_category_recall.png",
    )


# ============================================================
# FIGURE 11:
# CLASSIFICATION OUTCOME COUNTS
# ============================================================

def plot_outcome_counts(
    data,
):
    required = [
        "binary_label",
        "hybrid_prediction",
    ]

    if not require_columns(
        data,
        required,
        "hybrid outcome counts",
    ):
        return

    matrix = confusion_matrix(
        data[
            "binary_label"
        ].astype(int),
        data[
            "hybrid_prediction"
        ].astype(int),
        labels=[0, 1],
    )

    tn, fp, fn, tp = (
        matrix.ravel()
    )

    outcome = pd.DataFrame(
        {
            "outcome": [
                "True Negative",
                "False Positive",
                "False Negative",
                "True Positive",
            ],
            "count": [
                tn,
                fp,
                fn,
                tp,
            ],
        }
    )

    figure, axis = plt.subplots(
        figsize=(8, 5.5)
    )

    bars = axis.bar(
        outcome[
            "outcome"
        ],
        outcome[
            "count"
        ],
    )

    for bar, value in zip(
        bars,
        outcome[
            "count"
        ],
    ):
        axis.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height()
            + max(
                outcome[
                    "count"
                ].max()
                * 0.02,
                0.2,
            ),
            str(
                int(value)
            ),
            ha="center",
            va="bottom",
        )

    axis.set_ylabel(
        "Number of websites"
    )

    axis.set_xlabel(
        "Classification outcome"
    )

    axis.set_title(
        "Hybrid Model Classification Outcomes"
    )

    axis.grid(
        axis="y",
        alpha=0.25,
    )

    save_figure(
        figure,
        "11_hybrid_classification_outcomes.png",
    )


# ============================================================
# SUMMARY FILE
# ============================================================

def write_figure_manifest():
    figures = sorted(
        FIGURE_DIR.glob(
            "*.png"
        )
    )

    rows = []

    descriptions = {
        "01_confusion_matrix_rf_h.png":
            "Confusion matrix for the heuristic-only Random Forest model.",

        "02_confusion_matrix_rf_b.png":
            "Confusion matrix for the behavioural-only Random Forest model.",

        "03_confusion_matrix_hybrid.png":
            "Confusion matrix for the hybrid detection model.",

        "04_model_metric_comparison.png":
            "Comparison of accuracy, precision, recall and F1-score.",

        "05_roc_curves.png":
            "ROC curves and AUC values for RF-H, RF-B and Hybrid.",

        "06_false_positive_rate.png":
            "False-positive-rate comparison across the three detection configurations.",

        "07_response_time_comparison.png":
            "Median and P95 operational processing times.",

        "08_rf_h_feature_importance.png":
            "Random Forest heuristic feature-importance ranking.",

        "09_rf_b_feature_importance.png":
            "Random Forest behavioural feature-importance ranking.",

        "10_per_category_recall.png":
            "Per-category scam recall for categories meeting the minimum sample-size rule.",

        "11_hybrid_classification_outcomes.png":
            "Counts of true negatives, false positives, false negatives and true positives for the hybrid model.",
    }

    for index, path in enumerate(
        figures,
        start=1,
    ):
        rows.append(
            {
                "figure_number": (
                    index
                ),
                "filename": (
                    path.name
                ),
                "description": (
                    descriptions.get(
                        path.name,
                        "",
                    )
                ),
            }
        )

    manifest = pd.DataFrame(
        rows
    )

    manifest.to_csv(
        FIGURE_DIR
        / "figure_manifest.csv",
        index=False,
    )

    print(
        "CREATED:",
        FIGURE_DIR
        / "figure_manifest.csv",
    )


# ============================================================
# MAIN
# ============================================================

def main():
    warnings.filterwarnings(
        "ignore"
    )

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "\n========================================="
    )

    print(
        "PHASE 35 — RESULTS VISUALISATION"
    )

    print(
        "=========================================\n"
    )

    predictions = load_predictions()

    # -----------------------------------------
    # CONFUSION MATRICES
    # -----------------------------------------

    if predictions is not None:

        plot_confusion_matrix(
            predictions,
            "heuristic_prediction",
            "RF-H Confusion Matrix",
            "01_confusion_matrix_rf_h.png",
        )

        plot_confusion_matrix(
            predictions,
            "behavioural_prediction",
            "RF-B Confusion Matrix",
            "02_confusion_matrix_rf_b.png",
        )

        plot_confusion_matrix(
            predictions,
            "hybrid_prediction",
            "Hybrid Model Confusion Matrix",
            "03_confusion_matrix_hybrid.png",
        )

    # -----------------------------------------
    # MODEL COMPARISON
    # -----------------------------------------

    plot_metric_comparison()

    # -----------------------------------------
    # ROC
    # -----------------------------------------

    if predictions is not None:
        plot_roc_curves(
            predictions
        )

    # -----------------------------------------
    # FPR
    # -----------------------------------------

    plot_false_positive_rate()

    # -----------------------------------------
    # RESPONSE TIME
    # -----------------------------------------

    plot_response_times()

    # -----------------------------------------
    # RF-H IMPORTANCE
    # -----------------------------------------

    plot_feature_importance(
        MODEL_DIR
        / "rf_heuristic.joblib",

        MODEL_DIR
        / "rf_heuristic_features.csv",

        "RF-H Feature Importance",

        "08_rf_h_feature_importance.png",
    )

    # -----------------------------------------
    # RF-B IMPORTANCE
    # -----------------------------------------

    plot_feature_importance(
        MODEL_DIR
        / "rf_behavioural.joblib",

        MODEL_DIR
        / "rf_behavioural_features.csv",

        "RF-B Feature Importance",

        "09_rf_b_feature_importance.png",
    )

    # -----------------------------------------
    # CATEGORY RECALL
    # -----------------------------------------

    if predictions is not None:
        plot_category_recall(
            predictions
        )

    # -----------------------------------------
    # HYBRID OUTCOMES
    # -----------------------------------------

    if predictions is not None:
        plot_outcome_counts(
            predictions
        )

    # -----------------------------------------
    # MANIFEST
    # -----------------------------------------

    write_figure_manifest()

    print(
        "\n========================================="
    )

    print(
        "PHASE 35 VISUALISATION RUN COMPLETE"
    )

    print(
        "========================================="
    )

    print(
        "\nFigures available in:"
    )

    print(
        FIGURE_DIR
    )

    print(
        "\nA figure marked SKIPPED means the required "
        "real result file was unavailable or did not "
        "contain enough data. No results were invented."
    )


if __name__ == "__main__":
    main()