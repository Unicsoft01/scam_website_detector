from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    GroupShuffleSplit,
)


TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15

DEFAULT_RANDOM_SEED = 42

CANDIDATE_SEEDS = 500


@dataclass
class SplitResult:
    assignments: pd.DataFrame
    score: float
    random_seed: int


def validate_split_input(
    dataframe: pd.DataFrame,
) -> None:

    required = {
        "url",
        "registrable_domain",
        "binary_label",
        "scam_category",
        "source",
    }

    missing = (
        required
        - set(
            dataframe.columns
        )
    )

    if missing:
        raise ValueError(
            (
                "Split dataset is missing "
                "required columns: "
                f"{sorted(missing)}"
            )
        )

    if dataframe.empty:
        raise ValueError(
            "Split dataset contains no rows."
        )

    if dataframe[
        "url"
    ].isna().any():

        raise ValueError(
            "URL contains missing values."
        )

    if dataframe[
        "registrable_domain"
    ].isna().any():

        raise ValueError(
            (
                "registrable_domain contains "
                "missing values."
            )
        )

    if dataframe[
        "binary_label"
    ].isna().any():

        raise ValueError(
            "binary_label contains missing values."
        )

    labels = set(
        pd.to_numeric(
            dataframe[
                "binary_label"
            ],
            errors="raise",
        )
        .astype(int)
        .unique()
    )

    if not labels.issubset(
        {
            0,
            1,
        }
    ):
        raise ValueError(
            (
                "binary_label must contain "
                "only 0 and 1."
            )
        )

    if dataframe[
        "url"
    ].duplicated().any():

        raise ValueError(
            (
                "Duplicate URLs exist before "
                "dataset splitting."
            )
        )


def _distribution(
    dataframe: pd.DataFrame,
    column: str,
    universe: Iterable,
) -> pd.Series:

    if dataframe.empty:

        return pd.Series(
            0.0,
            index=list(
                universe
            ),
        )

    result = (
        dataframe[
            column
        ]
        .value_counts(
            normalize=True,
            dropna=False,
        )
        .reindex(
            list(
                universe
            ),
            fill_value=0.0,
        )
    )

    return result.astype(
        float
    )


def _distribution_distance(
    subset: pd.DataFrame,
    full: pd.DataFrame,
    column: str,
) -> float:

    universe = sorted(
        set(
            full[
                column
            ]
            .astype(str)
        )
    )

    full_series = (
        full[
            column
        ]
        .astype(str)
    )

    subset_series = (
        subset[
            column
        ]
        .astype(str)
    )

    full_temp = pd.DataFrame(
        {
            column:
                full_series
        }
    )

    subset_temp = pd.DataFrame(
        {
            column:
                subset_series
        }
    )

    expected = _distribution(
        full_temp,
        column,
        universe,
    )

    observed = _distribution(
        subset_temp,
        column,
        universe,
    )

    return float(
        np.abs(
            expected
            - observed
        ).sum()
    )


def _size_penalty(
    actual_size: int,
    total_size: int,
    target_ratio: float,
) -> float:

    if total_size == 0:
        return float(
            "inf"
        )

    actual_ratio = (
        actual_size
        / total_size
    )

    return abs(
        actual_ratio
        - target_ratio
    )


