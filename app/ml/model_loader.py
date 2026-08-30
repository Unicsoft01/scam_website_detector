import json
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


DEFAULT_MODEL_VERSION = "1.0.0"

DEFAULT_RUNTIME_ROOT = Path(
    "models/runtime"
)


@dataclass
class RuntimeModels:
    version: str

    heuristic_bundle: dict
    behavioural_bundle: dict
    hybrid_config: dict
    manifest: dict

    heuristic_model: Any
    behavioural_model: Any

    heuristic_features: list[str]
    behavioural_features: list[str]

    heuristic_medians: dict[str, float]
    behavioural_medians: dict[str, float]

    alpha: float
    hybrid_threshold: float

    heuristic_threshold: float | None
    behavioural_threshold: float | None


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


def _require_file(
    path: Path,
) -> None:

    if not path.exists():

        raise FileNotFoundError(
            f"Runtime model file missing: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Expected a file: {path}"
        )

    if path.stat().st_size == 0:

        raise ValueError(
            f"Runtime model file is empty: {path}"
        )


def _read_json(
    path: Path,
) -> dict:

    _require_file(
        path
    )

    try:

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            (
                "Invalid JSON in runtime "
                f"artefact: {path}"
            )
        ) from error

    if not isinstance(
        payload,
        dict,
    ):

        raise ValueError(
            (
                "Runtime JSON artefact must "
                f"contain an object: {path}"
            )
        )

    return payload


def _validate_feature_list(
    features,
    name: str,
) -> list[str]:

    if not isinstance(
        features,
        list,
    ):

        raise ValueError(
            f"{name} must be a list."
        )

    if not features:

        raise ValueError(
            f"{name} cannot be empty."
        )

    if not all(
        isinstance(
            feature,
            str,
        )
        and feature.strip()
        for feature in features
    ):

        raise ValueError(
            (
                f"{name} contains an invalid "
                "feature name."
            )
        )

    if len(
        features
    ) != len(
        set(
            features
        )
    ):

        raise ValueError(
            f"{name} contains duplicates."
        )

    return list(
        features
    )


def validate_input_feature_order(
    dataframe: pd.DataFrame,
    expected_features: list[str],
) -> pd.DataFrame:
    """
    Return the model input columns in exactly
    the order stored during training.

    Extra metadata columns are ignored.
    Missing required features are rejected.
    """

    missing = [
        feature
        for feature in expected_features
        if feature
        not in dataframe.columns
    ]

    if missing:

        raise ValueError(
            (
                "Runtime input is missing "
                "required model features: "
                f"{missing}"
            )
        )

    return dataframe.loc[
        :,
        expected_features
    ].copy()


def _validate_hash(
    package_directory: Path,
    manifest: dict,
    filename: str,
) -> None:

    hashes = manifest.get(
        "sha256",
        {},
    )

    expected = hashes.get(
        filename
    )

    if not expected:

        raise ValueError(
            (
                "No SHA256 value stored for "
                f"{filename}."
            )
        )

    path = (
        package_directory
        / filename
    )

    actual = sha256_file(
        path
    )

    if actual != expected:

        raise ValueError(
            (
                "Runtime artefact integrity "
                f"check failed for {filename}."
            )
        )


