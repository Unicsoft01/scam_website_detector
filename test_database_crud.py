import hashlib

from app.database.database import (
    SessionLocal,
)

from app.database.models import (
    Scan,
)


def test_scan_crud():

    db = SessionLocal()

    test_url = "https://example.com"

    test_url_hash = hashlib.sha256(
        test_url.encode("utf-8")
    ).hexdigest()

    try:

        # -----------------------------------------
        # Clean up earlier test records
        # -----------------------------------------

        existing_records = (
            db.query(Scan)
            .filter(
                Scan.submitted_url
                == test_url
            )
            .all()
        )

        for record in existing_records:
            db.delete(record)

        db.commit()

        # -----------------------------------------
        # CREATE
        # -----------------------------------------

        scan = Scan(
            submitted_url=test_url,
            normalized_url=test_url,
            url_hash=test_url_hash,
            registrable_domain="example.com",
            scan_status="pending",
            behavioural_available=False,
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        assert scan.scan_id is not None

        assert (
            scan.url_hash
            == test_url_hash
        )

        # -----------------------------------------
        # READ
        # -----------------------------------------

        saved_scan = (
            db.query(Scan)
            .filter(
                Scan.scan_id
                == scan.scan_id
            )
            .first()
        )

        assert saved_scan is not None

        assert (
            saved_scan.submitted_url
            == test_url
        )

        assert (
            saved_scan.normalized_url
            == test_url
        )

        assert (
            saved_scan.url_hash
            == test_url_hash
        )

        assert (
            saved_scan.registrable_domain
            == "example.com"
        )

        assert (
            saved_scan.scan_status
            == "pending"
        )

        # -----------------------------------------
        # UPDATE
        # -----------------------------------------

        saved_scan.scan_status = (
            "completed"
        )

        db.commit()
        db.refresh(saved_scan)

        assert (
            saved_scan.scan_status
            == "completed"
        )

        # -----------------------------------------
        # DELETE
        # -----------------------------------------

        scan_id = saved_scan.scan_id

        db.delete(saved_scan)
        db.commit()

        deleted_scan = (
            db.query(Scan)
            .filter(
                Scan.scan_id
                == scan_id
            )
            .first()
        )

        assert deleted_scan is None

    except Exception:

        db.rollback()
        raise

    finally:

        # -----------------------------------------
        # Safety cleanup
        # -----------------------------------------

        try:

            remaining_records = (
                db.query(Scan)
                .filter(
                    Scan.submitted_url
                    == test_url
                )
                .all()
            )

            for record in remaining_records:
                db.delete(record)

            db.commit()

        except Exception:

            db.rollback()

        finally:

            db.close()