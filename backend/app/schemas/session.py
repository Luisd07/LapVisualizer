"""Pydantic schemas describing practice and race sessions."""

from datetime import datetime

from pydantic import Field

from backend.app.schemas.base import PydanticSchema
from backend.app.schemas.driver import DriverSummary


class SessionUploadResponse(PydanticSchema):
    """Returned immediately after a timing log is uploaded."""

    session_id: str
    session_name: str
    run_number: int | None = None
    track_name: str | None = None
    total_laps: int
    driver_count: int
    uploaded_at: datetime
    duplicate: bool = False
    warnings: list[str] = Field(default_factory=list)


class SessionSummary(PydanticSchema):
    """Lightweight session record — used when listing saved sessions."""

    session_id: str
    session_name: str
    run_number: int | None = None
    track_name: str | None = None
    total_laps: int
    driver_count: int
    uploaded_at: datetime


class SessionDetail(PydanticSchema):
    """Full session detail — used in the dashboard view."""

    session_id: str
    session_name: str
    run_number: int | None = None
    track_name: str | None = None
    track_length: float | None = None
    flag_status: str | None = None
    race_time_seconds: float | None = None
    time_of_day: str | None = None
    session_date: str | None = None
    total_laps: int
    driver_count: int
    uploaded_at: datetime
    drivers: list[DriverSummary] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
