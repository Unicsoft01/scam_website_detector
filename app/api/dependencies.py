from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.session import (
    SessionLocal,
)


def get_db() -> Generator[
    Session,
    None,
    None,
]:

    database = SessionLocal()

    try:

        yield database

    finally:

        database.close()




# \
from fastapi import (
    HTTPException,
    status,
)


def get_scan_service():

    # Phase 25 placeholder.
    #
    # Returning None allows FastAPI/Pydantic
    # to validate the request body first.
    #
    # Once the real Phase 24 runtime is
    # connected, this function will return
    # the constructed ScanService instance.

    return None