"""Pydantic schemas describing individual laps."""

from backend.app.schemas.base import PydanticSchema


class LapSchema(PydanticSchema):
    """A single completed lap (lap-level fields only)."""

    lap_number: int
    lap_time_seconds: float
    total_time_seconds: float
