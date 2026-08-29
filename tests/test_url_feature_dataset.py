from pathlib import Path

import pandas as pd


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


FEATURE_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "url_level_features.csv"
)


EXPECTED_FEATURES = {
    "url_length",
    "hostname_length",
    "domain_length",
    "path_length",
    "query_length",
    "fragment_length",
    "dot_count",
    "hyphen_count",
    "digit_count",
    "special_character_count",
    "underscore_count",
    "at_symbol_count",
    "percent_encoded_count",
    "subdomain_count",
    "has_ip_address",
    "parameter_count",
    "repeated_character_count",
    "suspicious_token_count",
    "has_suspicious_extension",
    "domain_is_long",
    "url_is_long",
}


def test_url_feature_dataset_exists():
    assert FEATURE_FILE.exists()


def test_url_feature_columns_exist():
    df = pd.read_csv(
        FEATURE_FILE
    )

    assert (
        EXPECTED_FEATURES
        .issubset(
            set(df.columns)
        )
    )


def test_binary_labels_valid():
    df = pd.read_csv(
        FEATURE_FILE
    )

    labels = set(
        df["binary_label"]
        .dropna()
        .unique()
    )

    assert labels.issubset(
        {0, 1}
    )


def test_no_missing_url_values():
    df = pd.read_csv(
        FEATURE_FILE
    )

    assert (
        df["url"]
        .isna()
        .sum()
        == 0
    )