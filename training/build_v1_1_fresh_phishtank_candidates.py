from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import tldextract


INPUT_PATH = Path(
    "data/raw/phishtank_online_valid_2026_09_04.csv"
)

MASTER_PATH = Path(
    "data/processed/master_url_index.csv"
)

OUTPUT_PATH = Path(
    "data/experiments/v1_1/fresh_phishtank_candidates.csv"
)


def get_registrable_domain(url):
    extracted = tldextract.extract(
        str(url).strip()
    )

    if not extracted.domain:
        return None

    if extracted.suffix:
        return (
            f"{extracted.domain}."
            f"{extracted.suffix}"
        ).lower()

    return extracted.domain.lower()


def main():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input: {INPUT_PATH}"
        )

    if not MASTER_PATH.exists():
        raise FileNotFoundError(
            f"Missing master: {MASTER_PATH}"
        )

    phish = pd.read_csv(
        INPUT_PATH
    )

    master = pd.read_csv(
        MASTER_PATH
    )

    required = {
        "phish_id",
        "url",
        "submission_time",
        "verified",
        "verification_time",
        "target",
    }

    missing = required - set(
        phish.columns
    )

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    old_domains = set(
        master[
            "registrable_domain"
        ]
        .dropna()
        .astype(str)
        .str.lower()
        .str.strip()
    )

    phish[
        "registrable_domain"
    ] = phish[
        "url"
    ].apply(
        get_registrable_domain
    )

    phish = phish[
        phish[
            "registrable_domain"
        ].notna()
    ].copy()

    phish = phish[
        ~phish[
            "registrable_domain"
        ].isin(
            old_domains
        )
    ].copy()

    # Convert timestamps so newest
    # records can be preferred.
    phish[
        "verification_time_parsed"
    ] = pd.to_datetime(
        phish["verification_time"],
        errors="coerce",
        utc=True,
    )

    phish[
        "submission_time_parsed"
    ] = pd.to_datetime(
        phish["submission_time"],
        errors="coerce",
        utc=True,
    )

    # Prefer the most recently verified
    # URL for each registrable domain.
    phish = phish.sort_values(
        by=[
            "verification_time_parsed",
            "submission_time_parsed",
        ],
        ascending=False,
        na_position="last",
    )

    phish = phish.drop_duplicates(
        subset=[
            "registrable_domain"
        ],
        keep="first",
    ).copy()

    collection_timestamp = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    output = pd.DataFrame(
        {
            "url": phish["url"],
            "original_url": phish["url"],
            "registrable_domain":
                phish["registrable_domain"],
            "source": "phishtank_fresh_2026_09_04",
            "source_category": "phishing",
            "binary_label": 1,
            "scam_category": "phishing",
            "original_label": "yes",
            "source_record_id":
                phish["phish_id"],
            "submission_time":
                phish["submission_time"],
            "verification_time":
                phish["verification_time"],
            "target":
                phish["target"],
            "collection_timestamp":
                collection_timestamp,
        }
    )

    output = output.reset_index(
        drop=True
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("=" * 68)
    print(
        "V1.1 FRESH PHISHTANK CANDIDATES"
    )
    print("=" * 68)

    print(
        f"ROWS: {len(output)}"
    )

    print(
        "UNIQUE DOMAINS:",
        output[
            "registrable_domain"
        ].nunique(),
    )

    print(
        "DUPLICATE DOMAINS:",
        output[
            "registrable_domain"
        ].duplicated().sum(),
    )

    print()
    print(
        "VERIFICATION TIME RANGE:"
    )

    print(
        phish[
            "verification_time_parsed"
        ].min()
    )

    print(
        "to"
    )

    print(
        phish[
            "verification_time_parsed"
        ].max()
    )

    print()
    print(
        "SUBMISSION TIME RANGE:"
    )

    print(
        phish[
            "submission_time_parsed"
        ].min()
    )

    print(
        "to"
    )

    print(
        phish[
            "submission_time_parsed"
        ].max()
    )

    print()
    print(
        f"OUTPUT: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()