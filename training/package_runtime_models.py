import argparse
import json
import shutil
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import joblib


SOURCE_RF_H = Path(
    "models/rf_heuristic.joblib"
)

SOURCE_RF_B = Path(
    "models/rf_behavioural.joblib"
)

SOURCE_HYBRID = Path(
    "models/hybrid_fusion_config.json"
)

PHASE21_THRESHOLDS = Path(
    "data/processed/evaluation/"
    "baseline_thresholds.json"
)

PHASE21_SUMMARY = Path(
    "data/processed/evaluation/"
    "experimental_summary.json"
)


def sha256_file(
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


def require_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Required artefact missing: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Expected file: {path}"
        )

    if path.stat().st_size == 0:

        raise ValueError(
            f"Artefact is empty: {path}"
        )


def read_json(
    path: Path,
) -> dict:

    require_file(
        path
    )

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            (
                "Invalid JSON file: "
                f"{path}"
            )
        ) from error


def iso_file_mtime(
    path: Path,
) -> str:
    """
    This is the filesystem modification
    timestamp of the artefact.

    It is NOT silently claimed to be an
    exact model training timestamp.
    """

    timestamp = (
        path
        .stat()
        .st_mtime
    )

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).isoformat()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Package approved scam-detection "
            "models for runtime use."
        )
    )

    parser.add_argument(
        "--version",
        default="1.0.0",
        help=(
            "Runtime model version. "
            "Default: 1.0.0"
        ),
    )

    args = parser.parse_args()

    version = (
        args.version
        .strip()
    )

    if not version:

        raise ValueError(
            "Model version cannot be empty."
        )

    print()

    print(
        "PHASE 22 — MODEL PACKAGING "
        "AND RUNTIME LOADER"
    )

    print(
        "=" * 72
    )

    for path in [
        SOURCE_RF_H,
        SOURCE_RF_B,
        SOURCE_HYBRID,
        PHASE21_THRESHOLDS,
        PHASE21_SUMMARY,
    ]:

        require_file(
            path
        )

    # --------------------------------------------------
    # Load approved artefacts.
    # --------------------------------------------------

    rf_h_bundle = joblib.load(
        SOURCE_RF_H
    )

    rf_b_bundle = joblib.load(
        SOURCE_RF_B
    )

    hybrid_config = read_json(
        SOURCE_HYBRID
    )

    thresholds = read_json(
        PHASE21_THRESHOLDS
    )

    evaluation_summary = read_json(
        PHASE21_SUMMARY
    )

    # --------------------------------------------------
    # Basic validation.
    # --------------------------------------------------

    if rf_h_bundle.get(
        "model_name"
    ) != "RF-H":

        raise ValueError(
            (
                "Unexpected heuristic "
                "model identity."
            )
        )

    if rf_b_bundle.get(
        "model_name"
    ) != "RF-B":

        raise ValueError(
            (
                "Unexpected behavioural "
                "model identity."
            )
        )

    heuristic_features = (
        rf_h_bundle.get(
            "selected_features"
        )
    )

    behavioural_features = (
        rf_b_bundle.get(
            "selected_features"
        )
    )

    if not heuristic_features:

        raise ValueError(
            (
                "RF-H selected feature list "
                "is missing or empty."
            )
        )

    if not behavioural_features:

        raise ValueError(
            (
                "RF-B selected feature list "
                "is missing or empty."
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

    # Make sure the Phase 21 frozen
    # configuration agrees with Phase 20.
    phase21_alpha = float(
        thresholds[
            "hybrid_alpha"
        ]
    )

    phase21_hybrid_threshold = float(
        thresholds[
            "hybrid_threshold"
        ]
    )

    if abs(
        alpha
        - phase21_alpha
    ) > 1e-12:

        raise ValueError(
            (
                "Hybrid alpha differs between "
                "Phase 20 and Phase 21."
            )
        )

    if abs(
        hybrid_threshold
        - phase21_hybrid_threshold
    ) > 1e-12:

        raise ValueError(
            (
                "Hybrid threshold differs "
                "between Phase 20 and Phase 21."
            )
        )

    # --------------------------------------------------
    # Create versioned package.
    # --------------------------------------------------

    package_directory = Path(
        "models/runtime"
    ) / f"v{version}"

    if package_directory.exists():

        raise FileExistsError(
            (
                "Runtime model package already "
                f"exists: {package_directory}\n"
                "Do not silently overwrite an "
                "approved model version. Use a "
                "new version number if the "
                "model changes."
            )
        )

    package_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    heuristic_destination = (
        package_directory
        / "rf_heuristic.joblib"
    )

    behavioural_destination = (
        package_directory
        / "rf_behavioural.joblib"
    )

    hybrid_destination = (
        package_directory
        / "hybrid_fusion_config.json"
    )

    shutil.copy2(
        SOURCE_RF_H,
        heuristic_destination,
    )

    shutil.copy2(
        SOURCE_RF_B,
        behavioural_destination,
    )

    shutil.copy2(
        SOURCE_HYBRID,
        hybrid_destination,
    )

    # --------------------------------------------------
    # Save explicit feature definitions.
    # --------------------------------------------------

    heuristic_feature_payload = {
        "model":
            "RF-H",

        "model_version":
            version,

        "feature_count":
            len(
                heuristic_features
            ),

        "selected_features":
            heuristic_features,

        "expected_input_order":
            heuristic_features,
    }

    behavioural_feature_payload = {
        "model":
            "RF-B",

        "model_version":
            version,

        "feature_count":
            len(
                behavioural_features
            ),

        "selected_features":
            behavioural_features,

        "expected_input_order":
            behavioural_features,
    }

    heuristic_features_path = (
        package_directory
        / "heuristic_features.json"
    )

    behavioural_features_path = (
        package_directory
        / "behavioural_features.json"
    )

    heuristic_features_path.write_text(
        json.dumps(
            heuristic_feature_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    behavioural_features_path.write_text(
        json.dumps(
            behavioural_feature_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Determine model timestamps.
    # --------------------------------------------------

    rf_h_trained_at = (
        rf_h_bundle.get(
            "trained_at_utc"
        )
    )

    rf_b_trained_at = (
        rf_b_bundle.get(
            "trained_at_utc"
        )
    )

    # Earlier Phase 18/19 bundles may not
    # contain explicit training timestamps.
    # We record that transparently rather
    # than inventing a value.
    rf_h_time_source = (
        "model_bundle"
        if rf_h_trained_at
        else "not_recorded"
    )

    rf_b_time_source = (
        "model_bundle"
        if rf_b_trained_at
        else "not_recorded"
    )

    # --------------------------------------------------
    # Package metadata.
    # --------------------------------------------------

    packaged_at = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    manifest = {
        "model_version":
            version,

        "system":
            (
                "Real-Time Scam Website "
                "Detection System"
            ),

        "package_status":
            "approved_runtime_models",

        "packaged_at_utc":
            packaged_at,

        "target": {
            "name":
                "binary_label",

            "legitimate":
                0,

            "scam":
                1,
        },

        "heuristic_model": {
            "name":
                "RF-H",

            "classifier_family":
                "RandomForestClassifier",

            "file":
                "rf_heuristic.joblib",

            "selected_feature_count":
                len(
                    heuristic_features
                ),

            "expected_input_feature_order":
                heuristic_features,

            "trained_at_utc":
                rf_h_trained_at,

            "training_timestamp_source":
                rf_h_time_source,

            "artefact_modified_at_utc":
                iso_file_mtime(
                    SOURCE_RF_H
                ),

            "random_state":
                rf_h_bundle.get(
                    "random_state"
                ),

            "best_parameters":
                rf_h_bundle.get(
                    "best_parameters"
                ),
        },

        "behavioural_model": {
            "name":
                "RF-B",

            "classifier_family":
                "RandomForestClassifier",

            "file":
                "rf_behavioural.joblib",

            "selected_feature_count":
                len(
                    behavioural_features
                ),

            "expected_input_feature_order":
                behavioural_features,

            "trained_at_utc":
                rf_b_trained_at,

            "training_timestamp_source":
                rf_b_time_source,

            "artefact_modified_at_utc":
                iso_file_mtime(
                    SOURCE_RF_B
                ),

            "random_state":
                rf_b_bundle.get(
                    "random_state"
                ),

            "best_parameters":
                rf_b_bundle.get(
                    "best_parameters"
                ),
        },

        "hybrid": {
            "method":
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
                hybrid_threshold,

            "missing_behaviour_policy":
                hybrid_config.get(
                    "missing_behaviour_policy"
                ),
        },

        "classification_thresholds": {
            "heuristic":
                thresholds.get(
                    "rf_h_threshold"
                ),

            "behavioural":
                thresholds.get(
                    "rf_b_threshold"
                ),

            "hybrid":
                hybrid_threshold,
        },

        "evaluation": {
            "test_sample_count":
                evaluation_summary.get(
                    "test_sample_count"
                ),

            "unique_test_domains":
                evaluation_summary.get(
                    "unique_test_domains"
                ),

            "legitimate_test_count":
                evaluation_summary.get(
                    "legitimate_test_count"
                ),

            "scam_test_count":
                evaluation_summary.get(
                    "scam_test_count"
                ),

            "final_metrics":
                evaluation_summary.get(
                    "metrics"
                ),
        },

        "runtime_policy": {
            "load_models_once":
                True,

            "retrain_per_scan":
                False,

            "preserve_feature_order":
                True,

            "missing_behaviour_as_zero":
                False,

            "primary_decision":
                "hybrid_when_complete",

            "fallback":
                (
                    "explicitly labelled "
                    "heuristic fallback"
                ),
        },
    }

    # --------------------------------------------------
    # Hash package artefacts before writing
    # manifest.
    # --------------------------------------------------

    manifest[
        "sha256"
    ] = {
        "rf_heuristic.joblib":
            sha256_file(
                heuristic_destination
            ),

        "rf_behavioural.joblib":
            sha256_file(
                behavioural_destination
            ),

        "hybrid_fusion_config.json":
            sha256_file(
                hybrid_destination
            ),

        "heuristic_features.json":
            sha256_file(
                heuristic_features_path
            ),

        "behavioural_features.json":
            sha256_file(
                behavioural_features_path
            ),
    }

    manifest_path = (
        package_directory
        / "model_manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Model version: {version}"
    )

    print(
        (
            "Heuristic features: "
            f"{len(heuristic_features)}"
        )
    )

    print(
        (
            "Behavioural features: "
            f"{len(behavioural_features)}"
        )
    )

    print(
        f"Hybrid alpha: {alpha:.4f}"
    )

    print(
        (
            "Hybrid threshold: "
            f"{hybrid_threshold:.4f}"
        )
    )

    print()

    if rf_h_trained_at is None:

        print(
            (
                "RF-H exact training timestamp "
                "was not stored by the earlier "
                "training bundle."
            )
        )

    if rf_b_trained_at is None:

        print(
            (
                "RF-B exact training timestamp "
                "was not stored by the earlier "
                "training bundle."
            )
        )

    print()

    print(
        "Runtime package created:"
    )

    print(
        package_directory
    )

    print()

    print(
        "Files:"
    )

    for path in sorted(
        package_directory.iterdir()
    ):

        print(
            f"  {path.name}"
        )

    print()

    print(
        "=" * 72
    )

    print(
        "PHASE 22 PACKAGING COMPLETE"
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()