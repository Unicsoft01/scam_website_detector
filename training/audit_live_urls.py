import argparse
from pathlib import Path
import time

import pandas as pd

from app.services.live_availability_service import (
    audit_live_url,
    live_result_to_dict,
)


DEFAULT_INPUT = Path(
    "data/processed/master_url_index.csv"
)

DEFAULT_OUTPUT = Path(
    "data/interim/live_url_audit.csv"
)

DEFAULT_SUMMARY = Path(
    "data/interim/live_url_audit_summary.csv"
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Controlled live-availability audit "
            "for candidate website URLs."
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
        default=20,
        help=(
            "Maximum number of records to audit. "
            "Default is deliberately small."
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


def main():
    args = parse_arguments()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input file not found: {args.input}"
        )

    dataframe = pd.read_csv(
        args.input
    )

    if "url" not in dataframe.columns:
        raise ValueError(
            "Input dataset must contain a 'url' column."
        )

    if args.limit <= 0:
        raise ValueError(
            "--limit must be greater than zero."
        )

    dataframe = (
        dataframe
        .head(
            args.limit
        )
        .copy()
    )

    print(
        "\nLIVE WEBSITE AVAILABILITY AUDIT"
    )

    print(
        "=" * 70
    )

    print(
        f"Input: {args.input}"
    )

    print(
        f"Records selected: {len(dataframe)}"
    )

    print(
        f"Delay: {args.delay} seconds"
    )

    print()

    audit_rows = []

    for position, row in (
        dataframe.iterrows()
    ):
        url = str(
            row["url"]
        ).strip()

        print(
            f"[{len(audit_rows) + 1}/"
            f"{len(dataframe)}] "
            f"Auditing: {url}"
        )

        result = (
            audit_live_url(
                url
            )
        )

        audit_data = (
            live_result_to_dict(
                result
            )
        )

        # Preserve original dataset metadata.
        combined = (
            row.to_dict()
        )

        combined.update(
            audit_data
        )

        audit_rows.append(
            combined
        )

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

        # Save progress after every URL.
        # If the audit is interrupted, completed
        # observations are not lost.
        output_dataframe = (
            pd.DataFrame(
                audit_rows
            )
        )

        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_dataframe.to_csv(
            args.output,
            index=False,
        )

        if (
            len(audit_rows)
            < len(dataframe)
        ):
            time.sleep(
                max(
                    0.0,
                    args.delay,
                )
            )

    # ---------------------------------
    # SUMMARY
    # ---------------------------------

    final_dataframe = pd.DataFrame(
        audit_rows
    )

    summary = (
        final_dataframe[
            "live_status"
        ]
        .value_counts(
            dropna=False
        )
        .rename_axis(
            "live_status"
        )
        .reset_index(
            name="count"
        )
    )

    summary["percentage"] = (
        summary["count"]
        / len(
            final_dataframe
        )
        * 100
    ).round(
        2
    )

    args.summary.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary.to_csv(
        args.summary,
        index=False,
    )

    print()

    print(
        "=" * 70
    )

    print(
        "AUDIT COMPLETE"
    )

    print(
        "=" * 70
    )

    print()

    print(
        summary.to_string(
            index=False
        )
    )

    print()

    eligible_count = int(
        final_dataframe[
            "behavioural_eligible"
        ].sum()
    )

    print(
        "Behavioural/hybrid eligible: "
        f"{eligible_count}/"
        f"{len(final_dataframe)}"
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