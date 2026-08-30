import json
from hashlib import sha256
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.ml.evaluation import (
    calibrate_single_model_threshold,
    category_recall_table,
    choose_baseline_threshold,
    evaluate_configuration,
    predictions_from_threshold,
    time_callable_per_record_ms,
)

from app.ml.heuristic_model import (
    prepare_selected_features as prepare_h,
    scam_probability as probability_h,
)

from app.ml.behavioural_model import (
    prepare_selected_features as prepare_b,
    scam_probability as probability_b,
)

from app.ml.hybrid_fusion import (
    fuse_probabilities,
)


HEURISTIC_MODEL_PATH = Path(
    "models/rf_heuristic.joblib"
)

BEHAVIOURAL_MODEL_PATH = Path(
    "models/rf_behavioural.joblib"
)

HYBRID_CONFIG_PATH = Path(
    "models/hybrid_fusion_config.json"
)


HEURISTIC_VALIDATION_PATH = Path(
    "data/processed/model_training/"
    "heuristic_validation_predictions.csv"
)

BEHAVIOURAL_VALIDATION_PATH = Path(
    "data/processed/model_training/"
    "behavioural_validation_predictions.csv"
)


HEURISTIC_TEST_PATH = Path(
    "data/splits/heuristic/"
    "testing.csv"
)

BEHAVIOURAL_TEST_PATH = Path(
    "data/splits/behavioural/"
    "testing.csv"
)


OUTPUT_ROOT = Path(
    "data/processed/"
    "evaluation"
)

METRICS_OUTPUT = (
    OUTPUT_ROOT
    / "experimental_metrics.csv"
)

PREDICTIONS_OUTPUT = (
    OUTPUT_ROOT
    / "experimental_test_predictions.csv"
)

CONFUSION_OUTPUT = (
    OUTPUT_ROOT
    / "confusion_matrices.csv"
)

CATEGORY_OUTPUT = (
    OUTPUT_ROOT
    / "category_recall.csv"
)

RESPONSE_TIME_OUTPUT = (
    OUTPUT_ROOT
    / "response_time_results.csv"
)

THRESHOLD_OUTPUT = (
    OUTPUT_ROOT
    / "baseline_thresholds.json"
)

SUMMARY_OUTPUT = (
    OUTPUT_ROOT
    / "experimental_summary.json"
)

MANIFEST_OUTPUT = (
    OUTPUT_ROOT
    / "experimental_evaluation_manifest.txt"
)


def _require_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            (
                "Required Phase 21 input "
                f"is missing: {path}"
            )
        )


