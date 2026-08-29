from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.database.database import engine

from app.api.routes import router


app = FastAPI(
    title=settings.app_name,
    description="Real-time scam website detection using heuristic and behavioural analysis.",
    version="1.0.0",
)

# Include the API router with a prefix of "/api"
app.include_router(
    router,
    prefix="/api"
)


@app.get("/")
def home():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_env
    }


@app.get("/health")
def health_check():
    database_status = "unavailable"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            database_status = "connected"
    except Exception:
        database_status = "unavailable"

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "database": database_status
    }