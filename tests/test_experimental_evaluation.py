import numpy as np
import pandas as pd
import pytest

from app.ml.evaluation import (
    calibrate_single_model_threshold,
    category_recall_table,
    choose_baseline_threshold,
    evaluate_configuration,
    predictions_from_threshold,
    time_callable_per_record_ms,
)


def test_perfect_evaluation():

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

    result = evaluate_configuration(
        configuration="test",
        y_true=y,
        probabilities=probabilities,
        threshold=0.5,
    )

    assert result.accuracy == 1.0
    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.f1 == 1.0
    assert result.false_positive_rate == 0.0
    assert result.false_negative_rate == 0.0
    assert result.true_negative == 2
    assert result.true_positive == 2


def test_threshold_predictions():

    probabilities = np.array(
        [
            0.2,
            0.49,
            0.50,
            0.8,
        ]
    )

    predictions = (
        predictions_from_threshold(
            probabilities,
            threshold=0.5,
        )
    )

    assert predictions.tolist() == [
        0,
        0,
        1,
        1,
    ]


def test_invalid_probability_rejected():

    with pytest.raises(
        ValueError
    ):

        evaluate_configuration(
            configuration="test",
            y_true=[
                0,
                1,
            ],
            probabilities=[
                0.2,
                1.5,
            ],
            threshold=0.5,
        )


def test_threshold_calibration():

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
            0.3,
            0.6,
            0.9,
        ]
    )

    calibration = (
        calibrate_single_model_threshold(
            y_true=y,
            probabilities=probabilities,
            threshold_values=[
                0.4,
                0.5,
                0.6,
            ],
        )
    )

    assert len(
        calibration
    ) == 3

    threshold = (
        choose_baseline_threshold(
            calibration
        )
    )

    assert threshold in [
        0.4,
        0.5,
        0.6,
    ]


def test_category_recall():

    labels = np.array(
        [
            1,
            1,
            1,
            1,
        ]
    )

    predictions = np.array(
        [
            1,
            0,
            1,
            1,
        ]
    )

    categories = np.array(
        [
            "phishing",
            "phishing",
            "investment",
            "investment",
        ]
    )

    result = category_recall_table(
        labels=labels,
        predictions=predictions,
        categories=categories,
        configuration="Hybrid",
    )

    phishing = result[
        result[
            "scam_category"
        ] == "phishing"
    ].iloc[0]

    investment = result[
        result[
            "scam_category"
        ] == "investment"
    ].iloc[0]

    assert (
        phishing[
            "support"
        ]
        == 2
    )

    assert (
        phishing[
            "recall"
        ]
        == 0.5
    )

    assert (
        investment[
            "recall"
        ]
        == 1.0
    )


def test_missing_category_returns_nan():

    labels = np.array(
        [
            1,
            1,
        ]
    )

    predictions = np.array(
        [
            1,
            1,
        ]
    )

    categories = np.array(
        [
            "phishing",
            "phishing",
        ]
    )

    result = category_recall_table(
        labels,
        predictions,
        categories,
        "Hybrid",
    )

    crypto = result[
        result[
            "scam_category"
        ] == "cryptocurrency"
    ].iloc[0]

    assert (
        crypto[
            "support"
        ]
        == 0
    )

    assert np.isnan(
        crypto[
            "recall"
        ]
    )


def test_response_time_function():

    def simple_function():
        return sum(
            range(
                100
            )
        )

    result = (
        time_callable_per_record_ms(
            simple_function,
            number_of_records=10,
            repeats=3,
        )
    )

    assert (
        result[
            "mean_ms_per_record"
        ]
        >= 0
    )

    assert (
        result[
            "repeats"
        ]
        == 3
    )