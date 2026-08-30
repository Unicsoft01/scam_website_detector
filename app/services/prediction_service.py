from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd

from app.ml.model_loader import (
    RuntimeModels,
    get_runtime_models,
    validate_input_feature_order,
)


@dataclass
class PredictionOutput:
    configuration: str
    probability: float
    threshold: float
    predicted_label: int
    response_time_ms: float


def _class_name(
    label: int,
) -> str:

    return (
        "Scam Website"
        if label == 1
        else "Legitimate Website"
    )


def _validate_probability(
    probability: float,
) -> float:

    probability = float(
        probability
    )

    if not np.isfinite(
        probability
    ):

        raise ValueError(
            "Model returned a non-finite probability."
        )

    if not (
        0.0 <= probability <= 1.0
    ):

        raise ValueError(
            (
                "Model probability is outside "
                "[0, 1]."
            )
        )

    return probability


def _scam_class_index(
    estimator: Any,
) -> int:

    classes = list(
        estimator.classes_
    )

    if 1 not in classes:

        raise ValueError(
            (
                "The fitted classifier does not "
                "contain scam class label 1."
            )
        )

    return classes.index(
        1
    )


def _prepare_feature_frame(
    feature_data: dict,
    expected_features: list[str],
    training_medians: dict,
) -> pd.DataFrame:

    if not isinstance(
        feature_data,
        dict,
    ):

        raise TypeError(
            "feature_data must be a dictionary."
        )

    frame = pd.DataFrame(
        [
            feature_data
        ]
    )

    frame = validate_input_feature_order(
        frame,
        expected_features,
    )

    for feature in expected_features:

        frame[feature] = pd.to_numeric(
            frame[feature],
            errors="coerce",
        )

    frame = frame.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    missing_medians = [
        feature
        for feature in expected_features
        if feature not in training_medians
    ]

    if missing_medians:

        raise ValueError(
            (
                "Training medians are missing "
                "for runtime features: "
                f"{missing_medians}"
            )
        )

    median_series = pd.Series(
        {
            feature: training_medians[
                feature
            ]
            for feature in expected_features
        }
    )

    frame = frame.fillna(
        median_series
    )

    unresolved = [
        feature
        for feature in expected_features
        if frame[feature].isna().any()
    ]

    if unresolved:

        raise ValueError(
            (
                "Runtime preprocessing could not "
                "resolve missing values for: "
                f"{unresolved}"
            )
        )

    return frame


class PredictionService:

    def __init__(
        self,
        model_version: str = "1.0.0",
    ):

        self.models: RuntimeModels = (
            get_runtime_models(
                model_version
            )
        )

    @property
    def model_version(
        self,
    ) -> str:

        return self.models.version

    def predict_heuristic(
        self,
        feature_data: dict,
    ) -> PredictionOutput:

        if (
            self.models.heuristic_threshold
            is None
        ):

            raise ValueError(
                (
                    "No frozen RF-H threshold "
                    "is available in the "
                    "runtime package."
                )
            )

        start = perf_counter()

        X = _prepare_feature_frame(
            feature_data=feature_data,
            expected_features=(
                self.models
                .heuristic_features
            ),
            training_medians=(
                self.models
                .heuristic_medians
            ),
        )

        class_index = _scam_class_index(
            self.models.heuristic_model
        )

        probability = (
            self.models
            .heuristic_model
            .predict_proba(
                X
            )[0][class_index]
        )

        probability = (
            _validate_probability(
                probability
            )
        )

        threshold = float(
            self.models
            .heuristic_threshold
        )

        label = int(
            probability
            >= threshold
        )

        elapsed_ms = (
            perf_counter()
            - start
        ) * 1000.0

        return PredictionOutput(
            configuration="heuristic",
            probability=probability,
            threshold=threshold,
            predicted_label=label,
            response_time_ms=elapsed_ms,
        )

    def predict_behavioural(
        self,
        feature_data: dict,
    ) -> PredictionOutput:

        if (
            self.models.behavioural_threshold
            is None
        ):

            raise ValueError(
                (
                    "No frozen RF-B threshold "
                    "is available in the "
                    "runtime package."
                )
            )

        start = perf_counter()

        X = _prepare_feature_frame(
            feature_data=feature_data,
            expected_features=(
                self.models
                .behavioural_features
            ),
            training_medians=(
                self.models
                .behavioural_medians
            ),
        )

        class_index = _scam_class_index(
            self.models.behavioural_model
        )

        probability = (
            self.models
            .behavioural_model
            .predict_proba(
                X
            )[0][class_index]
        )

        probability = (
            _validate_probability(
                probability
            )
        )

        threshold = float(
            self.models
            .behavioural_threshold
        )

        label = int(
            probability
            >= threshold
        )

        elapsed_ms = (
            perf_counter()
            - start
        ) * 1000.0

        return PredictionOutput(
            configuration="behavioural",
            probability=probability,
            threshold=threshold,
            predicted_label=label,
            response_time_ms=elapsed_ms,
        )

    def fuse(
        self,
        heuristic_probability: float,
        behavioural_probability: float,
    ) -> PredictionOutput:

        start = perf_counter()

        p_h = _validate_probability(
            heuristic_probability
        )

        p_b = _validate_probability(
            behavioural_probability
        )

        alpha = float(
            self.models.alpha
        )

        probability = (
            alpha * p_h
            + (1.0 - alpha) * p_b
        )

        probability = (
            _validate_probability(
                probability
            )
        )

        threshold = float(
            self.models.hybrid_threshold
        )

        label = int(
            probability
            >= threshold
        )

        elapsed_ms = (
            perf_counter()
            - start
        ) * 1000.0

        return PredictionOutput(
            configuration="hybrid",
            probability=probability,
            threshold=threshold,
            predicted_label=label,
            response_time_ms=elapsed_ms,
        )


def prediction_class_name(
    label: int,
) -> str:

    return _class_name(
        label
    )