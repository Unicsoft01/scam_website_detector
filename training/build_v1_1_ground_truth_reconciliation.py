import argparse
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import tldextract


DEFAULT_INPUT = Path(
    "data/experiments/v1_1/accessible_scam_candidates.csv"
)

DEFAULT_OUTPUT = Path(
    "data/experiments/v1_1/scam_ground_truth_reconciliation.csv"
)


REQUIRED_COLUMNS = {
    "url",
    "registrable_domain",
    "source",
    "binary_label",
    "scam_category",
    "live_status",
    "status_code",
    "final_url",
    "content_type",
    "redirect_count",
    "html_available",
    "audit_timestamp",
}


def registrable_domain_from_url(url):
    if pd.isna(url):
        return None

    value = str(url).strip()

    if not value:
        return None

    extracted = tldextract.extract(value)

    if not extracted.domain:
        return None

    if extracted.suffix:
        return (
            f"{extracted.domain}."
            f"{extracted.suffix}"
        )

    return extracted.domain


def hostname_from_url(url):
    if pd.isna(url):
        return None

    try:
        return (
            urlparse(
                str(url)
            ).hostname
        )
    except Exception:
        return None


def classify_record(row):
    """
    This classification measures ground-truth
    confidence for CURRENT behavioural use.

    It does not relabel any scam record as
    legitimate.
    """

    source = str(
        row["source"]
    ).strip().lower()

    same_domain = bool(
        row["same_registrable_domain"]
    )

    html_available = (
        int(row["html_available"]) == 1
    )

    status_code = pd.to_numeric(
        row["status_code"],
        errors="coerce",
    )

    if (
        pd.isna(status_code)
        or status_code < 200
        or status_code >= 400
        or not html_available
    ):
        return "exclude_not_currently_usable"

    # PhishTank records came from the
    # current verified-online phishing feed.
    # Domain continuity provides additional
    # support, although page identity still
    # requires caution.
    if source == "phishtank":

        if same_domain:
            return "provisional_current_positive"

        return "manual_reconciliation_required"

    # ScamFerret and Mendeley labels are
    # historical. Accessibility and domain
    # continuity alone cannot prove that the
    # current page is still malicious.
    if source in {
        "scamferret",
        "mendeley",
    }:

        if same_domain:
            return "historical_positive_uncertain_current"

        return "manual_reconciliation_required"

    return "manual_reconciliation_required"


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Build v1.1 ground-truth "
            "reconciliation report."
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

    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input file not found: {args.input}"
        )

    dataframe = pd.read_csv(
        args.input
    )

    missing = REQUIRED_COLUMNS - set(
        dataframe.columns
    )

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    if dataframe.empty:
        raise ValueError(
            "Input dataset is empty."
        )

    if not (
        dataframe["binary_label"] == 1
    ).all():
        raise ValueError(
            "Reconciliation input must contain "
            "only scam-labelled records."
        )

    dataframe[
        "submitted_hostname"
    ] = dataframe["url"].apply(
        hostname_from_url
    )

    dataframe[
        "final_hostname"
    ] = dataframe["final_url"].apply(
        hostname_from_url
    )

    dataframe[
        "submitted_registrable_domain"
    ] = dataframe["url"].apply(
        registrable_domain_from_url
    )

    dataframe[
        "final_registrable_domain"
    ] = dataframe["final_url"].apply(
        registrable_domain_from_url
    )

    dataframe[
        "same_registrable_domain"
    ] = (
        dataframe[
            "submitted_registrable_domain"
        ]
        ==
        dataframe[
            "final_registrable_domain"
        ]
    )

    dataframe[
        "cross_domain_redirect"
    ] = (
        ~dataframe[
            "same_registrable_domain"
        ]
    ).astype(int)

    dataframe[
        "ground_truth_status"
    ] = dataframe.apply(
        classify_record,
        axis=1,
    )

    dataframe[
        "original_binary_label"
    ] = dataframe[
        "binary_label"
    ]

    # IMPORTANT:
    # We do not change binary_label here.
    # Uncertain historical records stay
    # quarantined rather than becoming legit.

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        args.output,
        index=False,
    )

    print()
    print("=" * 70)
    print(
        "V1.1 SCAM GROUND-TRUTH RECONCILIATION"
    )
    print("=" * 70)

    print(
        f"Rows examined: {len(dataframe)}"
    )

    print()
    print(
        "GROUND-TRUTH STATUS"
    )

    print(
        dataframe[
            "ground_truth_status"
        ].value_counts(
            dropna=False
        )
    )

    print()
    print(
        "STATUS BY SOURCE"
    )

    print(
        pd.crosstab(
            dataframe["source"],
            dataframe[
                "ground_truth_status"
            ],
        )
    )

    print()
    print(
        "STATUS BY CATEGORY"
    )

    print(
        pd.crosstab(
            dataframe["scam_category"],
            dataframe[
                "ground_truth_status"
            ],
        )
    )

    print()
    print(
        "CROSS-DOMAIN REDIRECTS:"
    )

    print(
        dataframe[
            "cross_domain_redirect"
        ].value_counts(
            dropna=False
        )
    )

    print()
    print(
        f"Output: {args.output}"
    )


if __name__ == "__main__":
    main()