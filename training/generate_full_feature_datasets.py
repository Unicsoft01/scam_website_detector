import argparse
import json
from pathlib import Path
import time

import pandas as pd

from pandas.errors import EmptyDataError

from pandas.errors import (
    EmptyDataError,
)

from app.services.full_feature_service import (
    extract_full_features,
)


DEFAULT_INPUT = Path(
    "data/interim/live_url_audit.csv"
)

HEURISTIC_OUTPUT = Path(
    "data/processed/heuristic_dataset.csv"
)

BEHAVIOURAL_OUTPUT = Path(
    "data/processed/behavioural_dataset.csv"
)

HYBRID_OUTPUT = Path(
    "data/processed/hybrid_dataset.csv"
)

LOG_OUTPUT = Path(
    "data/interim/feature_extraction_log.csv"
)

HEURISTIC_FAILURE_OUTPUT = Path(
    "data/interim/"
    "heuristic_extraction_failures.csv"
)

BEHAVIOURAL_FAILURE_OUTPUT = Path(
    "data/interim/"
    "behavioural_extraction_failures.csv"
)


METADATA_COLUMNS = [
    "url",
    "original_url",
    "registrable_domain",
    "source",
    "source_category",
    "binary_label",
    "scam_category",
    "original_label",
    "live_status",
    "audit_timestamp",
]


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Generate heuristic, behavioural "
            "and hybrid feature datasets."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help=(
            "Maximum eligible records to process. "
            "Default is deliberately 10 for safety."
        ),
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help=(
            "Delay in seconds between URLs."
        ),
    )

    parser.add_argument(
        "--observation-time-ms",
        type=int,
        default=2000,
        help=(
            "General Playwright observation window."
        ),
    )

    parser.add_argument(
        "--no-rdap",
        action="store_true",
        help=(
            "Disable RDAP collection for debugging."
        ),
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Skip URLs already present in the "
            "feature extraction log."
        ),
    )

    return parser.parse_args()


def _metadata_from_row(
    row: pd.Series,
) -> dict:

    metadata = {}

    for column in METADATA_COLUMNS:

        if column in row.index:
            metadata[column] = (
                row[column]
            )

    return metadata


def _prefix_features(
    features: dict,
    prefix: str,
) -> dict:

    return {
        f"{prefix}{name}": value
        for name, value
        in features.items()
    }


