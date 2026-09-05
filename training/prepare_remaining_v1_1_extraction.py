from pathlib import Path
import pandas as pd


BASE = Path("data/experiments/v1_1")

POOL_FILE = (
    BASE
    / "final_eligible_pool.csv"
)

LOG_FILE = Path(
    "data/interim/feature_extraction_log.csv"
)

OUTPUT = (
    BASE
    / "remaining_feature_extraction_candidates.csv"
)


def normalise_domain(series):
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
    )


def main():
    if not POOL_FILE.exists():
        raise FileNotFoundError(
            f"Missing: {POOL_FILE}"
        )

    if not LOG_FILE.exists():
        raise FileNotFoundError(
            f"Missing: {LOG_FILE}"
        )

    pool = pd.read_csv(
        POOL_FILE
    )

    log = pd.read_csv(
        LOG_FILE
    )

    if "registrable_domain" not in pool.columns:
        raise RuntimeError(
            "final_eligible_pool.csv has no "
            "registrable_domain column."
        )

    if "registrable_domain" not in log.columns:
        raise RuntimeError(
            "feature_extraction_log.csv has no "
            "registrable_domain column."
        )

    pool = pool.copy()
    log = log.copy()

    pool["registrable_domain"] = (
        normalise_domain(
            pool["registrable_domain"]
        )
    )

    log["registrable_domain"] = (
        normalise_domain(
            log["registrable_domain"]
        )
    )

    pool_domains = set(
        pool[
            "registrable_domain"
        ]
    )

    log_domains = set(
        log[
            "registrable_domain"
        ]
    )

    attempted = (
        pool_domains
        & log_domains
    )

    remaining_domains = (
        pool_domains
        - log_domains
    )

    unrelated_log_domains = (
        log_domains
        - pool_domains
    )

    remaining = pool[
        pool[
            "registrable_domain"
        ].isin(
            remaining_domains
        )
    ].copy()

    remaining = (
        remaining
        .drop_duplicates(
            subset=[
                "registrable_domain"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    remaining.to_csv(
        OUTPUT,
        index=False,
    )

    print(
        "\n======================================"
    )

    print(
        "V1.1 REMAINING EXTRACTION CHECK"
    )

    print(
        "======================================"
    )

    print(
        "Final eligible pool:",
        len(pool_domains),
    )

    print(
        "Log domains total:",
        len(log_domains),
    )

    print(
        "Pool domains already attempted:",
        len(attempted),
    )

    print(
        "Pool domains still unattempted:",
        len(remaining_domains),
    )

    print(
        "Log domains outside final pool:",
        len(unrelated_log_domains),
    )

    print(
        "\nRemaining labels:"
    )

    print(
        remaining[
            "binary_label"
        ].value_counts(
            dropna=False
        )
    )

    print(
        "\nRemaining categories:"
    )

    print(
        remaining[
            "scam_category"
        ].value_counts(
            dropna=False
        )
    )

    print(
        "\nSaved:"
    )

    print(
        OUTPUT
    )


if __name__ == "__main__":
    main()