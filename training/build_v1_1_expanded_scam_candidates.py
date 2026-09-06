from pathlib import Path

import pandas as pd
import tldextract


MASTER_PATH = Path(
    "data/processed/master_url_index.csv"
)

RAW_DIR = Path(
    "data/raw/scamferret_expanded_2025"
)

OUTPUT_PATH = Path(
    "data/experiments/v1_1/expanded_scam_candidates.csv"
)


FILES = {
    "cryptocurrency_groundtruth_url.txt": "cryptocurrency",
    "investment_groundtruth_url.txt": "investment",
    "online_shopping_english_groundtruth_url.txt": "online_shopping",
    "technical_support_groundtruth_url.txt": "technical_support",
}


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

    if not MASTER_PATH.exists():
        raise FileNotFoundError(
            f"Missing master dataset: {MASTER_PATH}"
        )

    master = pd.read_csv(
        MASTER_PATH
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

    rows = []

    for filename, category in FILES.items():

        path = RAW_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing input file: {path}"
            )

        urls = [
            line.strip()
            for line in path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).splitlines()
            if line.strip()
        ]

        seen_domains = set()

        for url in urls:

            domain = get_registrable_domain(
                url
            )

            if not domain:
                continue

            # One observation per
            # registrable domain.
            if domain in seen_domains:
                continue

            seen_domains.add(domain)

            # Exclude anything already
            # represented in current master.
            if domain in old_domains:
                continue

            rows.append(
                {
                    "url": url,
                    "original_url": url,
                    "registrable_domain": domain,
                    "source": "scamferret_expanded_2025",
                    "source_category": category,
                    "binary_label": 1,
                    "scam_category": category,
                    "original_label": "scam",
                }
            )

    dataframe = pd.DataFrame(
        rows
    )

    if dataframe.empty:
        raise ValueError(
            "No genuinely new candidate domains found."
        )

    # Defensive duplicate check across
    # the complete expanded pool.
    dataframe = dataframe.drop_duplicates(
        subset=["registrable_domain"],
        keep="first",
    ).reset_index(
        drop=True
    )

    # Deterministic shuffle.
    dataframe = dataframe.sample(
        frac=1,
        random_state=42,
    ).reset_index(
        drop=True
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("=" * 68)
    print(
        "V1.1 EXPANDED SCAM CANDIDATE SET"
    )
    print("=" * 68)

    print(
        f"TOTAL CANDIDATES: {len(dataframe)}"
    )

    print(
        f"UNIQUE DOMAINS: "
        f"{dataframe['registrable_domain'].nunique()}"
    )

    print(
        f"DUPLICATE DOMAINS: "
        f"{dataframe['registrable_domain'].duplicated().sum()}"
    )

    print()
    print(
        "BY CATEGORY:"
    )

    print(
        dataframe[
            "scam_category"
        ].value_counts()
    )

    print()
    print(
        f"OUTPUT: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()