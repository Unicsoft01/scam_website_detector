from app.database.database import SessionLocal
from app.database.models import Scan


db = SessionLocal()

try:
    scan = db.query(Scan).filter(
        Scan.url == "https://example.com"
    ).first()

    if scan:
        db.delete(scan)
        db.commit()
        print("Test record deleted successfully.")
    else:
        print("No test record found.")

finally:
    db.close()