def _score_candidate(
    full: pd.DataFrame,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> float:
    """
    Smaller is better.

    The score uses metadata distributions only.
    Model predictions are never involved.
    """

    score = 0.0

    # -----------------------------------------
    # Split-size deviation
    # -----------------------------------------

    score += (
        _size_penalty(
            len(train),
            len(full),
            TRAIN_RATIO,
        )
        * 4.0
    )

    score += (
        _size_penalty(
            len(validation),
            len(full),
            VALIDATION_RATIO,
        )
        * 4.0
    )

    score += (
        _size_penalty(
            len(test),
            len(full),
            TEST_RATIO,
        )
        * 4.0
    )

    # -----------------------------------------
    # Label balance
    # -----------------------------------------

    for subset in (
        train,
        validation,
        test,
    ):

        score += (
            _distribution_distance(
                subset,
                full,
                "binary_label",
            )
            * 3.0
        )

        # Scam-category balance.
        score += (
            _distribution_distance(
                subset,
                full,
                "scam_category",
            )
            * 1.5
        )

        # Dataset-source balance.
        score += (
            _distribution_distance(
                subset,
                full,
                "source",
            )
            * 1.0
        )

    return float(
        score
    )


def _domain_overlap(
    first: pd.DataFrame,
    second: pd.DataFrame,
) -> set[str]:

    return (
        set(
            first[
                "registrable_domain"
            ].astype(str)
        )
        &
        set(
            second[
                "registrable_domain"
            ].astype(str)
        )
    )


def validate_no_domain_leakage(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
) -> None:

    train_validation = (
        _domain_overlap(
            train,
            validation,
        )
    )

    train_test = (
        _domain_overlap(
            train,
            test,
        )
    )

    validation_test = (
        _domain_overlap(
            validation,
            test,
        )
    )

    if (
        train_validation
        or train_test
        or validation_test
    ):

        raise ValueError(
            (
                "Registrable-domain leakage "
                "detected between splits."
            )
        )


def _contains_both_labels(
    dataframe: pd.DataFrame,
) -> bool:

    return set(
        dataframe[
            "binary_label"
        ]
        .astype(int)
        .unique()
    ) == {
        0,
        1,
    }


def create_grouped_split(
    dataframe: pd.DataFrame,
    candidate_seeds: int = (
        CANDIDATE_SEEDS
    ),
) -> SplitResult:

    validate_split_input(
        dataframe
    )

    dataframe = (
        dataframe
        .reset_index(
            drop=True
        )
        .copy()
    )

    groups = dataframe[
        "registrable_domain"
    ].astype(str)

    unique_domains = (
        groups.nunique()
    )

    if unique_domains < 6:

        raise ValueError(
            (
                "Too few unique registrable "
                "domains for a defensible "
                "70/15/15 grouped split. "
                f"Found only {unique_domains}."
            )
        )

    best = None

    # -----------------------------------------
    # Generate deterministic candidate splits.
    # -----------------------------------------

    for seed in range(
        DEFAULT_RANDOM_SEED,
        DEFAULT_RANDOM_SEED
        + candidate_seeds,
    ):

        first_split = (
            GroupShuffleSplit(
                n_splits=1,

                train_size=(
                    TRAIN_RATIO
                ),

                random_state=(
                    seed
                ),
            )
        )

        (
            train_indices,
            temporary_indices,
        ) = next(
            first_split.split(
                dataframe,
                groups=groups,
            )
        )

        train = dataframe.iloc[
            train_indices
        ].copy()

        temporary = dataframe.iloc[
            temporary_indices
        ].copy()

        temporary_groups = (
            temporary[
                "registrable_domain"
            ]
            .astype(str)
        )

        # Remaining 30% is divided equally:
        # 15% validation + 15% test.
        second_split = (
            GroupShuffleSplit(
                n_splits=1,

                train_size=0.50,

                random_state=(
                    seed
                    + 10_000
                ),
            )
        )

        (
            validation_indices,
            test_indices,
        ) = next(
            second_split.split(
                temporary,

                groups=(
                    temporary_groups
                ),
            )
        )

        validation = (
            temporary.iloc[
                validation_indices
            ]
            .copy()
        )

        test = (
            temporary.iloc[
                test_indices
            ]
            .copy()
        )

        # -------------------------------------
        # Basic validity requirements
        # -------------------------------------

        if (
            train.empty
            or validation.empty
            or test.empty
        ):
            continue

        # Where enough data exist, every split
        # should contain both legitimate and
        # scam examples.
        if not (
            _contains_both_labels(
                train
            )
            and _contains_both_labels(
                validation
            )
            and _contains_both_labels(
                test
            )
        ):
            continue

        try:
            validate_no_domain_leakage(
                train,
                validation,
                test,
            )

        except ValueError:
            continue

        score = _score_candidate(
            dataframe,
            train,
            validation,
            test,
        )

        if (
            best is None
            or score
            < best[
                "score"
            ]
        ):

            best = {
                "score":
                    score,

                "seed":
                    seed,

                "train":
                    train,

                "validation":
                    validation,

                "test":
                    test,
            }

    if best is None:

        raise ValueError(
            (
                "Unable to create a valid "
                "domain-grouped split. "
                "The current dataset may be "
                "too small or too imbalanced."
            )
        )

    train = best[
        "train"
    ].copy()

    validation = best[
        "validation"
    ].copy()

    test = best[
        "test"
    ].copy()

    train[
        "split"
    ] = "training"

    validation[
        "split"
    ] = "validation"

    test[
        "split"
    ] = "testing"

    assignments = pd.concat(
        [
            train,
            validation,
            test,
        ],
        ignore_index=True,
    )

    validate_no_domain_leakage(
        assignments[
            assignments[
                "split"
            ]
            == "training"
        ],

        assignments[
            assignments[
                "split"
            ]
            == "validation"
        ],

        assignments[
            assignments[
                "split"
            ]
            == "testing"
        ],
    )

    return SplitResult(
        assignments=(
            assignments
        ),

        score=float(
            best[
                "score"
            ]
        ),

        random_seed=int(
            best[
                "seed"
            ]
        ),
    )