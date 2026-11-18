"""Lap helpers shared by the analysis service and the API mappers."""

from backend.app import models

TIME_PRECISION = 3


def round_time(value: float) -> float:
    """Round a time to the protocol's millisecond precision."""
    return round(value, TIME_PRECISION)


def round_opt(value: float | None) -> float | None:
    """Round an optional time to millisecond precision, preserving ``None``."""
    return round_time(value) if value is not None else None


def fastest_lap(driver: models.Driver) -> models.Lap | None:
    """Return the driver's fastest stored lap, or ``None`` if they ran none."""
    return min(driver.laps, key=lambda lap: lap.lap_time_seconds, default=None)
