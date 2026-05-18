"""Pydantic schemas describing race-car drivers."""

from pydantic import Field

from backend.app.schemas.base import PydanticSchema
from backend.app.schemas.laps import LapSchema


class DriverSummary(PydanticSchema):
    """Lightweight driver — used in session overview list."""

    first_name: str
    last_name: str
    number: int
    race_class: str
    team: str
    chassis: str
    lap_count: int
    best_lap_time: float


class DriverDetail(PydanticSchema):
    """Full driver detail — used in driver analysis view."""

    first_name: str
    last_name: str
    number: int
    race_class: str
    team: str
    chassis: str
    lap_count: int
    best_lap_time: float | None = None
    best_lap_number: int | None = None
    avg_lap_time: float | None = None
    laps: list[LapSchema] = Field(default_factory=list)
