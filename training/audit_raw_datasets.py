from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"

INTERIM_DIR.mkdir(parents=True, exist_ok=True)


PHISHTANK_FILE = (
    RAW_DIR
    / "phishtank"
    / "phishtank_verified_online.csv"
)

MENDELEY_FILE = (
    RAW_DIR
    / "mendeley"
    / "mendeley_online_shops.csv"
)

SCAMFERRET_FILES = {
    "cryptocurrency": (
        RAW_DIR
        / "scamferret"
        / "scam"
        / "scamferret_scam_cryptocurrency.txt"
    ),
    "investment": (
        RAW_DIR
        / "scamferret"
        / "scam"
        / "scamferret_scam_investment.txt"
    ),
    "online_shopping": (
        RAW_DIR
        / "scamferret"
        / "scam"
        / "scamferret_scam_online_shopping.txt"
    ),
    "technical_support": (
        RAW_DIR
        / "scamferret"
        / "scam"
        / "scamferret_scam_technical_support.txt"
    ),
}


def is_valid_http_url(value):
    if pd.isna(value):
        return False

    value = str(value).strip()

    if not value:
        return False

    try:
        parsed = urlparse(value)

        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def audit_csv(
    name,
    file_path,
    url_column=None,
    label_column=None
):
    print("\n" + "=" * 70)
    print(f"DATASET: {name}")
    print("=" * 70)

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return None

    df = pd.read_csv(
        file_path,
        encoding_errors="replace"
    )

    print(f"File: {file_path.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")
    for column in df.columns:
        print(f" - {column}")

    print("\nMissing values per column:")
    missing = df.isna().sum()

    for column, count in missing.items():
        print(f" - {column}: {count:,}")

    print(f"\nExact duplicate rows: {df.duplicated().sum():,}")

    if url_column and url_column in df.columns:
        urls = df[url_column].astype("string").str.strip()

        print(
            f"Duplicate URLs: "
            f"{urls.duplicated().sum():,}"
        )

        valid_mask = urls.apply(is_valid_http_url)

        print(
            f"Valid HTTP/HTTPS URLs: "
            f"{valid_mask.sum():,}"
        )

        print(
            f"Malformed/non-HTTP URLs: "
            f"{(~valid_mask).sum():,}"
        )

        malformed_examples = urls[~valid_mask].head(5)

        if len(malformed_examples) > 0:
            print("\nExample malformed URLs:")

            for value in malformed_examples:
                print(f" - {value}")

    else:
        print(
            "\nURL audit skipped because the expected URL "
            "column was not found."
        )

    if label_column and label_column in df.columns:
        print("\nLabel distribution:")

        print(
            df[label_column]
            .value_counts(dropna=False)
            .to_string()
        )

    return {
        "dataset": name,
        "file": file_path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def load_scamferret_urls(file_path):
    with file_path.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:
        urls = [
            line.strip()
            for line in file
            if line.strip()
        ]

    return urls


def audit_scamferret(name, file_path):
    print("\n" + "=" * 70)
    print(f"DATASET: ScamFerret - {name}")
    print("=" * 70)

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return None

    urls = load_scamferret_urls(file_path)

    series = pd.Series(
        urls,
        dtype="string",
        name="url"
    )

    duplicate_count = int(series.duplicated().sum())

    valid_mask = series.apply(is_valid_http_url)

    print(f"File: {file_path.name}")
    print(f"URL rows: {len(series):,}")
    print(f"Unique URLs: {series.nunique():,}")
    print(f"Duplicate URLs: {duplicate_count:,}")
    print(f"Valid HTTP/HTTPS URLs: {valid_mask.sum():,}")
    print(f"Malformed/non-HTTP URLs: {(~valid_mask).sum():,}")

    malformed_examples = series[~valid_mask].head(5)

    if len(malformed_examples) > 0:
        print("\nExample malformed URLs:")

        for value in malformed_examples:
            print(f" - {value}")

    return {
        "dataset": f"ScamFerret_{name}",
        "file": file_path.name,
        "rows": len(series),
        "columns": 1,
        "duplicate_rows": duplicate_count,
    }


def main():
    print("\nRAW DATASET AUDIT")
    print("=" * 70)

    summaries = []

    result = audit_csv(
        name="PhishTank",
        file_path=PHISHTANK_FILE,
        url_column="url",
        label_column="verified",
    )

    if result:
        summaries.append(result)

    result = audit_csv(
        name="Mendeley Online Shops",
        file_path=MENDELEY_FILE,
        url_column="Online shop URL",
        label_column="Label",
    )

    if result:
        summaries.append(result)

    for category, path in SCAMFERRET_FILES.items():
        result = audit_scamferret(
            name=category,
            file_path=path,
        )

        if result:
            summaries.append(result)

    if summaries:
        summary_df = pd.DataFrame(summaries)

        output_file = (
            INTERIM_DIR
            / "raw_dataset_audit_summary.csv"
        )

        summary_df.to_csv(
            output_file,
            index=False
        )

        print("\n" + "=" * 70)
        print("AUDIT SUMMARY")
        print("=" * 70)

        print(summary_df.to_string(index=False))

        print(
            f"\nAudit summary saved to:\n{output_file}"
        )


if __name__ == "__main__":
    main()