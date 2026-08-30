from sqlalchemy import (
    inspect,
)

from app.database.session import (
    engine,
)


EXPECTED_COLUMNS = {
    "scans": {
        "scan_id",
        "submitted_url",
        "normalized_url",
        "url_hash",
        "registrable_domain",
        "scan_status",
        "behavioural_available",
        "error_code",
        "error_message",
        "initiated_at",
        "completed_at",
    },

    "heuristic_observations": {
        "observation_id",
        "scan_id",
        "extraction_status",
        "feature_data",
        "feature_count",
        "extraction_time_ms",
        "failure_reason",
        "collected_at",
    },

    "behavioural_observations": {
        "observation_id",
        "scan_id",
        "extraction_status",
        "feature_data",
        "feature_count",
        "observation_window_ms",
        "extraction_time_ms",
        "failure_reason",
        "collected_at",
    },

    "scan_events": {
        "event_id",
        "scan_id",
        "event_type",
        "event_name",
        "event_data",
        "occurred_at",
    },

    "analysis_results": {
        "result_id",
        "scan_id",
        "configuration",
        "scam_probability",
        "threshold_used",
        "predicted_label",
        "model_version",
        "response_time_ms",
        "evidence_status",
        "created_at",
    },

    "system_logs": {
        "log_id",
        "scan_id",
        "level",
        "component",
        "message",
        "details",
        "created_at",
    },
}


def main():

    print()

    print(
        "PHASE 23 — FINAL DATABASE "
        "SCHEMA VERIFICATION"
    )

    print(
        "=" * 72
    )

    inspector = inspect(
        engine
    )

    tables = set(
        inspector.get_table_names()
    )

    failures = []

    for (
        table,
        expected_columns,
    ) in EXPECTED_COLUMNS.items():

        print(
            f"[{table}]"
        )

        if table not in tables:

            print(
                "  FAIL — table missing"
            )

            failures.append(
                f"Missing table: {table}"
            )

            print()

            continue

        actual_columns = {
            column[
                "name"
            ]
            for column in (
                inspector.get_columns(
                    table
                )
            )
        }

        missing_columns = (
            expected_columns
            - actual_columns
        )

        extra_columns = (
            actual_columns
            - expected_columns
        )

        if missing_columns:

            print(
                "  FAIL — missing columns:"
            )

            for column in sorted(
                missing_columns
            ):

                print(
                    f"    {column}"
                )

            failures.append(
                (
                    f"{table}: missing "
                    f"{sorted(missing_columns)}"
                )
            )

        else:

            print(
                "  Required columns: PASS"
            )

        if extra_columns:

            print(
                "  Extra columns found:"
            )

            for column in sorted(
                extra_columns
            ):

                print(
                    f"    {column}"
                )

        foreign_keys = (
            inspector.get_foreign_keys(
                table
            )
        )

        indexes = (
            inspector.get_indexes(
                table
            )
        )

        print(
            (
                "  Foreign keys: "
                f"{len(foreign_keys)}"
            )
        )

        for foreign_key in foreign_keys:

            print(
                (
                    "    "
                    f"{foreign_key.get('constrained_columns')} "
                    "-> "
                    f"{foreign_key.get('referred_table')}."
                    f"{foreign_key.get('referred_columns')}"
                )
            )

        print(
            (
                "  Indexes: "
                f"{len(indexes)}"
            )
        )

        for index in indexes:

            print(
                (
                    "    "
                    f"{index.get('name')}: "
                    f"{index.get('column_names')}"
                )
            )

        print()

    print(
        "=" * 72
    )

    if failures:

        print(
            "SCHEMA VERIFICATION: FAILED"
        )

        print()

        for failure in failures:

            print(
                f" - {failure}"
            )

        raise SystemExit(
            1
        )

    print(
        "SCHEMA VERIFICATION: PASSED"
    )


if __name__ == "__main__":
    main()