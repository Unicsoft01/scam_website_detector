from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Real-time scam website detection using heuristic and behavioural analysis.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_env
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env
    }