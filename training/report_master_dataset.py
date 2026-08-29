from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MASTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_url_index.csv"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "master_dataset_report.txt"
)


def main():
    df = pd.read_csv(MASTER_FILE)

    lines = []

    lines.append(
        "MASTER DATASET REPORT"
    )

    lines.append(
        "=" * 60
    )

    lines.append(
        f"Total records: {len(df):,}"
    )

    lines.append("")

    lines.append(
        "Binary label distribution:"
    )

    lines.append(
        df["binary_label"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    lines.append("")

    lines.append(
        "Source distribution:"
    )

    lines.append(
        df["source"]
        .value_counts()
        .to_string()
    )

    lines.append("")

    lines.append(
        "Scam-category distribution:"
    )

    lines.append(
        df["scam_category"]
        .value_counts()
        .to_string()
    )

    lines.append("")

    lines.append(
        "Source-category distribution:"
    )

    lines.append(
        df["source_category"]
        .value_counts()
        .to_string()
    )

    lines.append("")

    lines.append(
        f"Unique registrable domains: "
        f"{df['registrable_domain'].nunique():,}"
    )

    lines.append(
        f"Unique normalized URLs: "
        f"{df['url'].nunique():,}"
    )

    report = "\n".join(lines)

    REPORT_FILE.write_text(
        report,
        encoding="utf-8"
    )

    print(report)

    print(
        f"\nReport saved to:\n"
        f"{REPORT_FILE}"
    )


if __name__ == "__main__":
    main()