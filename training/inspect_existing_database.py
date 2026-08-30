from sqlalchemy import (
    inspect,
    text,
)

from app.database.session import (
    engine,
)


TARGET_TABLES = [
    "scans",
    "heuristic_observations",
    "behavioural_observations",
    "scan_events",
    "analysis_results",
    "system_logs",
]


def main():

    print()

    print(
        "PHASE 23 — EXISTING DATABASE INSPECTION"
    )

    print(
        "=" * 72
    )

    inspector = inspect(
        engine
    )

    existing_tables = set(
        inspector.get_table_names()
    )

    print(
        "Existing database tables:"
    )

    if not existing_tables:

        print(
            "  None"
        )

    else:

        for table in sorted(
            existing_tables
        ):

            print(
                f"  {table}"
            )

    print()

    with engine.connect() as connection:

        for table in TARGET_TABLES:

            print(
                f"[{table}]"
            )

            if table not in existing_tables:

                print(
                    "  Status: does not exist"
                )

                print()

                continue

            columns = (
                inspector.get_columns(
                    table
                )
            )

            print(
                "  Columns:"
            )

            for column in columns:

                print(
                    (
                        "   - "
                        f"{column['name']} "
                        f"({column['type']})"
                    )
                )

            # Table names here come only from
            # the hard-coded TARGET_TABLES list.
            count = connection.execute(
                text(
                    f"SELECT COUNT(*) "
                    f"FROM `{table}`"
                )
            ).scalar_one()

            print(
                f"  Rows: {count}"
            )

            print()

    print(
        "=" * 72
    )

    print(
        (
            "Inspection complete. "
            "No tables were changed."
        )
    )


if __name__ == "__main__":
    main()