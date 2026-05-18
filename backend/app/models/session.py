"""ORM model for an uploaded timing session."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base

if TYPE_CHECKING:
    from backend.app.models.driver import Driver


class Session(Base):
    """A single uploaded RMonitor log and its parsed metadata."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    run_number: Mapped[int | None]
    track_name: Mapped[str | None]
    track_length: Mapped[float | None]
    # Resolved from the final `$F` heartbeat and any `$I` init record.
    flag_status: Mapped[str | None]
    race_time_seconds: Mapped[float | None]
    time_of_day: Mapped[str | None]
    session_date: Mapped[str | None]
    source_filename: Mapped[str]
    content_hash: Mapped[str] = mapped_column(unique=True, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    # Non-fatal issues recorded while parsing the uploaded log.
    warnings: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        server_default=text("'[]'"),
    )

    drivers: Mapped[list[Driver]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
