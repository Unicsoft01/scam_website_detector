import numpy as np
import pandas as pd
import pytest

from app.ml.behavioural_model import (
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
            "b_redirect_count": [
                0,
                0,
                0,
                1,
                0,
                4,
                5,
                3,
                6,
                4,
            ],

            "b_dom_mutation_count": [
                1,
                2,
                0,
                1,
                2,
                20,
                25,
                18,
                30,
                22,
            ],

            "b_popup_count": [
                0,
                0,
                0,
                0,
                0,
                2,
                1,
                3,
                2,
                4,
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
            "b_redirect_count": [
                0,
                None,
            ],

            "b_popup_count": [
                0,
                2,
            ],
        }
    )

    result = (
        prepare_selected_features(
            dataframe=dataframe,

            selected_features=[
                "b_redirect_count",
                "b_popup_count",
            ],

            training_medians={
                "b_redirect_count": 1.0,
                "b_popup_count": 0.0,
            },
        )
    )

    assert (
        result.loc[
            1,
            "b_redirect_count"
        ]
        == 1.0
    )

    assert not (
        result
        .isna()
        .any()
        .any()
    )


def test_missing_behavioural_feature_rejected():

    dataframe = pd.DataFrame(
        {
            "b_popup_count": [
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
                "b_popup_count",
                "b_redirect_count",
            ],

            training_medians={
                "b_popup_count": 0.0,
                "b_redirect_count": 1.0,
            },
        )


def test_single_class_labels_rejected():

    labels = pd.Series(
        [
            1,
            1,
            1,
        ]
    )

    with pytest.raises(
        ValueError
    ):

        validate_training_labels(
            labels
        )


def test_probability_output():

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
            0.30,
            0.70,
            0.95,
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
    ) == len(
        x.columns
    )

    assert set(
        table[
            "feature"
        ]
    ) == set(
        x.columns
    )

    assert (
        table[
            "rank"
        ].iloc[0]
        == 1
    )


def test_invalid_probability_threshold():

    y_true = pd.Series(
        [
            0,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.1,
            0.9,
        ]
    )

    with pytest.raises(
        ValueError
    ):

        evaluate_validation(
            y_true,
            probabilities,
            threshold=1.5,
        )