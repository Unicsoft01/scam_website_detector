from pathlib import Path
import importlib
import sys


print("=" * 60)
print("SCAM WEBSITE DETECTOR HEALTH CHECK")
print("=" * 60)


# Number of checks that failed. Used to set the exit code.
failures = 0



# -----------------------------
# Python Version
# -----------------------------

print("\nPYTHON CHECK")

if sys.version_info >= (3, 11):

    print(
        "[PASS] Python:",
        sys.version.split()[0]
    )

else:

    failures += 1

    print(
        "[FAIL] Python 3.11+ required"
    )



# -----------------------------
# Required Packages
# -----------------------------

print("\nDEPENDENCY CHECK")


packages = [

    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pymysql",
    "pandas",
    "numpy",
    "sklearn",
    "joblib",
    "bs4",
    "playwright",
    "pydantic_settings"

]


for package in packages:

    try:

        importlib.import_module(package)

        print(
            "[PASS]",
            package
        )


    except Exception:

        failures += 1

        print(
            "[FAIL]",
            package
        )



# -----------------------------
# Model Files
# -----------------------------

print("\nMODEL CHECK")


models = [

    "models/rf_heuristic.joblib",

    "models/rf_behavioural.joblib",

    "models/hybrid_fusion_config.json"

]


for model in models:

    if Path(model).exists():

        print(
            "[PASS]",
            model
        )

    else:

        failures += 1

        print(
            "[FAIL]",
            model
        )



# -----------------------------
# Application Files
# -----------------------------

print("\nAPPLICATION FILE CHECK")


files = [

    "app/main.py",

    "app/services/scan_service.py",

    "app/services/prediction_service.py",

    "app/database/database.py",

    "app/database/models.py"

]


for file in files:

    if Path(file).exists():

        print(
            "[PASS]",
            file
        )

    else:

        failures += 1

        print(
            "[FAIL]",
            file
        )



# -----------------------------
# Playwright Chromium
# -----------------------------

print("\nBROWSER ENGINE CHECK")


try:

    from playwright.sync_api import sync_playwright


    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        browser.close()


    print(
        "[PASS] Chromium available"
    )


except Exception as e:

    failures += 1

    print(
        "[FAIL] Chromium unavailable"
    )

    print(e)



# -----------------------------
# Database Check
# -----------------------------

print("\nDATABASE CHECK")


try:

    from app.database.database import engine

    from sqlalchemy import text


    connection = engine.connect()


    connection.execute(
        text(
            "SELECT 1"
        )
    )


    connection.close()


    print(
        "[PASS] MySQL connection successful"
    )


except Exception as e:

    failures += 1

    print(
        "[FAIL] Database connection failed"
    )

    print(e)



# -----------------------------
# Table Check
# -----------------------------

print("\nDATABASE TABLE CHECK")


required_tables = [

    "scans",

    "heuristic_observations",

    "behavioural_observations",

    "scan_events"

]


try:


    from app.database.database import engine

    from sqlalchemy import inspect


    inspector = inspect(engine)


    existing = inspector.get_table_names()



    for table in required_tables:


        if table in existing:

            print(
                "[PASS]",
                table
            )

        else:

            failures += 1

            print(
                "[FAIL]",
                table
            )


except Exception as e:

    failures += 1

    print(
        "[FAIL] Could not read database tables"
    )

    print(e)



# -----------------------------
# Final Status
# -----------------------------


print("\n")

print("=" * 60)


print(
    "SYSTEM CHECK COMPLETED"
)


if failures:

    print(
        f"RESULT: {failures} check(s) FAILED"
    )

else:

    print(
        "RESULT: all checks passed"
    )


print("=" * 60)


# Exit code 0 = ready, 1 = at least one check failed.
sys.exit(1 if failures else 0)