"""Pydantic schemas for the lap-analysis endpoints."""

import enum

from pydantic import Field

from backend.app.schemas.base import PydanticSchema


class SessionType(enum.StrEnum):
    """How a session's leaderboard is ranked.

    A race is ranked by finishing order (the timing system's ``$G``
    classification); a practice or qualifying session is ranked by best lap
    (the ``$H`` classification).
    """

    RACE = "race"
    PRACTICE = "practice"


class LeaderboardEntry(PydanticSchema):
    """One row of a session leaderboard.

    The leaderboard mirrors the timing system's own final classification —
    ``$G`` for a race, ``$H`` for a practice — so `position` is the official
    standing, not a ranking re-derived from the lap log. Fields that only one
    session type provides (e.g. `total_time_seconds`) are left unset otherwise.
    """

    position: int
    reg_number: str
    number: str
    driver_name: str
    race_class: str | None = None
    lap_count: int
    # Official best lap, from the $H classification record.
    best_lap_time: float | None = None
    best_lap_number: int | None = None
    # Race finish details, from the $G classification record.
    laps_completed: int | None = None
    total_time_seconds: float | None = None
    # Gap to the leader: a time in seconds, or — for a lapped car — `laps_down`.
    gap_to_leader: float | None = None
    laps_down: int | None = None


class Leaderboard(PydanticSchema):
    """A session's full classification, ordered best-placed first."""

    session_type: SessionType
    entries: list[LeaderboardEntry] = Field(default_factory=list)


class ProgressionLap(PydanticSchema):
    """A single lap within a driver's progression, with derived deltas."""

    lap_number: int
    lap_time_seconds: float
    total_time_seconds: float
    gap_to_personal_best: float
    is_personal_best: bool


class DriverProgression(PydanticSchema):
    """A driver's laps in order — the data behind a lap-time chart."""

    reg_number: str
    number: str
    driver_name: str
    race_class: str | None = None
    best_lap_time: float | None = None
    laps: list[ProgressionLap] = Field(default_factory=list)


class ComparisonDriver(PydanticSchema):
    """Identifying metadata for a driver included in a comparison."""

    reg_number: str
    number: str
    driver_name: str
    race_class: str | None = None
    best_lap_time: float | None = None


class ComparisonRow(PydanticSchema):
    """Lap times for every compared driver at a single lap number."""

    lap_number: int
    times: dict[str, float | None] = Field(default_factory=dict)


class ComparisonResult(PydanticSchema):
    """Side-by-side lap times for a set of selected drivers."""

    drivers: list[ComparisonDriver] = Field(default_factory=list)
    rows: list[ComparisonRow] = Field(default_factory=list)


class DriverStats(PydanticSchema):
    """Aggregate lap statistics for a single driver."""

    reg_number: str
    number: str
    driver_name: str
    race_class: str | None = None
    lap_count: int
    best_lap_time: float
    worst_lap_time: float
    mean_lap_time: float
    median_lap_time: float
    std_dev_seconds: float
    outlier_lap_numbers: list[int] = Field(default_factory=list)