def _read_csv(
    path: Path,
) -> pd.DataFrame:

    _require_file(
        path
    )

    try:

        dataframe = pd.read_csv(
            path
        )

    except pd.errors.EmptyDataError:

        raise ValueError(
            f"CSV is empty: {path}"
        )

    if dataframe.empty:

        raise ValueError(
            (
                "CSV contains no rows: "
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


def _validate_identical_population(
    heuristic: pd.DataFrame,
    behavioural: pd.DataFrame,
) -> None:

    required = {
        "url",
        "binary_label",
        "registrable_domain",
    }

    for (
        name,
        dataframe,
    ) in [
        (
            "heuristic",
            heuristic,
        ),
        (
            "behavioural",
            behavioural,
        ),
    ]:

        missing = (
            required
            - set(
                dataframe.columns
            )
        )

        if missing:

            raise ValueError(
                (
                    f"{name} testing data "
                    "is missing columns: "
                    f"{sorted(missing)}"
                )
            )

        if dataframe[
            "url"
        ].duplicated().any():

            raise ValueError(
                (
                    f"{name} testing data "
                    "contains duplicate URLs."
                )
            )

    h_urls = set(
        heuristic[
            "url"
        ]
    )

    b_urls = set(
        behavioural[
            "url"
        ]
    )

    if h_urls != b_urls:

        raise ValueError(
            (
                "RF-H and RF-B test URL "
                "populations are not identical. "
                f"H-only={len(h_urls-b_urls)}, "
                f"B-only={len(b_urls-h_urls)}."
            )
        )


def _align_test_data(
    heuristic: pd.DataFrame,
    behavioural: pd.DataFrame,
):

    behavioural_indexed = (
        behavioural
        .set_index(
            "url",
            drop=False,
        )
    )

    behavioural_aligned = (
        behavioural_indexed
        .loc[
            heuristic[
                "url"
            ].tolist()
        ]
        .reset_index(
            drop=True
        )
    )

    if not (
        heuristic[
            "binary_label"
        ]
        .astype(int)
        .reset_index(
            drop=True
        )
        ==
        behavioural_aligned[
            "binary_label"
        ]
        .astype(int)
        .reset_index(
            drop=True
        )
    ).all():

        raise ValueError(
            (
                "RF-H and RF-B testing "
                "labels do not match."
            )
        )

    if not (
        heuristic[
            "registrable_domain"
        ]
        .astype(str)
        .reset_index(
            drop=True
        )
        ==
        behavioural_aligned[
            "registrable_domain"
        ]
        .astype(str)
        .reset_index(
            drop=True
        )
    ).all():

        raise ValueError(
            (
                "Registrable-domain metadata "
                "does not match after alignment."
            )
        )

    return (
        heuristic.reset_index(
            drop=True
        ),
        behavioural_aligned,
    )


def _calibrate_baseline_threshold(
    path: Path,
    probability_column: str,
) -> tuple[float, pd.DataFrame]:

    dataframe = _read_csv(
        path
    )

    required = {
        "binary_label",
        probability_column,
    }

    missing = (
        required
        - set(
            dataframe.columns
        )
    )

    if missing:

        raise ValueError(
            (
                "Validation prediction file "
                f"missing: {sorted(missing)}"
            )
        )

    calibration = (
        calibrate_single_model_threshold(
            y_true=(
                dataframe[
                    "binary_label"
                ].values
            ),

            probabilities=(
                dataframe[
                    probability_column
                ].values
            ),
        )
    )

    threshold = (
        choose_baseline_threshold(
            calibration
        )
    )

    return (
        threshold,
        calibration,
    )


def _metric_row(
    result,
) -> dict:

    return {
        "configuration":
            result.configuration,

        "threshold":
            result.threshold,

        "sample_count":
            result.sample_count,

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

        "true_negative":
            result.true_negative,

        "false_positive":
            result.false_positive,

        "false_negative":
            result.false_negative,

        "true_positive":
            result.true_positive,
    }


def main():

    print()

    print(
        "PHASE 21 — EXPERIMENTAL EVALUATION"
    )

    print(
        "=" * 72
    )

    required_files = [
        HEURISTIC_MODEL_PATH,
        BEHAVIOURAL_MODEL_PATH,
        HYBRID_CONFIG_PATH,
        HEURISTIC_VALIDATION_PATH,
        BEHAVIOURAL_VALIDATION_PATH,
        HEURISTIC_TEST_PATH,
        BEHAVIOURAL_TEST_PATH,
    ]

    for path in required_files:

        _require_file(
            path
        )

    # --------------------------------------------------
    # Load frozen models/configuration.
    # --------------------------------------------------

    rf_h_bundle = joblib.load(
        HEURISTIC_MODEL_PATH
    )

    rf_b_bundle = joblib.load(
        BEHAVIOURAL_MODEL_PATH
    )

    hybrid_config = json.loads(
        HYBRID_CONFIG_PATH.read_text(
            encoding="utf-8"
        )
    )

    alpha = float(
        hybrid_config[
            "alpha"
        ]
    )

    hybrid_threshold = float(
        hybrid_config[
            "classification_threshold"
        ]
    )

    # --------------------------------------------------
    # Validation-only baseline threshold selection.
    # Test data is still untouched here.
    # --------------------------------------------------

    print(
        "Freezing RF-H and RF-B thresholds "
        "from validation predictions..."
    )

    (
        heuristic_threshold,
        heuristic_threshold_table,
    ) = _calibrate_baseline_threshold(
        HEURISTIC_VALIDATION_PATH,
        "rf_h_probability",
    )

    (
        behavioural_threshold,
        behavioural_threshold_table,
    ) = _calibrate_baseline_threshold(
        BEHAVIOURAL_VALIDATION_PATH,
        "rf_b_probability",
    )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    threshold_payload = {
        "rf_h_threshold":
            heuristic_threshold,

        "rf_b_threshold":
            behavioural_threshold,

        "hybrid_alpha":
            alpha,

        "hybrid_threshold":
            hybrid_threshold,

        "rf_h_threshold_selected_on":
            "validation",

        "rf_b_threshold_selected_on":
            "validation",

        "hybrid_parameters_selected_on":
            "validation",

        "test_set_used_for_parameter_selection":
            False,
    }

    THRESHOLD_OUTPUT.write_text(
        json.dumps(
            threshold_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"RF-H threshold frozen: "
        f"{heuristic_threshold:.2f}"
    )

    print(
        f"RF-B threshold frozen: "
        f"{behavioural_threshold:.2f}"
    )

    print(
        f"Hybrid alpha frozen: "
        f"{alpha:.2f}"
    )

    print(
        f"Hybrid threshold frozen: "
        f"{hybrid_threshold:.2f}"
    )

    # --------------------------------------------------
    # Only now load the untouched test set.
    # --------------------------------------------------

    heuristic_test = _read_csv(
        HEURISTIC_TEST_PATH
    )

    behavioural_test = _read_csv(
        BEHAVIOURAL_TEST_PATH
    )

    _validate_identical_population(
        heuristic_test,
        behavioural_test,
    )

    (
        heuristic_test,
        behavioural_test,
    ) = _align_test_data(
        heuristic_test,
        behavioural_test,
    )

    print()

    print(
        f"Common test records: "
        f"{len(heuristic_test)}"
    )

    print(
        "Unique test domains: "
        f"{heuristic_test['registrable_domain'].nunique()}"
    )

    print(
        "Legitimate records: "
        f"{int((heuristic_test['binary_label'] == 0).sum())}"
    )

    print(
        "Scam records: "
        f"{int((heuristic_test['binary_label'] == 1).sum())}"
    )

    # --------------------------------------------------
    # Prepare model matrices.
    # --------------------------------------------------

    x_h = prepare_h(
        heuristic_test,

        rf_h_bundle[
            "selected_features"
        ],

        rf_h_bundle[
            "training_medians"
        ],
    )

    x_b = prepare_b(
        behavioural_test,

        rf_b_bundle[
            "selected_features"
        ],

        rf_b_bundle[
            "training_medians"
        ],
    )

    y_test = heuristic_test[
        "binary_label"
    ].astype(int).values

    # --------------------------------------------------
    # Produce test probabilities exactly once.
    # --------------------------------------------------

    p_h = probability_h(
        rf_h_bundle[
            "estimator"
        ],
        x_h,
    )

    p_b = probability_b(
        rf_b_bundle[
            "estimator"
        ],
        x_b,
    )

    p_hybrid = fuse_probabilities(
        p_h,
        p_b,
        alpha=alpha,
    )

    if np.isnan(
        p_hybrid
    ).any():

        raise ValueError(
            (
                "Missing hybrid test "
                "probabilities detected. "
                "Principal Phase 21 comparison "
                "requires complete evidence."
            )
        )

    # --------------------------------------------------
    # Predictions.
    # --------------------------------------------------

    pred_h = (
        predictions_from_threshold(
            p_h,
            heuristic_threshold,
        )
    )

    pred_b = (
        predictions_from_threshold(
            p_b,
            behavioural_threshold,
        )
    )

    pred_hybrid = (
        predictions_from_threshold(
            p_hybrid,
            hybrid_threshold,
        )
    )

    # --------------------------------------------------
    # Formal metrics.
    # --------------------------------------------------

    result_h = evaluate_configuration(
        configuration="Heuristic-only",
        y_true=y_test,
        probabilities=p_h,
        threshold=heuristic_threshold,
    )

    result_b = evaluate_configuration(
        configuration="Behavioural-only",
        y_true=y_test,
        probabilities=p_b,
        threshold=behavioural_threshold,
    )

    result_hybrid = (
        evaluate_configuration(
            configuration="Hybrid",
            y_true=y_test,
            probabilities=p_hybrid,
            threshold=hybrid_threshold,
        )
    )

    metrics = pd.DataFrame(
        [
            _metric_row(
                result_h
            ),

            _metric_row(
                result_b
            ),

            _metric_row(
                result_hybrid
            ),
        ]
    )

    metrics.to_csv(
        METRICS_OUTPUT,
        index=False,
    )

    # --------------------------------------------------
    # Confusion matrices.
    # --------------------------------------------------

    confusion_rows = []

    for result in [
        result_h,
        result_b,
        result_hybrid,
    ]:

        confusion_rows.extend(
            [
                {
                    "configuration":
                        result.configuration,
                    "actual":
                        "legitimate",
                    "predicted":
                        "legitimate",
                    "count":
                        result.true_negative,
                },
                {
                    "configuration":
                        result.configuration,
                    "actual":
                        "legitimate",
                    "predicted":
                        "scam",
                    "count":
                        result.false_positive,
                },
                {
                    "configuration":
                        result.configuration,
                    "actual":
                        "scam",
                    "predicted":
                        "legitimate",
                    "count":
                        result.false_negative,
                },
                {
                    "configuration":
                        result.configuration,
                    "actual":
                        "scam",
                    "predicted":
                        "scam",
                    "count":
                        result.true_positive,
                },
            ]
        )

    pd.DataFrame(
        confusion_rows
    ).to_csv(
        CONFUSION_OUTPUT,
        index=False,
    )

    # --------------------------------------------------
    # Per-category recall.
    # --------------------------------------------------

    if (
        "scam_category"
        not in heuristic_test.columns
    ):

        raise ValueError(
            (
                "scam_category is required "
                "for per-category recall."
            )
        )

    category_results = pd.concat(
        [
            category_recall_table(
                y_test,
                pred_h,
                heuristic_test[
                    "scam_category"
                ].values,
                "Heuristic-only",
            ),

            category_recall_table(
                y_test,
                pred_b,
                heuristic_test[
                    "scam_category"
                ].values,
                "Behavioural-only",
            ),

            category_recall_table(
                y_test,
                pred_hybrid,
                heuristic_test[
                    "scam_category"
                ].values,
                "Hybrid",
            ),
        ],
        ignore_index=True,
    )

    category_results.to_csv(
        CATEGORY_OUTPUT,
        index=False,
    )

    # --------------------------------------------------
    # Save row-level test predictions.
    # --------------------------------------------------

    prediction_output = pd.DataFrame(
        {
            "url":
                heuristic_test[
                    "url"
                ],

            "registrable_domain":
                heuristic_test[
                    "registrable_domain"
                ],

            "binary_label":
                y_test,

            "scam_category":
                heuristic_test[
                    "scam_category"
                ],

            "source":
                (
                    heuristic_test[
                        "source"
                    ]
                    if "source"
                    in heuristic_test.columns
                    else ""
                ),

            "rf_h_probability":
                p_h,

            "rf_h_prediction":
                pred_h,

            "rf_b_probability":
                p_b,

            "rf_b_prediction":
                pred_b,

            "hybrid_probability":
                p_hybrid,

            "hybrid_prediction":
                pred_hybrid,
        }
    )

    prediction_output.to_csv(
        PREDICTIONS_OUTPUT,
        index=False,
    )

    # --------------------------------------------------
    # Model-stage response-time experiment.
    # --------------------------------------------------

    def run_h():

        x = prepare_h(
            heuristic_test,

            rf_h_bundle[
                "selected_features"
            ],

            rf_h_bundle[
                "training_medians"
            ],
        )

        probability_h(
            rf_h_bundle[
                "estimator"
            ],
            x,
        )

    def run_b():

        x = prepare_b(
            behavioural_test,

            rf_b_bundle[
                "selected_features"
            ],

            rf_b_bundle[
                "training_medians"
            ],
        )

        probability_b(
            rf_b_bundle[
                "estimator"
            ],
            x,
        )

    def run_hybrid():

        h = prepare_h(
            heuristic_test,

            rf_h_bundle[
                "selected_features"
            ],

            rf_h_bundle[
                "training_medians"
            ],
        )

        b = prepare_b(
            behavioural_test,

            rf_b_bundle[
                "selected_features"
            ],

            rf_b_bundle[
                "training_medians"
            ],
        )

        p1 = probability_h(
            rf_h_bundle[
                "estimator"
            ],
            h,
        )

        p2 = probability_b(
            rf_b_bundle[
                "estimator"
            ],
            b,
        )

        fuse_probabilities(
            p1,
            p2,
            alpha=alpha,
        )

    timing_rows = []

    for (
        name,
        function,
    ) in [
        (
            "Heuristic-only",
            run_h,
        ),
        (
            "Behavioural-only",
            run_b,
        ),
        (
            "Hybrid",
            run_hybrid,
        ),
    ]:

        timing = (
            time_callable_per_record_ms(
                function=function,

                number_of_records=len(
                    heuristic_test
                ),

                repeats=10,
            )
        )

        timing_rows.append(
            {
                "configuration":
                    name,

                "timing_scope":
                    (
                        "model inference and "
                        "feature preparation only"
                    ),

                **timing,
            }
        )

    timing_dataframe = pd.DataFrame(
        timing_rows
    )

    timing_dataframe.to_csv(
        RESPONSE_TIME_OUTPUT,
        index=False,
    )

    # --------------------------------------------------
    # Human-readable terminal output.
    # --------------------------------------------------

    print()

    print(
        "FINAL TEST-SET RESULTS"
    )

    print(
        "=" * 72
    )

    display_columns = [
        "configuration",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "false_positive_rate",
        "false_negative_rate",
    ]

    print(
        metrics[
            display_columns
        ].to_string(
            index=False
        )
    )

    print()

    print(
        "CONFUSION MATRICES"
    )

    print(
        "-" * 72
    )

    for result in [
        result_h,
        result_b,
        result_hybrid,
    ]:

        print(
            result.configuration
        )

        print(
            (
                f"TN={result.true_negative}  "
                f"FP={result.false_positive}"
            )
        )

        print(
            (
                f"FN={result.false_negative}  "
                f"TP={result.true_positive}"
            )
        )

        print()

    print(
        "SCAM-CATEGORY RECALL"
    )

    print(
        "-" * 72
    )

    print(
        category_results.to_string(
            index=False
        )
    )

    print()

    print(
        "MODEL-STAGE RESPONSE TIME"
    )

    print(
        "-" * 72
    )

    print(
        timing_dataframe.to_string(
            index=False
        )
    )

    # --------------------------------------------------
    # Summary JSON.
    # --------------------------------------------------

    summary_payload = {
        "test_sample_count":
            int(
                len(
                    heuristic_test
                )
            ),

        "unique_test_domains":
            int(
                heuristic_test[
                    "registrable_domain"
                ].nunique()
            ),

        "legitimate_test_count":
            int(
                (
                    y_test
                    == 0
                ).sum()
            ),

        "scam_test_count":
            int(
                (
                    y_test
                    == 1
                ).sum()
            ),

        "thresholds": {
            "rf_h":
                heuristic_threshold,

            "rf_b":
                behavioural_threshold,

            "hybrid":
                hybrid_threshold,
        },

        "hybrid_alpha":
            alpha,

        "metrics":
            metrics.to_dict(
                orient="records"
            ),

        "response_time_scope":
            (
                "Feature preparation and "
                "model inference only; "
                "full end-to-end timing "
                "is evaluated separately."
            ),
    }

    SUMMARY_OUTPUT.write_text(
        json.dumps(
            summary_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Reproducibility manifest.
    # --------------------------------------------------

    manifest_lines = [
        "PHASE 21 EXPERIMENTAL EVALUATION MANIFEST",
        "=" * 72,

        (
            "Principal comparison: "
            "RF-H vs RF-B vs Hybrid"
        ),

        (
            "Common test observations: "
            f"{len(heuristic_test)}"
        ),

        (
            "Unique test domains: "
            f"{heuristic_test['registrable_domain'].nunique()}"
        ),

        (
            "RF-H threshold: "
            f"{heuristic_threshold:.8f}"
        ),

        (
            "RF-B threshold: "
            f"{behavioural_threshold:.8f}"
        ),

        (
            "Hybrid alpha: "
            f"{alpha:.8f}"
        ),

        (
            "Hybrid threshold: "
            f"{hybrid_threshold:.8f}"
        ),

        "",
        (
            "RF-H/RF-B threshold source: "
            "validation only"
        ),

        (
            "Hybrid alpha/threshold source: "
            "validation only"
        ),

        (
            "Test set used for parameter "
            "selection: NO"
        ),

        (
            "Test set used for final "
            "evaluation: YES"
        ),

        "",
        (
            "RF-H model SHA256: "
            f"{_sha256(HEURISTIC_MODEL_PATH)}"
        ),

        (
            "RF-B model SHA256: "
            f"{_sha256(BEHAVIOURAL_MODEL_PATH)}"
        ),

        (
            "Hybrid config SHA256: "
            f"{_sha256(HYBRID_CONFIG_PATH)}"
        ),

        (
            "Heuristic test SHA256: "
            f"{_sha256(HEURISTIC_TEST_PATH)}"
        ),

        (
            "Behavioural test SHA256: "
            f"{_sha256(BEHAVIOURAL_TEST_PATH)}"
        ),

        "",
        (
            "Response-time scope: "
            "feature preparation and "
            "machine-learning inference only."
        ),

        (
            "Full website collection and "
            "browser-execution timing is "
            "reserved for later end-to-end "
            "performance testing."
        ),
    ]

    MANIFEST_OUTPUT.write_text(
        "\n".join(
            manifest_lines
        ),
        encoding="utf-8",
    )

    print()

    print(
        "=" * 72
    )

    print(
        "PHASE 21 COMPLETE"
    )

    print(
        "=" * 72
    )

    print(
        f"Metrics: {METRICS_OUTPUT}"
    )

    print(
        f"Predictions: {PREDICTIONS_OUTPUT}"
    )

    print(
        f"Category recall: {CATEGORY_OUTPUT}"
    )

    print(
        f"Response time: {RESPONSE_TIME_OUTPUT}"
    )

    print(
        f"Summary: {SUMMARY_OUTPUT}"
    )

    print(
        f"Manifest: {MANIFEST_OUTPUT}"
    )


if __name__ == "__main__":
    main()