"""Pydantic schemas describing race-car drivers."""

from pydantic import Field

from backend.app.schemas.base import PydanticSchema
from backend.app.schemas.laps import LapSchema


class DriverSummary(PydanticSchema):
    """Lightweight driver record — used in the session overview list."""

    reg_number: str
    first_name: str
    last_name: str
    number: str
    race_class: str | None = None
    team: str | None = None
    chassis: str | None = None
    lap_count: int
    fastest_lap_time: float | None = None
    finish_position: int | None = None


class DriverDetail(PydanticSchema):
    """Full driver detail — used in the driver analysis view."""

    reg_number: str
    first_name: str
    last_name: str
    number: str
    race_class: str | None = None
    team: str | None = None
    chassis: str | None = None
    lap_count: int
    fastest_lap_time: float | None = None
    fastest_lap_number: int | None = None
    avg_lap_time: float | None = None
    # Official standings resolved from the $G/$H timing records.
    finish_position: int | None = None
    laps_completed: int | None = None
    total_time_seconds: float | None = None
    best_lap_position: int | None = None
    official_best_lap_number: int | None = None
    official_best_lap_time: float | None = None
    laps: list[LapSchema] = Field(default_factory=list)
