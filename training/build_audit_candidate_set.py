import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path(
    "data/processed/master_url_index.csv"
)

DEFAULT_OUTPUT = Path(
    "data/interim/live_audit_candidates.csv"
)

DEFAULT_SEED = 42


REQUIRED_COLUMNS = {
    "url",
    "registrable_domain",
    "source",
    "binary_label",
    "scam_category",
}


def _read_input(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():

        raise FileNotFoundError(
            f"Input dataset not found: {path}"
        )

    dataframe = pd.read_csv(
        path
    )

    if dataframe.empty:

        raise ValueError(
            "Input dataset contains no rows."
        )

    missing = (
        REQUIRED_COLUMNS
        - set(
            dataframe.columns
        )
    )

    if missing:

        raise ValueError(
            (
                "Missing required columns: "
                f"{sorted(missing)}"
            )
        )

    return dataframe


def _clean_candidates(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    dataframe = (
        dataframe
        .dropna(
            subset=[
                "url",
                "registrable_domain",
                "binary_label",
                "scam_category",
                "source",
            ]
        )
        .copy()
    )

    dataframe[
        "binary_label"
    ] = pd.to_numeric(
        dataframe[
            "binary_label"
        ],
        errors="raise",
    ).astype(int)

    valid_labels = set(
        dataframe[
            "binary_label"
        ].unique()
    )

    if not valid_labels.issubset(
        {
            0,
            1,
        }
    ):

        raise ValueError(
            (
                "Invalid binary labels found: "
                f"{sorted(valid_labels)}"
            )
        )

    # Exact URL duplicates must not receive
    # multiple opportunities to enter the audit.
    dataframe = (
        dataframe
        .drop_duplicates(
            subset=[
                "url"
            ],
            keep="first",
        )
    )

    return dataframe


def _sample_category(
    dataframe: pd.DataFrame,
    category: str,
    amount: int,
    seed: int,
) -> pd.DataFrame:

    subset = dataframe[
        dataframe[
            "scam_category"
        ]
        == category
    ].copy()

    if subset.empty:

        return subset

    # Shuffle before domain deduplication so
    # the same source ordering is not preserved.
    subset = subset.sample(
        frac=1.0,
        random_state=seed,
    )

    # Principal experimental unit should be
    # registrable domain.
    subset = subset.drop_duplicates(
        subset=[
            "registrable_domain"
        ],
        keep="first",
    )

    amount = min(
        amount,
        len(subset),
    )

    return (
        subset
        .head(
            amount
        )
        .copy()
    )


def _interleave_categories(
    frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Interleave category samples so even an audit
    stopped early is not dominated by one category.
    """

    rows = []

    maximum = max(
        (
            len(frame)
            for frame in frames.values()
        ),
        default=0,
    )

    ordered_categories = [
        "legitimate",
        "phishing",
        "online_shopping",
        "investment",
        "cryptocurrency",
        "technical_support",
    ]

    for position in range(
        maximum
    ):

        for category in ordered_categories:

            frame = frames.get(
                category
            )

            if frame is None:
                continue

            if position >= len(
                frame
            ):
                continue

            rows.append(
                frame.iloc[
                    position
                ]
                .to_dict()
            )

    return pd.DataFrame(
        rows
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--per-category",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
    )

    args = parser.parse_args()

    if args.per_category < 1:

        raise ValueError(
            "--per-category must be at least 1."
        )

    dataframe = _read_input(
        args.input
    )

    dataframe = _clean_candidates(
        dataframe
    )

    categories = [
        "legitimate",
        "phishing",
        "online_shopping",
        "investment",
        "cryptocurrency",
        "technical_support",
    ]

    sampled = {}

    for index, category in enumerate(
        categories
    ):

        sampled[
            category
        ] = _sample_category(
            dataframe=dataframe,
            category=category,
            amount=args.per_category,
            seed=(
                args.seed
                + index
            ),
        )

    candidates = (
        _interleave_categories(
            sampled
        )
    )

    if candidates.empty:

        raise ValueError(
            "No audit candidates were produced."
        )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates.to_csv(
        args.output,
        index=False,
    )

    print()

    print(
        "BALANCED LIVE-AUDIT CANDIDATE SET"
    )

    print(
        "=" * 72
    )

    print(
        f"Candidate rows: {len(candidates)}"
    )

    print(
        "Unique domains: "
        f"{candidates['registrable_domain'].nunique()}"
    )

    print()

    print(
        "BY LABEL"
    )

    print(
        candidates[
            "binary_label"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print()

    print(
        "BY CATEGORY"
    )

    print(
        candidates[
            "scam_category"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print()

    print(
        "BY SOURCE"
    )

    print(
        candidates[
            "source"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print()

    print(
        "CATEGORY x SOURCE"
    )

    print(
        pd.crosstab(
            candidates[
                "scam_category"
            ],
            candidates[
                "source"
            ],
        ).to_string()
    )

    print()

    print(
        f"Saved to: {args.output}"
    )


if __name__ == "__main__":
    main()