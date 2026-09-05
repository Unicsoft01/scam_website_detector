from pathlib import Path
import pandas as pd


BASE = Path("data/experiments/v1_1")

OLD_RECON = (
    BASE
    / "scam_ground_truth_reconciliation.csv"
)

FRESH_PHISH = (
    BASE
    / "fresh_phishtank_live_audit.csv"
)

LEGIT_FILE = (
    BASE
    / "accessible_legitimate_candidates.csv"
)

OUTPUT = (
    BASE
    / "final_eligible_pool.csv"
)


REQUIRED_COLUMNS = [
    "url",
    "registrable_domain",
    "binary_label",
    "scam_category",
    "source",
    "live_status",
    "behavioural_eligible",
]


def require_columns(df, name):
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise RuntimeError(
            f"{name} is missing required columns: "
            f"{missing}"
        )


def prepare_common_columns(df):
    """
    Preserve the fields required by the existing
    feature extraction pipeline.
    """

    df = df.copy()

    columns = [
        "url",
        "registrable_domain",
        "source",
        "binary_label",
        "scam_category",
        "live_status",
        "behavioural_eligible",
    ]

    # Preserve additional useful fields when available.
    optional = [
        "original_url",
        "source_category",
        "original_label",
        "hybrid_eligible",
        "status_code",
        "final_url",
        "content_type",
        "downloaded_bytes",
        "redirect_count",
        "html_available",
        "audit_timestamp",
    ]

    for column in optional:
        if column in df.columns:
            columns.append(column)

    return df[columns].copy()


