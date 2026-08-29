import numpy as np
import pandas as pd
import pytest

from app.ml.preprocessing import (
    clean_feature_column,
    get_feature_columns,
    remove_duplicate_urls,
    validate_binary_label,
)


def test_get_heuristic_features():

    dataframe = pd.DataFrame(
        {
            "url": [
                "https://example.com"
            ],

            "binary_label": [
                0
            ],

            "h_url_length": [
                20
            ],

            "h_dns_resolved": [
                1
            ],

            "b_popup_count": [
                0
            ],
        }
    )

    result = get_feature_columns(
        dataframe,
        "heuristic",
    )

    assert set(
        result
    ) == {
        "h_url_length",
        "h_dns_resolved",
    }


def test_get_behavioural_features():

    dataframe = pd.DataFrame(
        {
            "url": [
                "https://example.com"
            ],

            "binary_label": [
                0
            ],

            "h_url_length": [
                20
            ],

            "b_popup_count": [
                0
            ],
        }
    )

    result = get_feature_columns(
        dataframe,
        "behavioural",
    )

    assert result == [
        "b_popup_count"
    ]


def test_hybrid_features():

    dataframe = pd.DataFrame(
        {
            "url": [
                "https://example.com"
            ],

            "binary_label": [
                0
            ],

            "h_url_length": [
                20
            ],

            "b_popup_count": [
                0
            ],
        }
    )

    result = get_feature_columns(
        dataframe,
        "hybrid",
    )

    assert set(
        result
    ) == {
        "h_url_length",
        "b_popup_count",
    }


def test_valid_binary_labels():

    dataframe = pd.DataFrame(
        {
            "binary_label": [
                0,
                1,
                1,
                0,
            ]
        }
    )

    validate_binary_label(
        dataframe
    )

    assert set(
        dataframe[
            "binary_label"
        ]
    ) == {
        0,
        1,
    }


def test_invalid_binary_label():

    dataframe = pd.DataFrame(
        {
            "binary_label": [
                0,
                1,
                2,
            ]
        }
    )

    with pytest.raises(
        ValueError
    ):
        validate_binary_label(
            dataframe
        )


def test_missing_binary_label():

    dataframe = pd.DataFrame(
        {
            "binary_label": [
                0,
                None,
                1,
            ]
        }
    )

    with pytest.raises(
        ValueError
    ):
        validate_binary_label(
            dataframe
        )


def test_duplicate_urls_removed():

    dataframe = pd.DataFrame(
        {
            "url": [
                "https://example.com",
                "https://example.com",
                "https://openai.com",
            ],

            "binary_label": [
                0,
                0,
                0,
            ],
        }
    )

    cleaned, removed = (
        remove_duplicate_urls(
            dataframe
        )
    )

    assert len(
        cleaned
    ) == 2

    assert removed == 1


def test_conflicting_duplicate_labels_rejected():

    dataframe = pd.DataFrame(
        {
            "url": [
                "https://example.com",
                "https://example.com",
            ],

            "binary_label": [
                0,
                1,
            ],
        }
    )

    with pytest.raises(
        ValueError
    ):
        remove_duplicate_urls(
            dataframe
        )


def test_infinity_becomes_missing():

    dataframe = pd.DataFrame(
        {
            "h_test": [
                1.0,
                np.inf,
                -np.inf,
                3.0,
            ]
        }
    )

    diagnostic = (
        clean_feature_column(
            dataframe,
            "h_test",
        )
    )

    assert (
        dataframe[
            "h_test"
        ]
        .isna()
        .sum()
        == 2
    )

    assert (
        diagnostic
        .infinite_values_replaced
        == 2
    )


def test_non_numeric_value_becomes_missing():

    dataframe = pd.DataFrame(
        {
            "h_test": [
                "1",
                "unknown",
                "3",
            ]
        }
    )

    diagnostic = (
        clean_feature_column(
            dataframe,
            "h_test",
        )
    )

    assert (
        dataframe[
            "h_test"
        ]
        .isna()
        .sum()
        == 1
    )

    assert (
        diagnostic
        .non_numeric_values_coerced
        == 1
    )


def test_constant_feature_detected():

    dataframe = pd.DataFrame(
        {
            "h_test": [
                1,
                1,
                1,
                1,
            ]
        }
    )

    diagnostic = (
        clean_feature_column(
            dataframe,
            "h_test",
        )
    )

    assert (
        diagnostic.is_constant
        is True
    )


def test_high_missing_feature_detected():

    dataframe = pd.DataFrame(
        {
            "h_test": [
                1,
                None,
                None,
                None,
            ]
        }
    )

    diagnostic = (
        clean_feature_column(
            dataframe,
            "h_test",
        )
    )

    assert (
        diagnostic.is_highly_missing
        is True
    )