def _save_dataframe(
    rows: list[dict],
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        return

    dataframe = pd.DataFrame(
        rows
    )

    dataframe.to_csv(
        path,
        index=False,
    )


def _safe_json(
    value,
) -> str:

    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    except Exception:
        return str(
            value
        )


def _read_existing_records(
    path: Path,
) -> list[dict]:
    """
    Safely read an existing checkpoint CSV.

    Returns an empty list if:
    - the file does not exist;
    - the file is zero bytes;
    - the CSV contains no readable columns.
    """

    if not path.exists():
        return []

    try:
        if path.stat().st_size == 0:
            return []

    except OSError:
        return []

    try:
        dataframe = pd.read_csv(
            path
        )

    except EmptyDataError:
        return []

    return dataframe.to_dict(
        orient="records"
    )

def main():

    args = parse_arguments()

    if not args.input.exists():
        raise FileNotFoundError(
            (
                "Live audit input does not exist: "
                f"{args.input}"
            )
        )

    if args.limit <= 0:
        raise ValueError(
            "--limit must be greater than zero."
        )

    if args.observation_time_ms <= 0:
        raise ValueError(
            "--observation-time-ms "
            "must be greater than zero."
        )

    dataframe = pd.read_csv(
        args.input
    )

    required_columns = {
        "url",
        "binary_label",
        "source",
        "scam_category",
        "live_status",
        "behavioural_eligible",
    }

    missing_columns = (
        required_columns
        - set(
            dataframe.columns
        )
    )

    if missing_columns:
        raise ValueError(
            (
                "Input dataset is missing "
                "required columns: "
                f"{sorted(missing_columns)}"
            )
        )

    # ---------------------------------------------
    # ONLY PHASE 13 ELIGIBLE RECORDS
    # ---------------------------------------------

    eligible = dataframe[
        (
            dataframe[
                "live_status"
            ]
            == "accessible"
        )
        &
        (
            dataframe[
                "behavioural_eligible"
            ]
            == 1
        )
    ].copy()

    # Exact URL duplicates must not be repeatedly
    # scanned and overweighted.
    eligible = eligible.drop_duplicates(
        subset=[
            "url"
        ],
        keep="first",
    )

    # ---------------------------------------------
    # RESUME SUPPORT
    # ---------------------------------------------

    completed_urls = set()

    if (
        args.resume
        and LOG_OUTPUT.exists()
    ):

        old_log = pd.read_csv(
            LOG_OUTPUT
        )

        if "url" in old_log.columns:
            completed_urls = set(
                old_log[
                    "url"
                ]
                .dropna()
                .astype(str)
            )

            eligible = eligible[
                ~eligible[
                    "url"
                ]
                .astype(str)
                .isin(
                    completed_urls
                )
            ]

    eligible = (
        eligible
        .head(
            args.limit
        )
        .copy()
    )

    print()

    print(
        "FULL FEATURE DATASET GENERATION"
    )

    print(
        "=" * 72
    )

    print(
        f"Input: {args.input}"
    )

    print(
        "Eligible records available: "
        f"{len(dataframe[dataframe['live_status'] == 'accessible'])}"
    )

    print(
        f"Records selected this run: "
        f"{len(eligible)}"
    )

    print(
        "Behavioural observation window: "
        f"{args.observation_time_ms} ms"
    )

    print(
        "RDAP enabled: "
        f"{not args.no_rdap}"
    )

    print()

    heuristic_rows = []
    behavioural_rows = []
    hybrid_rows = []

    log_rows = []

    heuristic_failures = []
    behavioural_failures = []

    # ---------------------------------------------
    # PRESERVE OLD OUTPUT WHEN RESUMING
    # ---------------------------------------------

    if args.resume:

      heuristic_rows = (
            _read_existing_records(
                  HEURISTIC_OUTPUT
            )
      )

      behavioural_rows = (
            _read_existing_records(
                  BEHAVIOURAL_OUTPUT
            )
      )

      hybrid_rows = (
            _read_existing_records(
                  HYBRID_OUTPUT
            )
      )

      log_rows = (
            _read_existing_records(
                  LOG_OUTPUT
            )
      )

      heuristic_failures = (
            _read_existing_records(
                  HEURISTIC_FAILURE_OUTPUT
            )
      )

      behavioural_failures = (
            _read_existing_records(
                  BEHAVIOURAL_FAILURE_OUTPUT
            )
      )

    # ---------------------------------------------
    # FEATURE EXTRACTION LOOP
    # ---------------------------------------------

    total_selected = len(
        eligible
    )

    if total_selected == 0:

      print(
            "=" * 72
      )

      print(
            "NO NEW ELIGIBLE URLS TO PROCESS"
      )

      print(
            "=" * 72
      )

      print()

      print(
            "All currently eligible URLs "
            "have already been processed."
      )

      print()

      print(
            "Use Phase 13 to audit additional "
            "dataset URLs before resuming "
            "Phase 14."
      )

      print()

      print(
            f"Existing heuristic rows: "
            f"{len(heuristic_rows)}"
      )

      print(
            f"Existing behavioural rows: "
            f"{len(behavioural_rows)}"
      )

      print(
            f"Existing hybrid rows: "
            f"{len(hybrid_rows)}"
      )

      return

    for number, (_, row) in enumerate(
        eligible.iterrows(),
        start=1,
    ):

        url = str(
            row["url"]
        ).strip()

        metadata = (
            _metadata_from_row(
                row
            )
        )

        print(
            f"[{number}/{total_selected}] "
            f"{url}"
        )

        result = (
            extract_full_features(
                url=url,

                include_rdap=(
                    not args.no_rdap
                ),

                observation_time_ms=(
                    args.observation_time_ms
                ),
            )
        )

        # -----------------------------------------
        # HEURISTIC DATASET
        # -----------------------------------------

        if result.heuristic_complete:

            heuristic_row = {
                **metadata,

                **_prefix_features(
                    result.heuristic_features,
                    "h_",
                ),
            }

            heuristic_rows.append(
                heuristic_row
            )

        else:

            heuristic_failures.append(
                {
                    **metadata,

                    "heuristic_success":
                        result.heuristic_success,

                    "heuristic_complete":
                        result.heuristic_complete,

                    "error":
                        result.heuristic_error,

                    "metadata":
                        _safe_json(
                            result.heuristic_metadata
                        ),
                }
            )

        # -----------------------------------------
        # BEHAVIOURAL DATASET
        # -----------------------------------------

        if result.behavioural_success:

            behavioural_row = {
                **metadata,

                **_prefix_features(
                    result.behavioural_features,
                    "b_",
                ),
            }

            behavioural_rows.append(
                behavioural_row
            )

        else:

            behavioural_failures.append(
                {
                    **metadata,

                    "error":
                        result.behavioural_error,

                    "metadata":
                        _safe_json(
                            result.behavioural_metadata
                        ),
                }
            )

        # -----------------------------------------
        # HYBRID DATASET
        # -----------------------------------------

        if result.hybrid_success:

            hybrid_row = {
                **metadata,

                **_prefix_features(
                    result.heuristic_features,
                    "h_",
                ),

                **_prefix_features(
                    result.behavioural_features,
                    "b_",
                ),
            }

            hybrid_rows.append(
                hybrid_row
            )

        # -----------------------------------------
        # EXTRACTION LOG
        # -----------------------------------------

        log_rows.append(
            {
                **metadata,

                "heuristic_success":
                    result.heuristic_success,

                "heuristic_complete":
                    result.heuristic_complete,

                "behavioural_success":
                    result.behavioural_success,

                "hybrid_success":
                    result.hybrid_success,

                "heuristic_duration_ms":
                    result.heuristic_duration_ms,

                "behavioural_duration_ms":
                    result.behavioural_duration_ms,

                "total_duration_ms":
                    result.total_duration_ms,

                "heuristic_error":
                    result.heuristic_error,

                "behavioural_error":
                    result.behavioural_error,
            }
        )

        # -----------------------------------------
        # CHECKPOINT AFTER EVERY URL
        # -----------------------------------------

        _save_dataframe(
            heuristic_rows,
            HEURISTIC_OUTPUT,
        )

        _save_dataframe(
            behavioural_rows,
            BEHAVIOURAL_OUTPUT,
        )

        _save_dataframe(
            hybrid_rows,
            HYBRID_OUTPUT,
        )

        _save_dataframe(
            log_rows,
            LOG_OUTPUT,
        )

        _save_dataframe(
            heuristic_failures,
            HEURISTIC_FAILURE_OUTPUT,
        )

        _save_dataframe(
            behavioural_failures,
            BEHAVIOURAL_FAILURE_OUTPUT,
        )

        print(
            "    heuristic_complete="
            f"{result.heuristic_complete}"
        )

        print(
            "    behavioural_success="
            f"{result.behavioural_success}"
        )

        print(
            "    hybrid_success="
            f"{result.hybrid_success}"
        )

        print(
            "    total_duration_ms="
            f"{result.total_duration_ms}"
        )

        if number < total_selected:
            time.sleep(
                max(
                    0.0,
                    args.delay,
                )
            )

    # ---------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------

    print()

    print(
        "=" * 72
    )

    print(
        "FEATURE EXTRACTION COMPLETE"
    )

    print(
        "=" * 72
    )

    print(
        "Heuristic dataset rows: "
        f"{len(heuristic_rows)}"
    )

    print(
        "Behavioural dataset rows: "
        f"{len(behavioural_rows)}"
    )

    print(
        "Hybrid dataset rows: "
        f"{len(hybrid_rows)}"
    )

    print(
        "Heuristic failures: "
        f"{len(heuristic_failures)}"
    )

    print(
        "Behavioural failures: "
        f"{len(behavioural_failures)}"
    )

    print()

    print(
        f"Heuristic output: "
        f"{HEURISTIC_OUTPUT}"
    )

    print(
        f"Behavioural output: "
        f"{BEHAVIOURAL_OUTPUT}"
    )

    print(
        f"Hybrid output: "
        f"{HYBRID_OUTPUT}"
    )

    print(
        f"Extraction log: "
        f"{LOG_OUTPUT}"
    )


if __name__ == "__main__":
    main()