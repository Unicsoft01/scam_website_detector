from pathlib import Path
import pandas as pd


POOL = Path(
    "data/experiments/v1_1/final_eligible_pool.csv"
)

H_FILE = Path(
    "data/processed/heuristic_dataset.csv"
)

B_FILE = Path(
    "data/processed/behavioural_dataset.csv"
)

HYBRID_FILE = Path(
    "data/processed/hybrid_dataset.csv"
)

LOG_FILE = Path(
    "data/interim/feature_extraction_log.csv"
)

H_FAILURES = Path(
    "data/interim/heuristic_extraction_failures.csv"
)

B_FAILURES = Path(
    "data/interim/behavioural_extraction_failures.csv"
)

OUTPUT = Path(
    "data/experiments/v1_1/feature_coverage_report.csv"
)


def read_optional(path):
    if not path.exists():
        return None

    try:
        df = pd.read_csv(path)

        if df.empty:
            return None

        return df

    except Exception:
        return None


def domains(df):
    if (
        df is None
        or "registrable_domain" not in df.columns
    ):
        return set()

    return set(
        df["registrable_domain"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
    )


def print_reason_columns(df, name):
    if df is None:
        print(
            f"\n{name}: unavailable or empty"
        )
        return

    print(
        f"\n{name}: {len(df)} rows"
    )

    interesting = [
        c for c in df.columns
        if any(
            word in c.lower()
            for word in [
                "status",
                "error",
                "reason",
                "success",
                "message",
            ]
        )
    ]

    print(
        "Diagnostic columns:",
        interesting,
    )

    for column in interesting:
        counts = (
            df[column]
            .astype(str)
            .value_counts(
                dropna=False
            )
            .head(15)
        )

        print(
            f"\n{column}:"
        )

        print(
            counts.to_string()
        )


def main():
    if not POOL.exists():
        raise FileNotFoundError(
            f"Missing: {POOL}"
        )

    pool = pd.read_csv(
        POOL
    )

    heuristic = pd.read_csv(
        H_FILE
    )

    behavioural = pd.read_csv(
        B_FILE
    )

    hybrid = pd.read_csv(
        HYBRID_FILE
    )

    pool_domains = domains(
        pool
    )

    h_domains = domains(
        heuristic
    )

    b_domains = domains(
        behavioural
    )

    hybrid_domains = domains(
        hybrid
    )

    report = pool[
        [
            "url",
            "registrable_domain",
            "binary_label",
            "scam_category",
            "source",
        ]
    ].copy()

    report[
        "registrable_domain"
    ] = (
        report[
            "registrable_domain"
        ]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    report[
        "heuristic_present"
    ] = report[
        "registrable_domain"
    ].isin(
        h_domains
    ).astype(int)

    report[
        "behavioural_present"
    ] = report[
        "registrable_domain"
    ].isin(
        b_domains
    ).astype(int)

    report[
        "hybrid_present"
    ] = report[
        "registrable_domain"
    ].isin(
        hybrid_domains
    ).astype(int)

    report.to_csv(
        OUTPUT,
        index=False,
    )

    print(
        "\n======================================"
    )

    print(
        "V1.1 FEATURE COVERAGE"
    )

    print(
        "======================================"
    )

    print(
        "Eligible pool:",
        len(pool_domains),
    )

    print(
        "Heuristic:",
        len(h_domains),
    )

    print(
        "Behavioural:",
        len(b_domains),
    )

    print(
        "Hybrid:",
        len(hybrid_domains),
    )

    print(
        "\nMissing heuristic:",
        len(
            pool_domains
            - h_domains
        ),
    )

    print(
        "Missing behavioural:",
        len(
            pool_domains
            - b_domains
        ),
    )

    print(
        "Missing hybrid:",
        len(
            pool_domains
            - hybrid_domains
        ),
    )

    print(
        "\nCoverage by label:"
    )

    print(
        report.groupby(
            "binary_label"
        )[
            [
                "heuristic_present",
                "behavioural_present",
                "hybrid_present",
            ]
        ]
        .sum()
        .to_string()
    )

    print(
        "\nCoverage by category:"
    )

    print(
        report.groupby(
            "scam_category"
        )[
            [
                "heuristic_present",
                "behavioural_present",
                "hybrid_present",
            ]
        ]
        .agg(
            [
                "sum",
                "count",
            ]
        )
        .to_string()
    )

    log = read_optional(
        LOG_FILE
    )

    h_fail = read_optional(
        H_FAILURES
    )

    b_fail = read_optional(
        B_FAILURES
    )

    print_reason_columns(
        log,
        "Feature extraction log",
    )

    print_reason_columns(
        h_fail,
        "Heuristic failures",
    )

    print_reason_columns(
        b_fail,
        "Behavioural failures",
    )

    print(
        "\nCoverage report saved:"
    )

    print(
        OUTPUT
    )


if __name__ == "__main__":
    main()