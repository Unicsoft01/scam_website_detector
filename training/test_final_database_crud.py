from hashlib import sha256

from app.database.models import (
    Scan,
    HeuristicObservation,
    BehaviouralObservation,
    ScanEvent,
    AnalysisResult,
    SystemLog,
)

from app.database.session import SessionLocal


def main():

    print()
    print("PHASE 23 — DATABASE CRUD INTEGRATION TEST")
    print("=" * 72)

    session = SessionLocal()

    try:

        test_url = "https://example.com/"

        scan = Scan(
            submitted_url=test_url,
            normalized_url=test_url,
            url_hash=sha256(
                test_url.encode("utf-8")
            ).hexdigest(),
            registrable_domain="example.com",
            scan_status="testing",
            behavioural_available=True,
        )

        session.add(scan)
        session.flush()

        print(
            f"Created test scan: {scan.scan_id}"
        )

        heuristic = HeuristicObservation(
            scan_id=scan.scan_id,
            extraction_status="complete",
            feature_data={
                "h_test_feature": 1
            },
            feature_count=1,
            extraction_time_ms=1.5,
        )

        behavioural = BehaviouralObservation(
            scan_id=scan.scan_id,
            extraction_status="complete",
            feature_data={
                "b_test_feature": 1
            },
            feature_count=1,
            observation_window_ms=1000.0,
            extraction_time_ms=2.0,
        )

        event = ScanEvent(
            scan_id=scan.scan_id,
            event_type="test_event",
            event_name="database_test",
            event_data={
                "purpose":
                    "Phase 23 CRUD verification"
            },
        )

        result = AnalysisResult(
            scan_id=scan.scan_id,
            configuration="hybrid",
            scam_probability=0.25,
            threshold_used=0.50,
            predicted_label=0,
            model_version="test",
            response_time_ms=3.0,
            evidence_status="complete",
        )

        log = SystemLog(
            scan_id=scan.scan_id,
            level="INFO",
            component="database_test",
            message=(
                "Phase 23 database integration "
                "test."
            ),
            details={
                "temporary": True
            },
        )

        session.add_all(
            [
                heuristic,
                behavioural,
                event,
                result,
                log,
            ]
        )

        session.commit()

        print(
            "Related records inserted successfully."
        )

        stored_scan = (
            session.query(Scan)
            .filter(
                Scan.scan_id
                == scan.scan_id
            )
            .one()
        )

        print(
            "Heuristic observations:",
            1 if stored_scan.heuristic_observation
            else 0,
        )

        print(
            "Behavioural observations:",
            1 if stored_scan.behavioural_observation
            else 0,
        )

        print(
            "Scan events:",
            len(stored_scan.events),
        )

        print(
            "Analysis results:",
            len(stored_scan.analysis_results),
        )

        print(
            "System logs:",
            len(stored_scan.system_logs),
        )

        # Remove the temporary test data.
        session.delete(
            stored_scan
        )

        session.commit()

        print()
        print(
            "Temporary test scan removed."
        )

        print(
            "PHASE 23 CRUD TEST: PASSED"
        )

    except Exception:

        session.rollback()
        raise

    finally:

        session.close()


if __name__ == "__main__":
    main()