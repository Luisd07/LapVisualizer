"""Helpers that convert ORM models into API response schemas."""

from backend.app import models
from backend.app.schemas.driver import DriverDetail, DriverSummary
from backend.app.schemas.laps import LapSchema
from backend.app.schemas.session import (
    SessionDetail,
    SessionSummary,
    SessionUploadResponse,
)

_TIME_PRECISION = 3


def _best_lap(driver: models.Driver) -> models.Lap | None:
    """Return the driver's fastest lap, or ``None`` if they ran none."""
    return min(driver.laps, key=lambda lap: lap.lap_time_seconds, default=None)


def _total_laps(session: models.Session) -> int:
    """Return the total number of laps across every driver in the session."""
    return sum(len(driver.laps) for driver in session.drivers)


def _round_opt(value: float | None) -> float | None:
    """Round an optional time to millisecond precision, preserving ``None``."""
    return round(value, _TIME_PRECISION) if value is not None else None


def to_driver_summary(driver: models.Driver) -> DriverSummary:
    """Build a lightweight driver summary, including the driver's best lap."""
    best = _best_lap(driver)
    return DriverSummary(
        reg_number=driver.reg_number,
        first_name=driver.first_name,
        last_name=driver.last_name,
        number=driver.car_number,
        race_class=driver.race_class,
        team=driver.team,
        chassis=driver.chassis,
        lap_count=len(driver.laps),
        best_lap_time=_round_opt(best.lap_time_seconds) if best is not None else None,
        finish_position=driver.finish_position,
    )


def to_driver_detail(driver: models.Driver) -> DriverDetail:
    """Build a full driver detail record, including every lap and standings."""
    laps = sorted(driver.laps, key=lambda lap: lap.lap_number)
    times = [lap.lap_time_seconds for lap in laps]
    best = _best_lap(driver)
    return DriverDetail(
        reg_number=driver.reg_number,
        first_name=driver.first_name,
        last_name=driver.last_name,
        number=driver.car_number,
        race_class=driver.race_class,
        team=driver.team,
        chassis=driver.chassis,
        lap_count=len(laps),
        best_lap_time=_round_opt(best.lap_time_seconds) if best is not None else None,
        best_lap_number=best.lap_number if best is not None else None,
        avg_lap_time=(round(sum(times) / len(times), _TIME_PRECISION) if times else None),
        finish_position=driver.finish_position,
        laps_completed=driver.laps_completed,
        total_time_seconds=_round_opt(driver.total_time_seconds),
        best_lap_position=driver.best_lap_position,
        official_best_lap_number=driver.official_best_lap_number,
        official_best_lap_time=_round_opt(driver.official_best_lap_time),
        laps=[
            LapSchema(
                lap_number=lap.lap_number,
                lap_time_seconds=lap.lap_time_seconds,
                total_time_seconds=lap.total_time_seconds,
            )
            for lap in laps
        ],
    )


def to_session_summary(session: models.Session) -> SessionSummary:
    """Build a lightweight session summary for list views."""
    return SessionSummary(
        session_id=session.id,
        session_name=session.name,
        run_number=session.run_number,
        track_name=session.track_name,
        total_laps=_total_laps(session),
        driver_count=len(session.drivers),
        uploaded_at=session.uploaded_at,
    )


def to_session_detail(session: models.Session) -> SessionDetail:
    """Build a full session detail record, including driver summaries."""
    return SessionDetail(
        session_id=session.id,
        session_name=session.name,
        run_number=session.run_number,
        track_name=session.track_name,
        track_length=session.track_length,
        flag_status=session.flag_status,
        race_time_seconds=_round_opt(session.race_time_seconds),
        time_of_day=session.time_of_day,
        session_date=session.session_date,
        total_laps=_total_laps(session),
        driver_count=len(session.drivers),
        uploaded_at=session.uploaded_at,
        drivers=[to_driver_summary(driver) for driver in session.drivers],
        warnings=session.warnings,
    )


def to_upload_response(
    session: models.Session,
    *,
    duplicate: bool,
) -> SessionUploadResponse:
    """Build the response returned after an upload completes."""
    return SessionUploadResponse(
        session_id=session.id,
        session_name=session.name,
        run_number=session.run_number,
        track_name=session.track_name,
        total_laps=_total_laps(session),
        driver_count=len(session.drivers),
        uploaded_at=session.uploaded_at,
        duplicate=duplicate,
        warnings=session.warnings,
    )
