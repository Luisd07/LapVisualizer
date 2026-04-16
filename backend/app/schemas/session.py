from datetime import datetime
from backend.app.schemas.base import PydanticSchema
from backend.app.schemas.driver import DriverSummary


class SessionUploadResponse(PydanticSchema):
    """Returned immediately after a log is uploaded."""

    session_id: str
    session_name: str
    track_name: str | None = None
    total_laps: int
    driver_count: int
    uploaded_at: datetime


class SessionSummary(PydanticSchema):
    """Lightweight — used when listing saved sessions."""

    session_id: str
    session_name: str
    track_name: str | None = None
    total_laps: int
    driver_count: int
    uploaded_at: datetime


class SessionDetail(PydanticSchema):
    """Full session — used in dashboard view."""

    session_id: str
    session_name: str
    track_name: str | None = None
    track_length: float | None = None
    total_laps: int
    uploaded_at: datetime
    drivers: list[DriverSummary] = []
