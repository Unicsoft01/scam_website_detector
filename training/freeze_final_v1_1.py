from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import shutil

import numpy
import pandas
import sklearn


MODEL_DIR = Path(
    "models/runtime/v1.1.0"
)

DATA_DIR = Path(
    "data/experiments/v1_1"
)

FREEZE_DIR = (
    DATA_DIR
    / "final_freeze"
)


def sha256(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for block in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def main():
    required = [
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

        MODEL_DIR
        / "evaluation_results.json",

        DATA_DIR
        / "final_dataset_split_manifest.csv",

        DATA_DIR
        / "final_test_predictions.csv",

        DATA_DIR
        / "final_model_comparison.csv",
    ]

    missing = [
        str(path)
        for path in required
        if not path.exists()
    ]

    if missing:
        print(
            "FREEZE ABORTED."
        )

        print(
            "\nMissing required files:"
        )

        for path in missing:
            print(
                " -",
                path,
            )

        raise RuntimeError(
            "Final evaluation package is incomplete."
        )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FREEZE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    split_file = (
        DATA_DIR
        / "final_dataset_split_manifest.csv"
    )

    shutil.copy2(
        split_file,
        MODEL_DIR
        / split_file.name,
    )

    artifacts = {}

    for path in required:
        artifacts[
            path.name
        ] = {
            "sha256": sha256(path),
            "size_bytes": (
                path.stat().st_size
            ),
        }

    manifest = {
        "model_version": "v1.1.0",
        "status": (
            "final_frozen_experimental_model"
        ),
        "frozen_at_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "binary_target": {
            "0": "legitimate",
            "1": "scam",
        },
        "models": {
            "heuristic": (
                "rf_heuristic.joblib"
            ),
            "behavioural": (
                "rf_behavioural.joblib"
            ),
        },
        "feature_files": {
            "heuristic": (
                "heuristic_features.json"
            ),
            "behavioural": (
                "behavioural_features.json"
            ),
        },
        "fusion_config": (
            "hybrid_fusion_config.json"
        ),
        "dataset_split": (
            "final_dataset_split_manifest.csv"
        ),
        "evaluation_results": (
            "evaluation_results.json"
        ),
        "test_data_used_once": True,
        "post_test_tuning_performed": (
            False
        ),
        "software": {
            "python": (
                platform.python_version()
            ),
            "scikit_learn": (
                sklearn.__version__
            ),
            "pandas": (
                pandas.__version__
            ),
            "numpy": (
                numpy.__version__
            ),
        },
        "artifacts": artifacts,
    }

    with open(
        MODEL_DIR
        / "model_manifest.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            manifest,
            file,
            indent=2,
        )

    freeze_text = """MODEL FREEZE RECORD

Version:
v1.1.0

Purpose:
Final experimental scam website detection model.

Frozen components:
- Selected heuristic feature set
- Selected behavioural feature set
- RF-H model
- RF-B model
- Hybrid alpha
- RF-H threshold
- RF-B threshold
- Hybrid threshold
- Domain-level train/validation/test split
- Runtime software environment
- Final evaluation results

Test-set policy:
The final test set was excluded from feature selection,
model fitting, alpha selection and threshold selection.

After examination of the final test results, no tuning
of v1.1.0 is permitted.

Any subsequent model development must use a new model
version and must not overwrite v1.1.0.
"""

    with open(
        MODEL_DIR
        / "FREEZE_RECORD.txt",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            freeze_text
        )

    backup_files = [
        DATA_DIR
        / "final_dataset_split_manifest.csv",

        DATA_DIR
        / "final_hybrid_test_dataset.csv",

        DATA_DIR
        / "final_test_predictions.csv",

        DATA_DIR
        / "final_model_comparison.csv",

        DATA_DIR
        / "final_category_performance.csv",
    ]

    phase33_files = [
        DATA_DIR
        / "performance_test_results.csv",

        DATA_DIR
        / "performance_test_summary.csv",
    ]

    for path in (
        backup_files
        + phase33_files
    ):
        if path.exists():
            shutil.copy2(
                path,
                FREEZE_DIR
                / path.name,
            )

    print(
        "\n================================"
    )
    print(
        "V1.1.0 FINAL FREEZE COMPLETE"
    )
    print(
        "================================"
    )

    print(
        "Model directory:",
        MODEL_DIR,
    )

    print(
        "Frozen evidence:",
        FREEZE_DIR,
    )

    print(
        "\nNo further tuning of v1.1.0 is permitted."
    )


if __name__ == "__main__":
    main()