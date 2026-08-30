import json
from pathlib import Path

import pandas as pd
import pytest

from app.ml.model_loader import (
    validate_input_feature_order,
)


def test_feature_order_is_preserved():

    dataframe = pd.DataFrame(
        {
            "metadata": [
                "test"
            ],

            "h_feature_c": [
                3
            ],

            "h_feature_a": [
                1
            ],

            "h_feature_b": [
                2
            ],
        }
    )

    expected = [
        "h_feature_a",
        "h_feature_b",
        "h_feature_c",
    ]

    result = (
        validate_input_feature_order(
            dataframe,
            expected,
        )
    )

    assert list(
        result.columns
    ) == expected


def test_extra_columns_are_ignored():

    dataframe = pd.DataFrame(
        {
            "h_a": [
                1
            ],

            "h_b": [
                2
            ],

            "url": [
                "https://example.com"
            ],

            "source": [
                "test"
            ],
        }
    )

    result = (
        validate_input_feature_order(
            dataframe,
            [
                "h_a",
                "h_b",
            ],
        )
    )

    assert list(
        result.columns
    ) == [
        "h_a",
        "h_b",
    ]


def test_missing_required_feature_rejected():

    dataframe = pd.DataFrame(
        {
            "h_a": [
                1
            ]
        }
    )

    with pytest.raises(
        ValueError
    ):

        validate_input_feature_order(
            dataframe,
            [
                "h_a",
                "h_b",
            ],
        )