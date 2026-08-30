import numpy as np
import pandas as pd
import pytest

from app.ml.heuristic_model import (
    build_random_forest,
    evaluate_validation,
    feature_importance_table,
    prepare_selected_features,
    scam_probability,
    validate_training_labels,
)


def _training_matrix():

    x = pd.DataFrame(
        {
            "h_signal": [
                0,
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                1,
                1,
            ],

            "h_length": [
                10,
                12,
                11,
                13,
                9,
                80,
                90,
                100,
                85,
                95,
            ],
        }
    )

    y = pd.Series(
        [
            0,
            0,
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
        ]
    )

    return x, y


def test_prepare_selected_features():

    dataframe = pd.DataFrame(
        {
            "h_signal": [
                0,
                1,
            ],

            "h_length": [
                None,
                90,
            ],
        }
    )

    result = (
        prepare_selected_features(
            dataframe=dataframe,

            selected_features=[
                "h_signal",
                "h_length",
            ],

            training_medians={
                "h_signal": 0.5,
                "h_length": 50.0,
            },
        )
    )

    assert (
        result.loc[
            0,
            "h_length"
        ]
        == 50.0
    )

    assert not (
        result
        .isna()
        .any()
        .any()
    )


def test_missing_required_feature_rejected():

    dataframe = pd.DataFrame(
        {
            "h_signal": [
                0,
                1,
            ]
        }
    )

    with pytest.raises(
        ValueError
    ):

        prepare_selected_features(
            dataframe=dataframe,

            selected_features=[
                "h_signal",
                "h_missing",
            ],

            training_medians={
                "h_signal": 0.5,
                "h_missing": 1.0,
            },
        )


def test_invalid_training_labels_rejected():

    labels = pd.Series(
        [
            0,
            0,
            0,
        ]
    )

    with pytest.raises(
        ValueError
    ):

        validate_training_labels(
            labels
        )


def test_random_forest_probability_output():

    x, y = (
        _training_matrix()
    )

    model = (
        build_random_forest(
            n_estimators=50
        )
    )

    model.fit(
        x,
        y,
    )

    probabilities = (
        scam_probability(
            model,
            x,
        )
    )

    assert len(
        probabilities
    ) == len(
        x
    )

    assert np.all(
        probabilities >= 0
    )

    assert np.all(
        probabilities <= 1
    )


def test_validation_metrics():

    y_true = pd.Series(
        [
            0,
            0,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.10,
            0.20,
            0.80,
            0.90,
        ]
    )

    result = (
        evaluate_validation(
            y_true,
            probabilities,
            threshold=0.50,
        )
    )

    assert (
        result.accuracy
        == 1.0
    )

    assert (
        result.precision
        == 1.0
    )

    assert (
        result.recall
        == 1.0
    )

    assert (
        result.f1
        == 1.0
    )


def test_feature_importance_table():

    x, y = (
        _training_matrix()
    )

    model = (
        build_random_forest(
            n_estimators=50
        )
    )

    model.fit(
        x,
        y,
    )

    table = (
        feature_importance_table(
            model,
            list(
                x.columns
            ),
        )
    )

    assert len(
        table
    ) == 2

    assert set(
        table[
            "feature"
        ]
    ) == {
        "h_signal",
        "h_length",
    }

    assert (
        table[
            "rank"
        ].iloc[0]
        == 1
    )