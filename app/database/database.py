from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


# Dependency to get database session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()