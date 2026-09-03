from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.database.models import (
    AnalysisResult,
    BehaviouralObservation,
    HeuristicObservation,
    Scan,
)


class ScanQueryService:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session

    # =================================================
    # Individual scan
    # =================================================

    def get_scan(
        self,
        scan_id: int,
    ) -> Scan | None:

        statement = (
            select(Scan)
            .where(
                Scan.scan_id
                == scan_id
            )
        )

        return (
            self.session
            .execute(statement)
            .scalar_one_or_none()
        )

    # =================================================
    # Analysis results
    # =================================================

    def get_results(
        self,
        scan_id: int,
    ) -> list[AnalysisResult]:

        statement = (
            select(
                AnalysisResult
            )
            .where(
                AnalysisResult.scan_id
                == scan_id
            )
            .order_by(
                AnalysisResult.result_id
            )
        )

        return list(
            self.session
            .execute(statement)
            .scalars()
            .all()
        )

    # =================================================
    # Heuristic observation
    # =================================================

    def get_heuristic_observation(
        self,
        scan_id: int,
    ) -> HeuristicObservation | None:

        statement = (
            select(
                HeuristicObservation
            )
            .where(
                HeuristicObservation.scan_id
                == scan_id
            )
        )

        return (
            self.session
            .execute(statement)
            .scalar_one_or_none()
        )

    # =================================================
    # Behavioural observation
    # =================================================

    def get_behavioural_observation(
        self,
        scan_id: int,
    ) -> BehaviouralObservation | None:

        statement = (
            select(
                BehaviouralObservation
            )
            .where(
                BehaviouralObservation.scan_id
                == scan_id
            )
        )

        return (
            self.session
            .execute(statement)
            .scalar_one_or_none()
        )

    # =================================================
    # Scan history
    # =================================================

    def get_history(
        self,
        limit: int,
        offset: int,
    ) -> tuple[int, list[Scan]]:

        total_statement = (
            select(
                func.count(
                    Scan.scan_id
                )
            )
        )

        total = int(
            self.session
            .execute(
                total_statement
            )
            .scalar_one()
        )

        history_statement = (
            select(Scan)
            .order_by(
                Scan.initiated_at.desc()
            )
            .offset(
                offset
            )
            .limit(
                limit
            )
        )

        scans = list(
            self.session
            .execute(
                history_statement
            )
            .scalars()
            .all()
        )

        return (
            total,
            scans,
        )