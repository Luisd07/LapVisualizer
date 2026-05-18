"""Shared FastAPI dependencies and entity lookup helpers."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app import models
from backend.app.core.db import get_db

DbSession = Annotated[Session, Depends(get_db)]


def get_session_or_404(db: Session, session_id: str) -> models.Session:
    """Return a session with its drivers and laps eagerly loaded.

    Args:
        db: An active database session.
        session_id: The identifier of the session to load.

    Returns:
        The matching session.

    Raises:
        HTTPException: With status 404 when no session has that id.
    """
    statement = (
        select(models.Session)
        .where(models.Session.id == session_id)
        .options(selectinload(models.Session.drivers).selectinload(models.Driver.laps))
    )
    session = db.scalar(statement)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session
