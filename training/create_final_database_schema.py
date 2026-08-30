from sqlalchemy import (
    inspect,
)

from app.database.base import (
    Base,
)

from app.database.session import (
    engine,
)

# Import models so SQLAlchemy registers
# all tables in Base.metadata.
from app.database import models  # noqa: F401


EXPECTED_TABLES = {
    "scans",
    "heuristic_observations",
    "behavioural_observations",
    "scan_events",
    "analysis_results",
    "system_logs",
}


def main():

    print()

    print(
        "PHASE 23 — CREATE FINAL DATABASE SCHEMA"
    )

    print(
        "=" * 72
    )

    before = set(
        inspect(
            engine
        ).get_table_names()
    )

    print(
        "Target tables already present:"
    )

    present = sorted(
        EXPECTED_TABLES
        & before
    )

    if present:

        for table in present:

            print(
                f"  {table}"
            )

    else:

        print(
            "  None"
        )

    print()

    Base.metadata.create_all(
        bind=engine
    )

    after = set(
        inspect(
            engine
        ).get_table_names()
    )

    missing = (
        EXPECTED_TABLES
        - after
    )

    if missing:

        raise RuntimeError(
            (
                "Database creation finished "
                "but required tables are "
                "missing: "
                f"{sorted(missing)}"
            )
        )

    newly_created = (
        EXPECTED_TABLES
        - before
    )

    print(
        "Newly created tables:"
    )

    if newly_created:

        for table in sorted(
            newly_created
        ):

            print(
                f"  {table}"
            )

    else:

        print(
            "  None"
        )

    print()

    print(
        "All required table names exist."
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        (
            "create_all() does not alter an "
            "older incompatible table. "
            "Run the Phase 23 verification "
            "script next."
        )
    )


if __name__ == "__main__":
    main()