def main():
    # -------------------------------------------------
    # Check source files
    # -------------------------------------------------

    for path in [
        OLD_RECON,
        FRESH_PHISH,
        LEGIT_FILE,
    ]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file missing: {path}"
            )

    # =================================================
    # 1. PREVIOUSLY RECONCILED PHISHTANK POSITIVES
    # =================================================

    old = pd.read_csv(
        OLD_RECON
    )

    if "ground_truth_status" not in old.columns:
        raise RuntimeError(
            "ground_truth_status column is missing "
            "from scam_ground_truth_reconciliation.csv"
        )

    require_columns(
        old,
        "scam_ground_truth_reconciliation.csv",
    )

    old_positive = old[
        (
            old["ground_truth_status"]
            == "provisional_current_positive"
        )
        &
        (
            old["live_status"]
            == "accessible"
        )
        &
        (
            old["behavioural_eligible"]
            == 1
        )
    ].copy()

    print(
        "Previously reconciled positives:",
        len(old_positive),
    )

    # =================================================
    # 2. FRESH PHISHTANK POSITIVES
    # =================================================

    fresh = pd.read_csv(
        FRESH_PHISH
    )

    require_columns(
        fresh,
        "fresh_phishtank_live_audit.csv",
    )

    fresh_positive = fresh[
        (
            fresh["live_status"]
            == "accessible"
        )
        &
        (
            fresh["behavioural_eligible"]
            == 1
        )
    ].copy()

    # These rows originate from the fresh
    # PhishTank phishing candidate set.
    fresh_positive[
        "binary_label"
    ] = 1

    fresh_positive[
        "scam_category"
    ] = "phishing"

    print(
        "Fresh accessible PhishTank positives:",
        len(fresh_positive),
    )

    # =================================================
    # 3. ACCESSIBLE LEGITIMATE CONTROLS
    # =================================================

    legitimate = pd.read_csv(
        LEGIT_FILE
    )

    require_columns(
        legitimate,
        "accessible_legitimate_candidates.csv",
    )

    legitimate = legitimate[
        (
            legitimate["live_status"]
            == "accessible"
        )
        &
        (
            legitimate["behavioural_eligible"]
            == 1
        )
    ].copy()

    legitimate[
        "binary_label"
    ] = 0

    legitimate[
        "scam_category"
    ] = "legitimate"

    print(
        "Accessible behavioural-eligible "
        "legitimate candidates:",
        len(legitimate),
    )

    # =================================================
    # 4. KEEP REQUIRED PIPELINE COLUMNS
    # =================================================

    old_positive = prepare_common_columns(
        old_positive
    )

    fresh_positive = prepare_common_columns(
        fresh_positive
    )

    legitimate = prepare_common_columns(
        legitimate
    )

    # =================================================
    # 5. COMBINE
    # =================================================

    combined = pd.concat(
        [
            old_positive,
            fresh_positive,
            legitimate,
        ],
        ignore_index=True,
        sort=False,
    )

    # -------------------------------------------------
    # Normalise domain
    # -------------------------------------------------

    combined[
        "registrable_domain"
    ] = (
        combined[
            "registrable_domain"
        ]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -------------------------------------------------
    # Detect label conflicts BEFORE deduplication
    # -------------------------------------------------

    label_counts = (
        combined.groupby(
            "registrable_domain"
        )["binary_label"]
        .nunique()
    )

    conflicting_domains = set(
        label_counts[
            label_counts > 1
        ].index
    )

    print(
        "Conflicting domains removed:",
        len(conflicting_domains),
    )

    if conflicting_domains:
        combined = combined[
            ~combined[
                "registrable_domain"
            ].isin(
                conflicting_domains
            )
        ].copy()

    # -------------------------------------------------
    # Domain-level deduplication
    # -------------------------------------------------

    combined = (
        combined
        .drop_duplicates(
            subset=[
                "registrable_domain"
            ],
            keep="first",
        )
        .reset_index(
            drop=True
        )
    )

    # =================================================
    # 6. SPLIT SCAM / LEGITIMATE POOLS
    # =================================================

    scam = combined[
        combined[
            "binary_label"
        ] == 1
    ].copy()

    legit = combined[
        combined[
            "binary_label"
        ] == 0
    ].copy()

    if scam.empty:
        raise RuntimeError(
            "No current eligible scam positives "
            "were available."
        )

    if legit.empty:
        raise RuntimeError(
            "No eligible legitimate controls "
            "were available."
        )

    # =================================================
    # 7. BALANCE LEGITIMATE SAMPLE TO SCAM COUNT
    # =================================================

    legit_target = min(
        len(legit),
        len(scam),
    )

    legit = legit.sample(
        n=legit_target,
        random_state=42,
        replace=False,
    )

    final = pd.concat(
        [
            scam,
            legit,
        ],
        ignore_index=True,
        sort=False,
    )

    final = final.sample(
        frac=1,
        random_state=42,
    ).reset_index(
        drop=True
    )

    # =================================================
    # 8. FINAL SAFETY CHECKS
    # =================================================

    require_columns(
        final,
        "final eligible pool",
    )

    if (
        final[
            "registrable_domain"
        ].duplicated().any()
    ):
        raise RuntimeError(
            "Duplicate registrable domains remain "
            "in final eligible pool."
        )

    bad_live = final[
        final[
            "live_status"
        ] != "accessible"
    ]

    if not bad_live.empty:
        raise RuntimeError(
            "Non-accessible rows remain in final pool."
        )

    bad_behaviour = final[
        final[
            "behavioural_eligible"
        ] != 1
    ]

    if not bad_behaviour.empty:
        raise RuntimeError(
            "Behaviourally ineligible rows remain "
            "in final pool."
        )

    # If hybrid_eligible exists, require it too.
    if "hybrid_eligible" in final.columns:
        bad_hybrid = final[
            final[
                "hybrid_eligible"
            ] != 1
        ]

        if not bad_hybrid.empty:
            raise RuntimeError(
                "Hybrid-ineligible rows remain "
                "in final pool."
            )

    # =================================================
    # 9. SAVE
    # =================================================

    final.to_csv(
        OUTPUT,
        index=False,
    )

    # =================================================
    # 10. SUMMARY
    # =================================================

    print(
        "\n================================"
    )

    print(
        "FINAL ELIGIBLE POOL CREATED"
    )

    print(
        "================================"
    )

    print(
        "TOTAL ROWS:",
        len(final),
    )

    print(
        "UNIQUE DOMAINS:",
        final[
            "registrable_domain"
        ].nunique(),
    )

    print(
        "\nLABEL DISTRIBUTION:"
    )

    print(
        final[
            "binary_label"
        ].value_counts()
    )

    print(
        "\nCATEGORY DISTRIBUTION:"
    )

    print(
        final[
            "scam_category"
        ].value_counts()
    )

    print(
        "\nLIVE STATUS:"
    )

    print(
        final[
            "live_status"
        ].value_counts(
            dropna=False
        )
    )

    print(
        "\nBEHAVIOURAL ELIGIBILITY:"
    )

    print(
        final[
            "behavioural_eligible"
        ].value_counts(
            dropna=False
        )
    )

    if (
        "hybrid_eligible"
        in final.columns
    ):
        print(
            "\nHYBRID ELIGIBILITY:"
        )

        print(
            final[
                "hybrid_eligible"
            ].value_counts(
                dropna=False
            )
        )

    print(
        "\nSaved:",
        OUTPUT,
    )


if __name__ == "__main__":
    main()