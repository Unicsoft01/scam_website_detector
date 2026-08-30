from datetime import (
    datetime,
    timezone,
)

from typing import (
    Optional,
)

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


def utc_now() -> datetime:
    """
    Store UTC as a naive DATETIME value.

    MySQL DATETIME itself does not preserve
    timezone information, so the application
    consistently supplies UTC.
    """

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


class Scan(Base):

    __tablename__ = "scans"

    scan_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    submitted_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    url_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    registrable_domain: Mapped[
        Optional[str]
    ] = mapped_column(
        String(253),
        nullable=True,
    )

    scan_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
    )

    behavioural_available: Mapped[
        Optional[bool]
    ] = mapped_column(
        Boolean,
        nullable=True,
    )

    error_code: Mapped[
        Optional[str]
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    error_message: Mapped[
        Optional[str]
    ] = mapped_column(
        Text,
        nullable=True,
    )

    initiated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    completed_at: Mapped[
        Optional[datetime]
    ] = mapped_column(
        DateTime,
        nullable=True,
    )

    heuristic_observation: Mapped[
        Optional["HeuristicObservation"]
    ] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        uselist=False,
    )

    behavioural_observation: Mapped[
        Optional["BehaviouralObservation"]
    ] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        uselist=False,
    )

    events: Mapped[
        list["ScanEvent"]
    ] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    analysis_results: Mapped[
        list["AnalysisResult"]
    ] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    system_logs: Mapped[
        list["SystemLog"]
    ] = relationship(
        back_populates="scan",
    )

    __table_args__ = (
        Index(
            "ix_scans_url_hash",
            "url_hash",
        ),

        Index(
            "ix_scans_registrable_domain",
            "registrable_domain",
        ),

        Index(
            "ix_scans_status",
            "scan_status",
        ),

        Index(
            "ix_scans_initiated_at",
            "initiated_at",
        ),
    )


class HeuristicObservation(Base):

    __tablename__ = (
        "heuristic_observations"
    )

    observation_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    scan_id: Mapped[int] = mapped_column(
        BigInteger,

        ForeignKey(
            "scans.scan_id",
            ondelete="CASCADE",
        ),

        nullable=False,

        unique=True,
    )

    extraction_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="complete",
    )

    feature_data: Mapped[
        Optional[dict]
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    feature_count: Mapped[
        Optional[int]
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    extraction_time_ms: Mapped[
        Optional[float]
    ] = mapped_column(
        Float,
        nullable=True,
    )

    failure_reason: Mapped[
        Optional[str]
    ] = mapped_column(
        Text,
        nullable=True,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    scan: Mapped["Scan"] = relationship(
        back_populates=(
            "heuristic_observation"
        )
    )

    __table_args__ = (
        Index(
            "ix_heuristic_status",
            "extraction_status",
        ),
    )


class BehaviouralObservation(Base):

    __tablename__ = (
        "behavioural_observations"
    )

    observation_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    scan_id: Mapped[int] = mapped_column(
        BigInteger,

        ForeignKey(
            "scans.scan_id",
            ondelete="CASCADE",
        ),

        nullable=False,

        unique=True,
    )

    extraction_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="complete",
    )

    feature_data: Mapped[
        Optional[dict]
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    feature_count: Mapped[
        Optional[int]
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    observation_window_ms: Mapped[
        Optional[float]
    ] = mapped_column(
        Float,
        nullable=True,
    )

    extraction_time_ms: Mapped[
        Optional[float]
    ] = mapped_column(
        Float,
        nullable=True,
    )

    failure_reason: Mapped[
        Optional[str]
    ] = mapped_column(
        Text,
        nullable=True,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    scan: Mapped["Scan"] = relationship(
        back_populates=(
            "behavioural_observation"
        )
    )

    __table_args__ = (
        Index(
            "ix_behavioural_status",
            "extraction_status",
        ),
    )


class ScanEvent(Base):

    __tablename__ = "scan_events"

    event_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    scan_id: Mapped[int] = mapped_column(
        BigInteger,

        ForeignKey(
            "scans.scan_id",
            ondelete="CASCADE",
        ),

        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    event_name: Mapped[
        Optional[str]
    ] = mapped_column(
        String(128),
        nullable=True,
    )

    event_data: Mapped[
        Optional[dict]
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    scan: Mapped["Scan"] = relationship(
        back_populates="events"
    )

    __table_args__ = (
        Index(
            "ix_scan_events_scan_time",
            "scan_id",
            "occurred_at",
        ),

        Index(
            "ix_scan_events_type",
            "event_type",
        ),
    )


class AnalysisResult(Base):

    __tablename__ = "analysis_results"

    result_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    scan_id: Mapped[int] = mapped_column(
        BigInteger,

        ForeignKey(
            "scans.scan_id",
            ondelete="CASCADE",
        ),

        nullable=False,
    )

    configuration: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    scam_probability: Mapped[
        Optional[float]
    ] = mapped_column(
        Float,
        nullable=True,
    )

    threshold_used: Mapped[
        Optional[float]
    ] = mapped_column(
        Float,
        nullable=True,
    )

    predicted_label: Mapped[
        Optional[int]
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    model_version: Mapped[
        Optional[str]
    ] = mapped_column(
        String(32),
        nullable=True,
    )

    response_time_ms: Mapped[
        Optional[float]
    ] = mapped_column(
        Float,
        nullable=True,
    )

    evidence_status: Mapped[
        Optional[str]
    ] = mapped_column(
        String(64),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    scan: Mapped["Scan"] = relationship(
        back_populates=(
            "analysis_results"
        )
    )

    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "configuration",
            name=(
                "uq_analysis_scan_configuration"
            ),
        ),

        Index(
            "ix_analysis_configuration",
            "configuration",
        ),

        Index(
            "ix_analysis_label",
            "predicted_label",
        ),

        Index(
            "ix_analysis_created_at",
            "created_at",
        ),
    )


class SystemLog(Base):

    __tablename__ = "system_logs"

    log_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    scan_id: Mapped[
        Optional[int]
    ] = mapped_column(
        BigInteger,

        ForeignKey(
            "scans.scan_id",
            ondelete="SET NULL",
        ),

        nullable=True,
    )

    level: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    component: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    details: Mapped[
        Optional[dict]
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )

    scan: Mapped[
        Optional["Scan"]
    ] = relationship(
        back_populates="system_logs"
    )

    __table_args__ = (
        Index(
            "ix_system_logs_scan",
            "scan_id",
        ),

        Index(
            "ix_system_logs_level_time",
            "level",
            "created_at",
        ),

        Index(
            "ix_system_logs_component",
            "component",
        ),
    )