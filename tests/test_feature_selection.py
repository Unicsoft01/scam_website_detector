import numpy as np
import pandas as pd
import pytest

from app.ml.feature_selection import (
    build_candidate_counts,
    calculate_mi_ranking,
    choose_best_candidate,
    get_feature_columns,
    prepare_train_validation_features,
)


def _training_data():

    return pd.DataFrame(
        {
            "url": [
                f"https://train{i}.example"
                for i in range(20)
            ],

            "binary_label": [
                0,
                1,
            ] * 10,

            "h_signal": [
                0,
                10,
            ] * 10,

            "h_noise": [
                1,
                5,
                2,
                4,
                3,
            ] * 4,

            "h_missing": [
                1,
                None,
            ] * 10,

            "b_popup_count": [
                0,
                1,
            ] * 10,
        }
    )


def _validation_data():

    return pd.DataFrame(
        {
            "url": [
                f"https://validation{i}.example"
                for i in range(10)
            ],

            "binary_label": [
                0,
                1,
            ] * 5,

            "h_signal": [
                0,
                10,
            ] * 5,

            "h_noise": [
                2,
                4,
                1,
                5,
                3,
            ] * 2,

            "h_missing": [
                None,
                1,
            ] * 5,

            "b_popup_count": [
                0,
                1,
            ] * 5,
        }
    )


def test_get_heuristic_columns():

    dataframe = (
        _training_data()
    )

    features = (
        get_feature_columns(
            dataframe,
            "heuristic",
        )
    )

    assert set(
        features
    ) == {
        "h_signal",
        "h_noise",
        "h_missing",
    }


def test_get_behavioural_columns():

    dataframe = (
        _training_data()
    )

    features = (
        get_feature_columns(
            dataframe,
            "behavioural",
        )
    )

    assert features == [
        "b_popup_count"
    ]


def test_training_median_used_for_validation():

    train = (
        _training_data()
    )

    validation = (
        _validation_data()
    )

    prepared = (
        prepare_train_validation_features(
            train,
            validation,
            "heuristic",
        )
    )

    expected = float(
        pd.to_numeric(
            train[
                "h_missing"
            ]
        ).median()
    )

    assert (
        prepared.medians[
            "h_missing"
        ]
        == expected
    )

    assert not (
        prepared.x_train
        .isna()
        .any()
        .any()
    )

    assert not (
        prepared.x_validation
        .isna()
        .any()
        .any()
    )


def test_all_missing_training_feature_excluded():

    train = (
        _training_data()
    )

    validation = (
        _validation_data()
    )

    train[
        "h_all_missing"
    ] = np.nan

    validation[
        "h_all_missing"
    ] = 5

    prepared = (
        prepare_train_validation_features(
            train,
            validation,
            "heuristic",
        )
    )

    assert (
        "h_all_missing"
        in
        prepared.excluded_all_missing
    )

    assert (
        "h_all_missing"
        not in
        prepared.x_train.columns
    )


def test_mi_ranking_created():

    train = (
        _training_data()
    )

    validation = (
        _validation_data()
    )

    prepared = (
        prepare_train_validation_features(
            train,
            validation,
            "heuristic",
        )
    )

    ranking = (
        calculate_mi_ranking(
            prepared.x_train,
            prepared.y_train,
        )
    )

    assert len(
        ranking
    ) == prepared.x_train.shape[
        1
    ]

    assert ranking[
        "rank"
    ].iloc[0] == 1

    assert (
        ranking[
            "mutual_information"
        ]
        .isna()
        .sum()
        == 0
    )


def test_candidate_counts_do_not_exceed_features():

    counts = (
        build_candidate_counts(
            23
        )
    )

    assert max(
        counts
    ) <= 23

    assert 23 in counts


def test_choose_candidate_prefers_f1():

    dataframe = pd.DataFrame(
        {
            "feature_count": [
                5,
                10,
                15,
            ],

            "validation_f1": [
                0.70,
                0.85,
                0.80,
            ],

            "validation_recall": [
                0.80,
                0.83,
                0.90,
            ],
        }
    )

    result = (
        choose_best_candidate(
            dataframe
        )
    )

    assert result == 10


def test_tie_prefers_recall():

    dataframe = pd.DataFrame(
        {
            "feature_count": [
                5,
                10,
            ],

            "validation_f1": [
                0.85,
                0.85,
            ],

            "validation_recall": [
                0.80,
                0.90,
            ],
        }
    )

    result = (
        choose_best_candidate(
            dataframe
        )
    )

    assert result == 10


def test_equal_f1_recall_prefers_fewer():

    dataframe = pd.DataFrame(
        {
            "feature_count": [
                5,
                10,
            ],

            "validation_f1": [
                0.85,
                0.85,
            ],

            "validation_recall": [
                0.90,
                0.90,
            ],
        }
    )

    result = (
        choose_best_candidate(
            dataframe
        )
    )

    assert result == 5


def test_single_class_training_rejected():

    train = (
        _training_data()
    )

    validation = (
        _validation_data()
    )

    train[
        "binary_label"
    ] = 0

    with pytest.raises(
        ValueError
    ):

        prepare_train_validation_features(
            train,
            validation,
            "heuristic",
        )