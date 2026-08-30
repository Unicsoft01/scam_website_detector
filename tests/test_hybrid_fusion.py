import numpy as np
import pandas as pd
import pytest

from app.ml.hybrid_fusion import (
    calibrate_fusion,
    choose_best_fusion,
    classify_probabilities,
    evaluate_fusion,
    fuse_probabilities,
    production_decision,
)


def test_equal_weight_fusion():

    p_h = np.array(
        [
            0.8,
            0.2,
        ]
    )

    p_b = np.array(
        [
            0.6,
            0.4,
        ]
    )

    result = fuse_probabilities(
        p_h,
        p_b,
        alpha=0.5,
    )

    assert np.allclose(
        result,
        [
            0.7,
            0.3,
        ],
    )


def test_alpha_one_equals_heuristic():

    p_h = np.array(
        [
            0.8,
            0.2,
        ]
    )

    p_b = np.array(
        [
            0.1,
            0.9,
        ]
    )

    result = fuse_probabilities(
        p_h,
        p_b,
        alpha=1.0,
    )

    assert np.allclose(
        result,
        p_h,
    )


def test_alpha_zero_equals_behavioural():

    p_h = np.array(
        [
            0.8,
            0.2,
        ]
    )

    p_b = np.array(
        [
            0.1,
            0.9,
        ]
    )

    result = fuse_probabilities(
        p_h,
        p_b,
        alpha=0.0,
    )

    assert np.allclose(
        result,
        p_b,
    )


def test_missing_behaviour_remains_missing():

    p_h = np.array(
        [
            0.8,
            0.9,
        ]
    )

    p_b = np.array(
        [
            0.6,
            np.nan,
        ]
    )

    result = fuse_probabilities(
        p_h,
        p_b,
        alpha=0.5,
    )

    assert np.isclose(
        result[
            0
        ],
        0.7,
    )

    assert np.isnan(
        result[
            1
        ]
    )


def test_invalid_alpha_rejected():

    with pytest.raises(
        ValueError
    ):

        fuse_probabilities(
            [
                0.5,
            ],
            [
                0.5,
            ],
            alpha=1.5,
        )


def test_threshold_classification():

    probabilities = np.array(
        [
            0.2,
            0.49,
            0.50,
            0.8,
        ]
    )

    predictions = (
        classify_probabilities(
            probabilities,
            threshold=0.50,
        )
    )

    assert predictions.tolist() == [
        0,
        0,
        1,
        1,
    ]


def test_calibration_produces_results():

    y = np.array(
        [
            0,
            0,
            0,
            1,
            1,
            1,
        ]
    )

    p_h = np.array(
        [
            0.1,
            0.2,
            0.4,
            0.6,
            0.8,
            0.9,
        ]
    )

    p_b = np.array(
        [
            0.2,
            0.3,
            0.4,
            0.7,
            0.8,
            0.95,
        ]
    )

    results = calibrate_fusion(
        y,
        p_h,
        p_b,
        alpha_values=[
            0.0,
            0.5,
            1.0,
        ],
        threshold_values=[
            0.4,
            0.5,
            0.6,
        ],
    )

    assert len(
        results
    ) == 9

    assert {
        "alpha",
        "threshold",
        "f1",
    }.issubset(
        results.columns
    )


def test_choose_best_prefers_f1():

    dataframe = pd.DataFrame(
        {
            "alpha": [
                0.3,
                0.5,
            ],

            "threshold": [
                0.5,
                0.5,
            ],

            "f1": [
                0.70,
                0.90,
            ],

            "recall": [
                0.90,
                0.85,
            ],

            "false_positive_rate": [
                0.1,
                0.1,
            ],
        }
    )

    best = choose_best_fusion(
        dataframe
    )

    assert (
        float(
            best[
                "alpha"
            ]
        )
        == 0.5
    )


def test_evaluate_perfect_fusion():

    y = np.array(
        [
            0,
            0,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.1,
            0.2,
            0.8,
            0.9,
        ]
    )

    result = evaluate_fusion(
        y_true=y,

        hybrid_probability=(
            probabilities
        ),

        alpha=0.5,

        threshold=0.5,
    )

    assert (
        result.f1
        == 1.0
    )

    assert (
        result.false_positive_rate
        == 0.0
    )

    assert (
        result.false_negative_rate
        == 0.0
    )


def test_production_complete_hybrid():

    result = production_decision(
        heuristic_probability=0.8,
        behavioural_probability=0.6,
        alpha=0.5,
        threshold=0.5,
    )

    assert (
        result[
            "decision_mode"
        ]
        == "hybrid"
    )

    assert (
        result[
            "hybrid_available"
        ]
        is True
    )

    assert np.isclose(
        result[
            "hybrid_probability"
        ],
        0.7,
    )


def test_missing_behaviour_uses_explicit_fallback():

    result = production_decision(
        heuristic_probability=0.8,
        behavioural_probability=None,
        alpha=0.5,
        threshold=0.5,
    )

    assert (
        result[
            "decision_mode"
        ]
        == "heuristic_fallback"
    )

    assert (
        result[
            "hybrid_available"
        ]
        is False
    )

    assert (
        result[
            "behavioural_probability"
        ]
        is None
    )

    assert (
        result[
            "hybrid_probability"
        ]
        is None
    )