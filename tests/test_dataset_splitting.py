import pandas as pd
import pytest

from app.ml.splitting import (
    create_grouped_split,
    validate_no_domain_leakage,
)


def _make_dataset():

    rows = []

    # Enough domains for grouped splitting.
    for index in range(
        40
    ):

        label = (
            index
            % 2
        )

        if label == 0:

            category = (
                "legitimate"
            )

        else:

            scam_categories = [
                "phishing",
                "online_shopping",
                "investment",
                "cryptocurrency",
                "technical_support",
            ]

            category = (
                scam_categories[
                    index
                    % len(
                        scam_categories
                    )
                ]
            )

        source_options = [
            "phishtank",
            "scamferret",
            "mendeley",
        ]

        source = (
            source_options[
                index
                % len(
                    source_options
                )
            ]
        )

        domain = (
            f"domain{index}.example"
        )

        rows.append(
            {
                "url":
                    f"https://{domain}/",

                "registrable_domain":
                    domain,

                "binary_label":
                    label,

                "scam_category":
                    category,

                "source":
                    source,
            }
        )

    return pd.DataFrame(
        rows
    )


def test_grouped_split_has_three_sets():

    dataframe = (
        _make_dataset()
    )

    result = (
        create_grouped_split(
            dataframe,
            candidate_seeds=100,
        )
    )

    splits = set(
        result.assignments[
            "split"
        ]
    )

    assert splits == {
        "training",
        "validation",
        "testing",
    }


def test_no_domain_leakage():

    dataframe = (
        _make_dataset()
    )

    result = (
        create_grouped_split(
            dataframe,
            candidate_seeds=100,
        )
    )

    assignments = (
        result.assignments
    )

    train = assignments[
        assignments[
            "split"
        ]
        == "training"
    ]

    validation = assignments[
        assignments[
            "split"
        ]
        == "validation"
    ]

    test = assignments[
        assignments[
            "split"
        ]
        == "testing"
    ]

    validate_no_domain_leakage(
        train,
        validation,
        test,
    )

    train_domains = set(
        train[
            "registrable_domain"
        ]
    )

    validation_domains = set(
        validation[
            "registrable_domain"
        ]
    )

    test_domains = set(
        test[
            "registrable_domain"
        ]
    )

    assert not (
        train_domains
        & validation_domains
    )

    assert not (
        train_domains
        & test_domains
    )

    assert not (
        validation_domains
        & test_domains
    )


def test_all_records_are_assigned():

    dataframe = (
        _make_dataset()
    )

    result = (
        create_grouped_split(
            dataframe,
            candidate_seeds=100,
        )
    )

    assert len(
        result.assignments
    ) == len(
        dataframe
    )


def test_split_is_reproducible():

    dataframe = (
        _make_dataset()
    )

    first = (
        create_grouped_split(
            dataframe,
            candidate_seeds=100,
        )
    )

    second = (
        create_grouped_split(
            dataframe,
            candidate_seeds=100,
        )
    )

    first_mapping = (
        first.assignments[
            [
                "url",
                "split",
            ]
        ]
        .sort_values(
            "url"
        )
        .reset_index(
            drop=True
        )
    )

    second_mapping = (
        second.assignments[
            [
                "url",
                "split",
            ]
        ]
        .sort_values(
            "url"
        )
        .reset_index(
            drop=True
        )
    )

    pd.testing.assert_frame_equal(
        first_mapping,
        second_mapping,
    )


def test_duplicate_urls_rejected():

    dataframe = (
        _make_dataset()
    )

    duplicate = (
        dataframe.iloc[
            [0]
        ]
        .copy()
    )

    dataframe = pd.concat(
        [
            dataframe,
            duplicate,
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError
    ):

        create_grouped_split(
            dataframe,
            candidate_seeds=50,
        )


def test_too_few_domains_rejected():

    dataframe = pd.DataFrame(
        {
            "url": [
                "https://a.example/1",
                "https://b.example/1",
                "https://c.example/1",
            ],

            "registrable_domain": [
                "a.example",
                "b.example",
                "c.example",
            ],

            "binary_label": [
                0,
                1,
                0,
            ],

            "scam_category": [
                "legitimate",
                "phishing",
                "legitimate",
            ],

            "source": [
                "source1",
                "source2",
                "source1",
            ],
        }
    )

    with pytest.raises(
        ValueError
    ):

        create_grouped_split(
            dataframe
        )