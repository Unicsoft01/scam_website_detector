from __future__ import annotations

# from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import (
    AnalysisResult,
    BehaviouralObservation,
    HeuristicObservation,
    Scan,
    ScanEvent,
    SystemLog,
    utc_now,
)


class ScanRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session

    def create_scan(
        self,
        submitted_url: str,
        normalized_url: str,
        url_hash: str,
        registrable_domain: Optional[str],
    ) -> Scan:

        scan = Scan(
            submitted_url=submitted_url,
            normalized_url=normalized_url,
            url_hash=url_hash,
            registrable_domain=(
                registrable_domain
            ),
            scan_status="processing",
        )

        self.session.add(
            scan
        )

        self.session.flush()

        return scan

    def update_normalized_scan(
        self,
        scan: Scan,
        normalized_url: str,
        url_hash: str,
        registrable_domain: Optional[str],
    ) -> None:

        scan.normalized_url = (
            normalized_url
        )

        scan.url_hash = url_hash

        scan.registrable_domain = (
            registrable_domain
        )

        self.session.flush()

    def set_behavioural_available(
        self,
        scan: Scan,
        available: bool,
    ) -> None:

        scan.behavioural_available = (
            available
        )

        self.session.flush()

    def save_heuristic_observation(
        self,
        scan_id: int,
        feature_data: Optional[dict],
        extraction_status: str,
        extraction_time_ms: Optional[float],
        failure_reason: Optional[str] = None,
    ) -> HeuristicObservation:

        observation = (
            HeuristicObservation(
                scan_id=scan_id,

                extraction_status=(
                    extraction_status
                ),

                feature_data=feature_data,

                feature_count=(
                    len(feature_data)
                    if feature_data
                    is not None
                    else None
                ),

                extraction_time_ms=(
                    extraction_time_ms
                ),

                failure_reason=(
                    failure_reason
                ),
            )
        )

        self.session.add(
            observation
        )

        self.session.flush()

        return observation

    def save_behavioural_observation(
        self,
        scan_id: int,
        feature_data: Optional[dict],
        extraction_status: str,
        observation_window_ms: Optional[float],
        extraction_time_ms: Optional[float],
        failure_reason: Optional[str] = None,
    ) -> BehaviouralObservation:

        observation = (
            BehaviouralObservation(
                scan_id=scan_id,

                extraction_status=(
                    extraction_status
                ),

                feature_data=feature_data,

                feature_count=(
                    len(feature_data)
                    if feature_data
                    is not None
                    else None
                ),

                observation_window_ms=(
                    observation_window_ms
                ),

                extraction_time_ms=(
                    extraction_time_ms
                ),

                failure_reason=(
                    failure_reason
                ),
            )
        )

        self.session.add(
            observation
        )

        self.session.flush()

        return observation

    def add_event(
        self,
        scan_id: int,
        event_type: str,
        event_name: Optional[str] = None,
        event_data: Optional[dict] = None,
    ) -> ScanEvent:

        event = ScanEvent(
            scan_id=scan_id,
            event_type=event_type,
            event_name=event_name,
            event_data=event_data,
        )

        self.session.add(
            event
        )

        self.session.flush()

        return event

    def save_analysis_result(
        self,
        scan_id: int,
        configuration: str,
        scam_probability: float,
        threshold_used: float,
        predicted_label: int,
        model_version: str,
        response_time_ms: float,
        evidence_status: str,
    ) -> AnalysisResult:

        result = AnalysisResult(
            scan_id=scan_id,

            configuration=configuration,

            scam_probability=float(
                scam_probability
            ),

            threshold_used=float(
                threshold_used
            ),

            predicted_label=int(
                predicted_label
            ),

            model_version=model_version,

            response_time_ms=float(
                response_time_ms
            ),

            evidence_status=(
                evidence_status
            ),
        )

        self.session.add(
            result
        )

        self.session.flush()

        return result

    def add_log(
        self,
        level: str,
        component: str,
        message: str,
        scan_id: Optional[int] = None,
        details: Optional[dict] = None,
    ) -> SystemLog:

        log = SystemLog(
            scan_id=scan_id,
            level=level,
            component=component,
            message=message,
            details=details,
        )

        self.session.add(
            log
        )

        self.session.flush()

        return log

    def complete_scan(
        self,
        scan: Scan,
    ) -> None:

        scan.scan_status = "completed"

        scan.completed_at = (
            utc_now()
        )

        self.session.flush()

    def fail_scan(
        self,
        scan: Scan,
        error_code: str,
        error_message: str,
    ) -> None:

        scan.scan_status = "failed"

        scan.error_code = (
            error_code
        )

        scan.error_message = (
            error_message
        )

        scan.completed_at = (
            utc_now()
        )

        self.session.flush()

    def partial_scan(
        self,
        scan: Scan,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:

        scan.scan_status = "partial"

        scan.error_code = error_code
        scan.error_message = (
            error_message
        )

        scan.completed_at = (
            utc_now()
        )

        self.session.flush()

    def commit(
        self,
    ) -> None:

        self.session.commit()

    def rollback(
        self,
    ) -> None:

        self.session.rollback()