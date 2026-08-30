import numpy as np
import pandas as pd
import pytest

from app.services.prediction_service import (
    _prepare_feature_frame,
)


def test_runtime_feature_order():

    features = {
        "h_c": 3,
        "h_a": 1,
        "h_b": 2,
    }

    expected = [
        "h_a",
        "h_b",
        "h_c",
    ]

    medians = {
        "h_a": 10,
        "h_b": 20,
        "h_c": 30,
    }

    frame = _prepare_feature_frame(
        feature_data=features,
        expected_features=expected,
        training_medians=medians,
    )

    assert list(
        frame.columns
    ) == expected


def test_runtime_missing_value_uses_training_median():

    features = {
        "h_a": 1,
        "h_b": None,
    }

    medians = {
        "h_a": 10,
        "h_b": 25,
    }

    frame = _prepare_feature_frame(
        feature_data=features,

        expected_features=[
            "h_a",
            "h_b",
        ],

        training_medians=medians,
    )

    assert frame.loc[
        0,
        "h_b",
    ] == 25


def test_missing_required_feature_rejected():

    features = {
        "h_a": 1
    }

    medians = {
        "h_a": 10,
        "h_b": 20,
    }

    with pytest.raises(
        ValueError
    ):

        _prepare_feature_frame(
            feature_data=features,

            expected_features=[
                "h_a",
                "h_b",
            ],

            training_medians=medians,
        )


def test_infinity_uses_training_median():

    features = {
        "h_a": np.inf
    }

    medians = {
        "h_a": 5
    }

    frame = _prepare_feature_frame(
        feature_data=features,
        expected_features=["h_a"],
        training_medians=medians,
    )

    assert frame.loc[
        0,
        "h_a",
    ] == 5