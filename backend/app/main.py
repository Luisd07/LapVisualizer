"""FastAPI application entry point for LapVisualizer.

The database schema is owned by Alembic — run `alembic upgrade head` before
starting the app (the Docker image does this automatically).
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.deps import DbSession
from backend.app.api.routes import analysis, drivers, sessions
from backend.app.core.config import settings
from backend.app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="LapVisualizer",
    version="0.1.0",
    summary="Parse RMonitor timing logs and analyse lap data.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api")
app.include_router(drivers.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")


@app.get("/health", tags=["meta"])
def health(db: DbSession) -> dict[str, str]:
    """Report service liveness, including database connectivity."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "ok"}
