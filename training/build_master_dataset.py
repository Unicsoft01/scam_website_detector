from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import pandas as pd
import tldextract


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INTERIM_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# FILE LOCATIONS
# ---------------------------------------------------------

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


SCAMFERRET_SCAM_FILES = {
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


SCAMFERRET_LEGITIMATE_FILES = {
    "cryptocurrency": (
        RAW_DIR
        / "scamferret"
        / "legitimate"
        / "scamferret_legitimate_cryptocurrency.txt"
    ),
    "investment": (
        RAW_DIR
        / "scamferret"
        / "legitimate"
        / "scamferret_legitimate_investment.txt"
    ),
    "online_shopping": (
        RAW_DIR
        / "scamferret"
        / "legitimate"
        / "scamferret_legitimate_online_shopping.txt"
    ),
    "technical_support": (
        RAW_DIR
        / "scamferret"
        / "legitimate"
        / "scamferret_legitimate_technical_support.txt"
    ),
}


# ---------------------------------------------------------
# OFFLINE DOMAIN EXTRACTOR
# ---------------------------------------------------------

extract_domain = tldextract.TLDExtract(
    suffix_list_urls=()
)


# ---------------------------------------------------------
# URL FUNCTIONS
# ---------------------------------------------------------

def normalize_url(value):
    """
    Normalize a URL conservatively without contacting the website.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        parsed = urlsplit(value)

        scheme = parsed.scheme.lower()

        if scheme not in {"http", "https"}:
            return None

        hostname = parsed.hostname

        if not hostname:
            return None

        hostname = hostname.lower().rstrip(".")

        # Preserve username/password only if they existed.
        userinfo = ""

        if parsed.username:
            userinfo = parsed.username

            if parsed.password:
                userinfo += f":{parsed.password}"

            userinfo += "@"

        # Remove default HTTP/HTTPS ports.
        port = parsed.port

        if (
            (scheme == "http" and port == 80)
            or
            (scheme == "https" and port == 443)
        ):
            port = None

        netloc = userinfo + hostname

        if port:
            netloc += f":{port}"

        path = parsed.path or "/"

        normalized = urlunsplit(
            (
                scheme,
                netloc,
                path,
                parsed.query,
                ""  # remove fragment
            )
        )

        return normalized

    except Exception:
        return None


def get_registrable_domain(url):
    """
    Extract the registrable domain without performing network requests.
    """

    if not url:
        return None

    try:
        hostname = urlsplit(url).hostname

        if not hostname:
            return None

        extracted = extract_domain(hostname)

        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}".lower()

        # Useful for IP literals or unusual hostnames.
        return hostname.lower()

    except Exception:
        return None


# ---------------------------------------------------------
# LOAD PHISHTANK
# ---------------------------------------------------------

def load_phishtank():
    if not PHISHTANK_FILE.exists():
        print(
            f"WARNING: PhishTank file missing: "
            f"{PHISHTANK_FILE}"
        )

        return pd.DataFrame()

    df = pd.read_csv(
        PHISHTANK_FILE,
        encoding_errors="replace"
    )

    if "url" not in df.columns:
        raise ValueError(
            "PhishTank file does not contain expected 'url' column."
        )

    rows = pd.DataFrame()

    rows["original_url"] = df["url"]

    rows["source"] = "phishtank"

    rows["source_category"] = "phishing"

    rows["binary_label"] = 1

    rows["scam_category"] = "phishing"

    if "verified" in df.columns:
        rows["original_label"] = df["verified"].astype(str)
    else:
        rows["original_label"] = "verified_phishing"

    return rows


# ---------------------------------------------------------
# LOAD MENDELEY
# ---------------------------------------------------------

def load_mendeley():
    if not MENDELEY_FILE.exists():
        print(
            f"WARNING: Mendeley file missing: "
            f"{MENDELEY_FILE}"
        )

        return pd.DataFrame()

    df = pd.read_csv(
        MENDELEY_FILE,
        encoding_errors="replace"
    )

    url_column = "Online shop URL"
    label_column = "Label"

    if url_column not in df.columns:
        raise ValueError(
            f"Mendeley file does not contain expected "
            f"'{url_column}' column."
        )

    if label_column not in df.columns:
        raise ValueError(
            f"Mendeley file does not contain expected "
            f"'{label_column}' column."
        )

    working = df[
        [url_column, label_column]
    ].copy()

    working[label_column] = (
        working[label_column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    valid_labels = {
        "fraudulent",
        "legitimate"
    }

    unexpected = working[
        ~working[label_column].isin(valid_labels)
    ]

    if not unexpected.empty:
        print(
            "\nWARNING: Unexpected Mendeley labels found:"
        )

        print(
            unexpected[label_column]
            .value_counts(dropna=False)
            .to_string()
        )

    # Keep only labels that we can confidently map.
    working = working[
        working[label_column].isin(valid_labels)
    ].copy()

    rows = pd.DataFrame()

    rows["original_url"] = working[url_column]

    rows["source"] = "mendeley"

    rows["source_category"] = "online_shopping"

    rows["original_label"] = working[label_column]

    rows["binary_label"] = (
        working[label_column]
        .map(
            {
                "legitimate": 0,
                "fraudulent": 1,
            }
        )
        .astype(int)
    )

    rows["scam_category"] = (
        working[label_column]
        .map(
            {
                "legitimate": "legitimate",
                "fraudulent": "online_shopping",
            }
        )
    )

    return rows


# ---------------------------------------------------------
# LOAD SCAMFERRET TXT
# ---------------------------------------------------------

def read_url_file(file_path):
    with file_path.open(
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:
        return [
            line.strip()
            for line in file
            if line.strip()
        ]


def load_scamferret_file(
    file_path,
    source_category,
    binary_label
):
    if not file_path.exists():
        print(
            f"WARNING: ScamFerret file missing: "
            f"{file_path}"
        )

        return pd.DataFrame()

    urls = read_url_file(file_path)

    rows = pd.DataFrame(
        {
            "original_url": urls
        }
    )

    rows["source"] = "scamferret"

    rows["source_category"] = source_category

    rows["binary_label"] = binary_label

    if binary_label == 1:
        rows["scam_category"] = source_category
        rows["original_label"] = "scam"

    else:
        rows["scam_category"] = "legitimate"
        rows["original_label"] = "legitimate"

    return rows


def load_all_scamferret():
    frames = []

    for category, file_path in SCAMFERRET_SCAM_FILES.items():
        frame = load_scamferret_file(
            file_path=file_path,
            source_category=category,
            binary_label=1,
        )

        if not frame.empty:
            frames.append(frame)

    for category, file_path in SCAMFERRET_LEGITIMATE_FILES.items():
        frame = load_scamferret_file(
            file_path=file_path,
            source_category=category,
            binary_label=0,
        )

        if not frame.empty:
            frames.append(frame)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True
    )


# ---------------------------------------------------------
# BUILD MASTER DATASET
# ---------------------------------------------------------

def build_master_dataset():
    print("=" * 70)
    print("MASTER DATASET CONSTRUCTION")
    print("=" * 70)

    frames = []

    phishtank = load_phishtank()

    if not phishtank.empty:
        frames.append(phishtank)

    mendeley = load_mendeley()

    if not mendeley.empty:
        frames.append(mendeley)

    scamferret = load_all_scamferret()

    if not scamferret.empty:
        frames.append(scamferret)

    if not frames:
        raise RuntimeError(
            "No raw datasets were successfully loaded."
        )

    combined = pd.concat(
        frames,
        ignore_index=True
    )

    print(
        f"\nRaw combined records: "
        f"{len(combined):,}"
    )

    # -----------------------------------------------------
    # NORMALIZE URLS
    # -----------------------------------------------------

    combined["url"] = (
        combined["original_url"]
        .apply(normalize_url)
    )

    invalid_records = combined[
        combined["url"].isna()
    ].copy()

    invalid_output = (
        INTERIM_DIR
        / "invalid_master_records.csv"
    )

    invalid_records.to_csv(
        invalid_output,
        index=False
    )

    print(
        f"Invalid/non-HTTP records removed: "
        f"{len(invalid_records):,}"
    )

    combined = combined[
        combined["url"].notna()
    ].copy()

    # -----------------------------------------------------
    # REGISTRABLE DOMAIN
    # -----------------------------------------------------

    combined["registrable_domain"] = (
        combined["url"]
        .apply(get_registrable_domain)
    )

    # -----------------------------------------------------
    # LABEL CONFLICT CHECK
    # -----------------------------------------------------

    label_counts = (
        combined
        .groupby("url")["binary_label"]
        .nunique()
    )

    conflict_urls = label_counts[
        label_counts > 1
    ].index

    label_conflicts = combined[
        combined["url"].isin(conflict_urls)
    ].copy()

    conflict_output = (
        INTERIM_DIR
        / "label_conflicts.csv"
    )

    label_conflicts.to_csv(
        conflict_output,
        index=False
    )

    print(
        f"URLs with conflicting labels: "
        f"{len(conflict_urls):,}"
    )

    # Remove unresolved label conflicts from clean master.
    combined = combined[
        ~combined["url"].isin(conflict_urls)
    ].copy()

    # -----------------------------------------------------
    # SOURCE OVERLAP AUDIT
    # -----------------------------------------------------

    source_counts = (
        combined
        .groupby("url")["source"]
        .nunique()
    )

    overlap_urls = source_counts[
        source_counts > 1
    ].index

    source_overlaps = combined[
        combined["url"].isin(overlap_urls)
    ].copy()

    overlap_output = (
        INTERIM_DIR
        / "cross_source_url_overlaps.csv"
    )

    source_overlaps.to_csv(
        overlap_output,
        index=False
    )

    print(
        f"URLs occurring in multiple sources: "
        f"{len(overlap_urls):,}"
    )

    # -----------------------------------------------------
    # DUPLICATE DOMAIN AUDIT
    # -----------------------------------------------------

    domain_counts = (
        combined
        .groupby("registrable_domain")["url"]
        .nunique()
    )

    duplicate_domains = domain_counts[
        domain_counts > 1
    ].index

    duplicate_domain_records = combined[
        combined["registrable_domain"].isin(
            duplicate_domains
        )
    ].copy()

    duplicate_domain_output = (
        INTERIM_DIR
        / "duplicate_domain_records.csv"
    )

    duplicate_domain_records.to_csv(
        duplicate_domain_output,
        index=False
    )

    print(
        f"Domains associated with multiple unique URLs: "
        f"{len(duplicate_domains):,}"
    )

    # -----------------------------------------------------
    # EXACT NORMALIZED URL DUPLICATES
    # -----------------------------------------------------

    before_dedup = len(combined)

    # Sort for deterministic output.
    combined = combined.sort_values(
        by=[
            "url",
            "source",
            "source_category"
        ]
    )

    combined = combined.drop_duplicates(
        subset=["url"],
        keep="first"
    )

    removed_duplicates = (
        before_dedup
        - len(combined)
    )

    print(
        f"Duplicate normalized URL records removed: "
        f"{removed_duplicates:,}"
    )

    # -----------------------------------------------------
    # FINAL COLUMN ORDER
    # -----------------------------------------------------

    final_columns = [
        "url",
        "original_url",
        "registrable_domain",
        "source",
        "source_category",
        "binary_label",
        "scam_category",
        "original_label",
    ]

    combined = combined[
        final_columns
    ].copy()

    combined = combined.sort_values(
        by=[
            "binary_label",
            "source",
            "source_category",
            "url",
        ]
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # SAVE MASTER
    # -----------------------------------------------------

    master_output = (
        PROCESSED_DIR
        / "master_url_index.csv"
    )

    combined.to_csv(
        master_output,
        index=False
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL MASTER DATASET")
    print("=" * 70)

    print(
        f"Final records: "
        f"{len(combined):,}"
    )

    print("\nBinary label distribution:")

    print(
        combined["binary_label"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nSource distribution:")

    print(
        combined["source"]
        .value_counts()
        .to_string()
    )

    print("\nScam-category distribution:")

    print(
        combined["scam_category"]
        .value_counts()
        .to_string()
    )

    print("\nSource-category distribution:")

    print(
        combined["source_category"]
        .value_counts()
        .to_string()
    )

    print(
        f"\nMaster dataset saved to:\n"
        f"{master_output}"
    )

    print(
        f"\nInvalid records report:\n"
        f"{invalid_output}"
    )

    print(
        f"\nLabel conflicts report:\n"
        f"{conflict_output}"
    )

    print(
        f"\nCross-source overlaps report:\n"
        f"{overlap_output}"
    )

    print(
        f"\nDuplicate-domain report:\n"
        f"{duplicate_domain_output}"
    )


if __name__ == "__main__":
    build_master_dataset()