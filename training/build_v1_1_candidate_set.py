import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path(
    "data/processed/master_url_index.csv"
)

DEFAULT_OUTPUT = Path(
    "data/experiments/v1_1/candidates.csv"
)

DEFAULT_SEED = 42


CATEGORY_TARGETS = {
    "legitimate": 350,
    "phishing": 150,
    "online_shopping": 300,
    "investment": 200,
    "cryptocurrency": 160,
    "technical_support": 11,
}


REQUIRED_COLUMNS = {
    "url",
    "original_url",
    "registrable_domain",
    "source",
    "source_category",
    "binary_label",
    "scam_category",
    "original_label",
}


def read_master_dataset(
    path: Path,
) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Master dataset not found: {path}"
        )

    dataframe = pd.read_csv(path)

    if dataframe.empty:
        raise ValueError(
            "Master dataset is empty."
        )

    missing = REQUIRED_COLUMNS - set(
        dataframe.columns
    )

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    return dataframe


def clean_dataset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    dataframe = dataframe.dropna(
        subset=[
            "url",
            "registrable_domain",
            "source",
            "binary_label",
            "scam_category",
        ]
    ).copy()

    dataframe["binary_label"] = pd.to_numeric(
        dataframe["binary_label"],
        errors="raise",
    ).astype(int)

    if not set(
        dataframe["binary_label"].unique()
    ).issubset({0, 1}):

        raise ValueError(
            "binary_label must contain only 0 and 1."
        )

    dataframe = dataframe.drop_duplicates(
        subset=["url"],
        keep="first",
    )

    return dataframe


def sample_category(
    dataframe: pd.DataFrame,
    category: str,
    target: int,
    seed: int,
) -> pd.DataFrame:

    subset = dataframe[
        dataframe["scam_category"] == category
    ].copy()

    if subset.empty:
        print(
            f"{category}: no records available"
        )
        return subset

    # Randomise before selecting a representative
    # URL for each registrable domain.
    subset = subset.sample(
        frac=1.0,
        random_state=seed,
    )

    # Registrable domain is the principal
    # experimental unit.
    subset = subset.drop_duplicates(
        subset=["registrable_domain"],
        keep="first",
    )

    available = len(subset)

    amount = min(
        target,
        available,
    )

    sampled = subset.sample(
        n=amount,
        random_state=seed,
        replace=False,
    ).copy()

    print(
        f"{category}: "
        f"requested={target}, "
        f"available_domains={available}, "
        f"selected={len(sampled)}"
    )

    return sampled


def interleave_categories(
    category_frames: dict,
) -> pd.DataFrame:

    category_order = [
        "legitimate",
        "phishing",
        "online_shopping",
        "investment",
        "cryptocurrency",
        "technical_support",
    ]

    rows = []

    maximum = max(
        (
            len(frame)
            for frame in category_frames.values()
        ),
        default=0,
    )

    for position in range(maximum):

        for category in category_order:

            frame = category_frames.get(
                category
            )

            if frame is None:
                continue

            if position >= len(frame):
                continue

            rows.append(
                frame.iloc[position].to_dict()
            )

    return pd.DataFrame(rows)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Build the expanded v1.1 "
            "live-audit candidate dataset."
        )
    )

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
        "--seed",
        type=int,
        default=DEFAULT_SEED,
    )

    args = parser.parse_args()

    dataframe = read_master_dataset(
        args.input
    )

    dataframe = clean_dataset(
        dataframe
    )

    category_frames = {}

    for category, target in CATEGORY_TARGETS.items():

        category_frames[category] = (
            sample_category(
                dataframe=dataframe,
                category=category,
                target=target,
                seed=args.seed,
            )
        )

    candidates = interleave_categories(
        category_frames
    )

    if candidates.empty:
        raise ValueError(
            "No candidate records were selected."
        )

    # Final guard against accidental duplicate domains
    # within the same category.
    candidates = candidates.drop_duplicates(
        subset=[
            "scam_category",
            "registrable_domain",
        ],
        keep="first",
    ).copy()

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates.to_csv(
        args.output,
        index=False,
    )

    print()
    print("=" * 70)
    print("V1.1 CANDIDATE DATASET CREATED")
    print("=" * 70)

    print(
        f"Output: {args.output}"
    )

    print(
        f"Total rows: {len(candidates)}"
    )

    print()
    print("Binary labels:")
    print(
        candidates[
            "binary_label"
        ].value_counts()
    )

    print()
    print("Categories:")
    print(
        candidates[
            "scam_category"
        ].value_counts()
    )

    print()
    print(
        "Unique registrable domains:"
    )

    print(
        candidates[
            "registrable_domain"
        ].nunique()
    )

    print()
    print("Sources:")
    print(
        candidates[
            "source"
        ].value_counts()
    )


if __name__ == "__main__":
    main()