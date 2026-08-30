from app.database.base import (
    Base,
)

from app.database import models  # noqa: F401


EXPECTED_TABLES = {
    "scans",
    "heuristic_observations",
    "behavioural_observations",
    "scan_events",
    "analysis_results",
    "system_logs",
}


def test_all_final_tables_registered():

    tables = set(
        Base.metadata.tables.keys()
    )

    assert (
        EXPECTED_TABLES
        .issubset(
            tables
        )
    )


def test_scans_primary_key():

    table = Base.metadata.tables[
        "scans"
    ]

    primary_keys = {
        column.name
        for column in (
            table.primary_key.columns
        )
    }

    assert primary_keys == {
        "scan_id"
    }


def test_heuristic_scan_foreign_key():

    table = Base.metadata.tables[
        "heuristic_observations"
    ]

    foreign_keys = {
        str(
            foreign_key.target_fullname
        )
        for foreign_key in (
            table.foreign_keys
        )
    }

    assert (
        "scans.scan_id"
        in foreign_keys
    )


def test_behavioural_scan_foreign_key():

    table = Base.metadata.tables[
        "behavioural_observations"
    ]

    foreign_keys = {
        str(
            foreign_key.target_fullname
        )
        for foreign_key in (
            table.foreign_keys
        )
    }

    assert (
        "scans.scan_id"
        in foreign_keys
    )


def test_analysis_result_relationship():

    table = Base.metadata.tables[
        "analysis_results"
    ]

    foreign_keys = {
        str(
            foreign_key.target_fullname
        )
        for foreign_key in (
            table.foreign_keys
        )
    }

    assert (
        "scans.scan_id"
        in foreign_keys
    )


def test_analysis_unique_constraint():

    table = Base.metadata.tables[
        "analysis_results"
    ]

    constraint_names = {
        constraint.name
        for constraint in table.constraints
        if constraint.name
    }

    assert (
        "uq_analysis_scan_configuration"
        in constraint_names
    )


def test_system_logs_scan_nullable():

    table = Base.metadata.tables[
        "system_logs"
    ]

    assert (
        table.c.scan_id.nullable
        is True
    )