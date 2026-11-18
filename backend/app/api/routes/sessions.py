"""Endpoints for uploading, listing, and managing timing sessions."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app import models
from backend.app.api.deps import DbSession, get_session_or_404
from backend.app.api.mappers import (
    to_session_detail,
    to_session_summary,
    to_upload_response,
)
from backend.app.core.config import settings
from backend.app.schemas.session import (
    SessionDetail,
    SessionSummary,
    SessionUploadResponse,
)
from backend.app.services import ingest

router = APIRouter(prefix="/sessions", tags=["sessions"])

_BYTES_PER_MB = 1024 * 1024
_CHUNK_SIZE = _BYTES_PER_MB


def _read_limited(file: UploadFile) -> bytes:
    """Read the upload in chunks, rejecting it as soon as it exceeds the size limit."""
    limit = settings.max_upload_mb * _BYTES_PER_MB
    chunks: list[bytes] = []
    total = 0
    while chunk := file.file.read(_CHUNK_SIZE):
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File exceeds the {settings.max_upload_mb} MB limit.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post(
    "/upload",
    response_model=SessionUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_session(
    db: DbSession,
    file: Annotated[UploadFile, File(description="An RMonitor timing log.")],
) -> SessionUploadResponse:
    """Parse an uploaded RMonitor log and store its session, drivers, and laps."""
    raw = _read_limited(file)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    logger.info("Received upload {!r} ({} bytes)", file.filename, len(raw))
    try:
        session, duplicate = ingest.ingest_log(
            db,
            filename=file.filename or "upload.rmon.log",
            raw=raw,
        )
    except ingest.InvalidTimingLogError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    return to_upload_response(session, duplicate=duplicate)


@router.get("", response_model=list[SessionSummary])
def list_sessions(db: DbSession) -> list[SessionSummary]:
    """List every stored session, newest upload first."""
    statement = (
        select(models.Session)
        .order_by(models.Session.uploaded_at.desc())
        .options(selectinload(models.Session.drivers).selectinload(models.Driver.laps))
    )
    return [to_session_summary(session) for session in db.scalars(statement)]


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: str, db: DbSession) -> SessionDetail:
    """Return one session with its driver summaries."""
    return to_session_detail(get_session_or_404(db, session_id))


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: DbSession) -> None:
    """Delete a session along with all of its drivers and laps."""
    db.delete(get_session_or_404(db, session_id))
    db.commit()
    logger.info("Deleted session {}", session_id)
