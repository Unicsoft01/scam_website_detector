import argparse
from pathlib import Path
import time

import pandas as pd

from app.services.live_availability_service import (
    audit_live_url,
    live_result_to_dict,
)


DEFAULT_INPUT = Path(
    "data/experiments/v1_1/candidates.csv"
)

DEFAULT_OUTPUT = Path(
    "data/experiments/v1_1/live_url_audit.csv"
)

DEFAULT_SUMMARY = Path(
    "data/experiments/v1_1/live_url_audit_summary.csv"
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Resumable controlled live-availability audit "
            "for v1.1 candidate website URLs."
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

    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help=(
            "Maximum number of previously unaudited "
            "records to process in this run."
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

    return parser.parse_args()


def build_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        dataframe["live_status"]
        .value_counts(dropna=False)
        .rename_axis("live_status")
        .reset_index(name="count")
    )

    summary["percentage"] = (
        summary["count"]
        / len(dataframe)
        * 100
    ).round(2)

    return summary


def save_progress(
    dataframe: pd.DataFrame,
    output_path: Path,
    summary_path: Path,
):
    """
    Save accumulated audit observations.

    A temporary file is written first and then
    replaces the main output. This reduces the
    risk of leaving a partially written CSV if
    execution stops during a save.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Defensive URL deduplication.
    dataframe = (
        dataframe
        .drop_duplicates(
            subset=["url"],
            keep="last",
        )
        .copy()
    )

    temporary_output = (
        output_path.parent
        / f"{output_path.name}.tmp"
    )

    dataframe.to_csv(
        temporary_output,
        index=False,
    )

    temporary_output.replace(
        output_path
    )

    if not dataframe.empty:

        summary = build_summary(
            dataframe
        )

        temporary_summary = (
            summary_path.parent
            / f"{summary_path.name}.tmp"
        )

        summary.to_csv(
            temporary_summary,
            index=False,
        )

        temporary_summary.replace(
            summary_path
        )


def main():
    args = parse_arguments()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input file not found: {args.input}"
        )

    if args.limit <= 0:
        raise ValueError(
            "--limit must be greater than zero."
        )

    if args.delay < 0:
        raise ValueError(
            "--delay cannot be negative."
        )

    candidates = pd.read_csv(
        args.input
    )

    if candidates.empty:
        raise ValueError(
            "Candidate dataset is empty."
        )

    if "url" not in candidates.columns:
        raise ValueError(
            "Input dataset must contain a 'url' column."
        )

    candidates["url"] = (
        candidates["url"]
        .astype(str)
        .str.strip()
    )

    if candidates["url"].duplicated().any():
        raise ValueError(
            "Candidate dataset contains duplicate URLs."
        )

    # -----------------------------------------
    # Load observations from previous runs.
    # -----------------------------------------

    if args.output.exists():

        previous = pd.read_csv(
            args.output
        )

        if "url" not in previous.columns:
            raise ValueError(
                "Existing audit output does not "
                "contain a 'url' column."
            )

        previous["url"] = (
            previous["url"]
            .astype(str)
            .str.strip()
        )

        previous = (
            previous
            .drop_duplicates(
                subset=["url"],
                keep="last",
            )
            .copy()
        )

    else:

        previous = pd.DataFrame()

    if previous.empty:

        completed_urls = set()

    else:

        completed_urls = set(
            previous["url"]
        )

    # -----------------------------------------
    # Select only previously unaudited URLs.
    # -----------------------------------------

    remaining = (
        candidates[
            ~candidates["url"].isin(
                completed_urls
            )
        ]
        .copy()
    )

    selected = (
        remaining
        .head(args.limit)
        .copy()
    )

    total_candidates = len(
        candidates
    )

    previously_audited = len(
        completed_urls
    )

    print()
    print(
        "V1.1 RESUMABLE LIVE WEBSITE AUDIT"
    )
    print("=" * 70)

    print(
        f"Input: {args.input}"
    )

    print(
        f"Output: {args.output}"
    )

    print(
        f"Total candidates: {total_candidates}"
    )

    print(
        f"Previously audited: "
        f"{previously_audited}"
    )

    print(
        f"Currently remaining: "
        f"{len(remaining)}"
    )

    print(
        f"Selected this run: "
        f"{len(selected)}"
    )

    print(
        f"Delay: {args.delay} seconds"
    )

    print()

    if selected.empty:

        print(
            "No unaudited candidate URLs remain."
        )

        if not previous.empty:

            save_progress(
                previous,
                args.output,
                args.summary,
            )

        return

    # Preserve all previous observations.
    accumulated_rows = []

    if not previous.empty:

        accumulated_rows.extend(
            previous.to_dict(
                orient="records"
            )
        )

    completed_this_run = 0

    for _, row in selected.iterrows():

        url = str(
            row["url"]
        ).strip()

        print(
            f"[{completed_this_run + 1}/"
            f"{len(selected)}] "
            f"Auditing: {url}"
        )

        try:

            result = audit_live_url(
                url
            )

            audit_data = (
                live_result_to_dict(
                    result
                )
            )

            combined = (
                row.to_dict()
            )

            combined.update(
                audit_data
            )

            accumulated_rows.append(
                combined
            )

            completed_this_run += 1

            print(
                "    "
                f"live_status="
                f"{result.live_status}"
            )

            print(
                "    "
                f"behavioural_eligible="
                f"{result.behavioural_eligible}"
            )

            # Save after every completed URL.
            accumulated_dataframe = (
                pd.DataFrame(
                    accumulated_rows
                )
            )

            save_progress(
                accumulated_dataframe,
                args.output,
                args.summary,
            )

        except KeyboardInterrupt:

            print()
            print(
                "Audit interrupted by user."
            )
            print(
                "Completed observations have "
                "already been saved."
            )
            raise

        except Exception as error:

            print(
                "    Unexpected audit error: "
                f"{type(error).__name__}: "
                f"{error}"
            )

            print(
                "    This URL was not marked "
                "complete and will be retried "
                "on a future run."
            )

        if (
            completed_this_run
            < len(selected)
        ):
            time.sleep(
                max(
                    0.0,
                    args.delay,
                )
            )

    # -----------------------------------------
    # Read the authoritative saved result.
    # -----------------------------------------

    final_dataframe = pd.read_csv(
        args.output
    )

    final_dataframe = (
        final_dataframe
        .drop_duplicates(
            subset=["url"],
            keep="last",
        )
        .copy()
    )

    summary = build_summary(
        final_dataframe
    )

    total_completed = len(
        final_dataframe
    )

    total_remaining = (
        total_candidates
        - total_completed
    )

    print()
    print("=" * 70)
    print(
        "BATCH COMPLETE"
    )
    print("=" * 70)

    print()
    print(
        f"Completed this run: "
        f"{completed_this_run}"
    )

    print(
        f"Total audited: "
        f"{total_completed}/"
        f"{total_candidates}"
    )

    print(
        f"Remaining: "
        f"{total_remaining}"
    )

    print()
    print(
        "OVERALL STATUS"
    )

    print(
        summary.to_string(
            index=False
        )
    )

    if (
        "behavioural_eligible"
        in final_dataframe.columns
    ):

        eligible_count = int(
            pd.to_numeric(
                final_dataframe[
                    "behavioural_eligible"
                ],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        print()
        print(
            "Behavioural/hybrid eligible: "
            f"{eligible_count}/"
            f"{total_completed}"
        )

    if {
        "scam_category",
        "live_status",
    }.issubset(
        final_dataframe.columns
    ):

        print()
        print(
            "STATUS BY CATEGORY"
        )

        category_status = (
            pd.crosstab(
                final_dataframe[
                    "scam_category"
                ],
                final_dataframe[
                    "live_status"
                ],
            )
        )

        print(
            category_status.to_string()
        )

    print()
    print(
        f"Detailed output: "
        f"{args.output}"
    )

    print(
        f"Summary output: "
        f"{args.summary}"
    )


if __name__ == "__main__":
    main()