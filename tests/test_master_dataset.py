from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MASTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_url_index.csv"
)


def test_master_dataset_exists():
    assert MASTER_FILE.exists()


def test_master_dataset_required_columns():
    df = pd.read_csv(MASTER_FILE)

    expected_columns = {
        "url",
        "original_url",
        "registrable_domain",
        "source",
        "source_category",
        "binary_label",
        "scam_category",
        "original_label",
    }

    assert expected_columns.issubset(
        set(df.columns)
    )


def test_master_dataset_binary_labels():
    df = pd.read_csv(MASTER_FILE)

    labels = set(
        df["binary_label"]
        .dropna()
        .unique()
    )

    assert labels.issubset({0, 1})


def test_master_dataset_no_duplicate_urls():
    df = pd.read_csv(MASTER_FILE)

    assert df["url"].duplicated().sum() == 0


def test_master_dataset_no_missing_urls():
    df = pd.read_csv(MASTER_FILE)

    assert df["url"].isna().sum() == 0


def test_master_dataset_no_label_conflicts():
    df = pd.read_csv(MASTER_FILE)

    conflict_count = (
        df.groupby("url")["binary_label"]
        .nunique()
        .gt(1)
        .sum()
    )

    assert conflict_count == 0