def load_runtime_models(
    version: str = DEFAULT_MODEL_VERSION,
    runtime_root: Path = DEFAULT_RUNTIME_ROOT,
) -> RuntimeModels:

    package_directory = (
        runtime_root
        / f"v{version}"
    )

    manifest_path = (
        package_directory
        / "model_manifest.json"
    )

    heuristic_path = (
        package_directory
        / "rf_heuristic.joblib"
    )

    behavioural_path = (
        package_directory
        / "rf_behavioural.joblib"
    )

    hybrid_path = (
        package_directory
        / "hybrid_fusion_config.json"
    )

    heuristic_features_path = (
        package_directory
        / "heuristic_features.json"
    )

    behavioural_features_path = (
        package_directory
        / "behavioural_features.json"
    )

    for path in [
        manifest_path,
        heuristic_path,
        behavioural_path,
        hybrid_path,
        heuristic_features_path,
        behavioural_features_path,
    ]:

        _require_file(
            path
        )

    manifest = _read_json(
        manifest_path
    )

    if manifest.get(
        "model_version"
    ) != version:

        raise ValueError(
            (
                "Requested runtime version "
                "does not match manifest. "
                f"Requested={version}, "
                "manifest="
                f"{manifest.get('model_version')}"
            )
        )

    for filename in [
        "rf_heuristic.joblib",
        "rf_behavioural.joblib",
        "hybrid_fusion_config.json",
        "heuristic_features.json",
        "behavioural_features.json",
    ]:

        _validate_hash(
            package_directory,
            manifest,
            filename,
        )

    heuristic_bundle = joblib.load(
        heuristic_path
    )

    behavioural_bundle = joblib.load(
        behavioural_path
    )

    hybrid_config = _read_json(
        hybrid_path
    )

    heuristic_feature_payload = (
        _read_json(
            heuristic_features_path
        )
    )

    behavioural_feature_payload = (
        _read_json(
            behavioural_features_path
        )
    )

    heuristic_features = (
        _validate_feature_list(
            heuristic_feature_payload.get(
                "selected_features"
            ),
            "heuristic selected features",
        )
    )

    behavioural_features = (
        _validate_feature_list(
            behavioural_feature_payload.get(
                "selected_features"
            ),
            "behavioural selected features",
        )
    )

    if heuristic_bundle.get(
        "selected_features"
    ) != heuristic_features:

        raise ValueError(
            (
                "Heuristic feature list differs "
                "from the RF-H model bundle."
            )
        )

    if behavioural_bundle.get(
        "selected_features"
    ) != behavioural_features:

        raise ValueError(
            (
                "Behavioural feature list differs "
                "from the RF-B model bundle."
            )
        )

    heuristic_model = (
        heuristic_bundle.get(
            "estimator"
        )
    )

    behavioural_model = (
        behavioural_bundle.get(
            "estimator"
        )
    )

    if heuristic_model is None:

        raise ValueError(
            (
                "RF-H estimator missing from "
                "runtime model bundle."
            )
        )

    if behavioural_model is None:

        raise ValueError(
            (
                "RF-B estimator missing from "
                "runtime model bundle."
            )
        )

    heuristic_medians = (
        heuristic_bundle.get(
            "training_medians"
        )
    )

    behavioural_medians = (
        behavioural_bundle.get(
            "training_medians"
        )
    )

    if not isinstance(
        heuristic_medians,
        dict,
    ):

        raise ValueError(
            (
                "RF-H training medians are "
                "missing or invalid."
            )
        )

    if not isinstance(
        behavioural_medians,
        dict,
    ):

        raise ValueError(
            (
                "RF-B training medians are "
                "missing or invalid."
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

    if not (
        0.0 <= alpha <= 1.0
    ):

        raise ValueError(
            "Hybrid alpha is outside [0, 1]."
        )

    if not (
        0.0
        <= hybrid_threshold
        <= 1.0
    ):

        raise ValueError(
            (
                "Hybrid classification "
                "threshold is outside [0, 1]."
            )
        )

    thresholds = manifest.get(
        "classification_thresholds",
        {},
    )

    heuristic_threshold = (
        thresholds.get(
            "heuristic"
        )
    )

    behavioural_threshold = (
        thresholds.get(
            "behavioural"
        )
    )

    if heuristic_threshold is not None:

        heuristic_threshold = float(
            heuristic_threshold
        )

    if behavioural_threshold is not None:

        behavioural_threshold = float(
            behavioural_threshold
        )

    return RuntimeModels(
        version=version,

        heuristic_bundle=(
            heuristic_bundle
        ),

        behavioural_bundle=(
            behavioural_bundle
        ),

        hybrid_config=(
            hybrid_config
        ),

        manifest=manifest,

        heuristic_model=(
            heuristic_model
        ),

        behavioural_model=(
            behavioural_model
        ),

        heuristic_features=(
            heuristic_features
        ),

        behavioural_features=(
            behavioural_features
        ),

        heuristic_medians=(
            heuristic_medians
        ),

        behavioural_medians=(
            behavioural_medians
        ),

        alpha=alpha,

        hybrid_threshold=(
            hybrid_threshold
        ),

        heuristic_threshold=(
            heuristic_threshold
        ),

        behavioural_threshold=(
            behavioural_threshold
        ),
    )


@lru_cache(
    maxsize=4
)
def get_runtime_models(
    version: str = DEFAULT_MODEL_VERSION,
) -> RuntimeModels:
    """
    Cached application loader.

    The first call loads the files from disk.
    Later calls return the already-loaded
    runtime models from memory.
    """

    return load_runtime_models(
        version=version
    )


def clear_runtime_model_cache() -> None:
    """
    Mainly useful for tests or controlled
    model-version changes.
    """

    get_runtime_models.cache_clear()