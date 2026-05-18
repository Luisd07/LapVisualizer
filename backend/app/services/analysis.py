"""Lap-analysis service: leaderboards, progressions, comparisons, and stats."""

import statistics
from collections.abc import Iterable

from backend.app import models
from backend.app.schemas.analysis import (
    ComparisonDriver,
    ComparisonResult,
    ComparisonRow,
    DriverProgression,
    DriverStats,
    Leaderboard,
    LeaderboardEntry,
    ProgressionLap,
    SessionType,
)

_TIME_PRECISION = 3
_MIN_LAPS_FOR_STDEV = 2
_MIN_LAPS_FOR_OUTLIERS = 3
# Sentinel sort key for drivers the timing system left unclassified — it keeps
# them after every ranked competitor instead of ahead of position 1.
_UNRANKED = 10**6

# Run-name keywords that tell a race from a practice/qualifying session. Orbits
# broadcasts both the $G and $H classification records regardless of session
# type, so the $B run name is the only signal for which one is the official
# result. Practice words win: "Final Practice" is a practice, not a race.
_PRACTICE_KEYWORDS = ("practice", "qualif", "warm", "test")
_RACE_KEYWORDS = ("race", "final", "heat", "main", "feature")
# A lap more than 7% slower than the driver's median lap is treated as an
# outlier (traffic, an off, or a cool-down lap). The median is itself robust
# to such laps, so an extreme lap cannot mask its own detection.
_OUTLIER_MEDIAN_MULTIPLIER = 1.07


def _driver_name(driver: models.Driver) -> str:
    """Return the driver's full name."""
    return f"{driver.first_name} {driver.last_name}".strip()


def _round(value: float) -> float:
    """Round a time to the protocol's millisecond precision."""
    return round(value, _TIME_PRECISION)


def _round_opt(value: float | None) -> float | None:
    """Round an optional time to millisecond precision, preserving ``None``."""
    return _round(value) if value is not None else None


def _best_lap(driver: models.Driver) -> models.Lap | None:
    """Return the driver's fastest lap, or ``None`` if they ran none."""
    return min(driver.laps, key=lambda lap: lap.lap_time_seconds, default=None)


def _best_time(driver: models.Driver) -> float | None:
    """Return the driver's fastest lap time in seconds, or ``None``."""
    best = _best_lap(driver)
    return _round(best.lap_time_seconds) if best is not None else None


def _select_drivers(
    session: models.Session,
    reg_numbers: Iterable[str] | None = None,
    race_class: str | None = None,
) -> list[models.Driver]:
    """Filter a session's drivers by registration number and/or class."""
    drivers = list(session.drivers)
    if reg_numbers is not None:
        wanted = set(reg_numbers)
        drivers = [driver for driver in drivers if driver.reg_number in wanted]
    if race_class is not None:
        target = race_class.casefold()
        drivers = [driver for driver in drivers if (driver.race_class or "").casefold() == target]
    return drivers


def classify_session_type(run_name: str) -> SessionType:
    """Classify a session as a race or a practice from its `$B` run name.

    Args:
        run_name: The session's run description (e.g. "Final Practice - Q1").

    Returns:
        `SessionType.RACE` for race-type runs (race, heat, final, …), or
        `SessionType.PRACTICE` for practice/qualifying runs. Practice keywords
        are matched first, and an unrecognised name falls back to `PRACTICE`.
    """
    name = run_name.casefold()
    if any(keyword in name for keyword in _PRACTICE_KEYWORDS):
        return SessionType.PRACTICE
    if any(keyword in name for keyword in _RACE_KEYWORDS):
        return SessionType.RACE
    return SessionType.PRACTICE


def build_leaderboard(
    session: models.Session,
    race_class: str | None = None,
) -> Leaderboard:
    """Return the session's official classification, best-placed first.

    A race is ordered by finishing position (the `$G` record); a practice or
    qualifying session by best-lap position (the `$H` record). The order and
    positions come straight from the timing system — they are never re-derived
    from the lap log.
    """
    session_type = classify_session_type(session.name)
    drivers = _select_drivers(session, race_class=race_class)
    if session_type is SessionType.RACE:
        entries = _race_entries(drivers)
    else:
        entries = _practice_entries(drivers)
    return Leaderboard(session_type=session_type, entries=entries)


def _race_gap(
    driver: models.Driver,
    leader_laps: int | None,
    leader_time: float | None,
) -> tuple[float | None, int | None]:
    """Return ``(gap_seconds, laps_down)`` for a driver relative to the winner.

    A car on the lead lap gets a time gap; a lapped car gets a lap count and no
    time gap. Both are ``None`` when the classification lacks the data.
    """
    if driver.laps_completed is None or leader_laps is None:
        return None, None
    laps_down = leader_laps - driver.laps_completed
    if laps_down > 0:
        return None, laps_down
    if driver.total_time_seconds is None or leader_time is None:
        return 0.0, 0
    return _round(driver.total_time_seconds - leader_time), 0


def _race_entries(drivers: list[models.Driver]) -> list[LeaderboardEntry]:
    """Build race rows ordered by finishing position, with gaps to the winner."""
    ordered = sorted(drivers, key=lambda driver: driver.finish_position or _UNRANKED)
    leader = ordered[0] if ordered else None
    leader_laps = leader.laps_completed if leader is not None else None
    leader_time = leader.total_time_seconds if leader is not None else None
    entries: list[LeaderboardEntry] = []
    for fallback_position, driver in enumerate(ordered, start=1):
        gap, laps_down = _race_gap(driver, leader_laps, leader_time)
        entries.append(
            LeaderboardEntry(
                position=driver.finish_position or fallback_position,
                reg_number=driver.reg_number,
                number=driver.car_number,
                driver_name=_driver_name(driver),
                race_class=driver.race_class,
                lap_count=len(driver.laps),
                best_lap_time=_round_opt(driver.official_best_lap_time),
                best_lap_number=driver.official_best_lap_number,
                laps_completed=driver.laps_completed,
                total_time_seconds=_round_opt(driver.total_time_seconds),
                gap_to_leader=gap,
                laps_down=laps_down,
            ),
        )
    return entries


def _practice_entries(drivers: list[models.Driver]) -> list[LeaderboardEntry]:
    """Build practice/qualifying rows ordered by best-lap position."""
    ordered = sorted(drivers, key=lambda driver: driver.best_lap_position or _UNRANKED)
    leader_time = next(
        (driver.official_best_lap_time for driver in ordered if driver.official_best_lap_time),
        None,
    )
    entries: list[LeaderboardEntry] = []
    for fallback_position, driver in enumerate(ordered, start=1):
        best = driver.official_best_lap_time
        gap = _round(best - leader_time) if best and leader_time else None
        entries.append(
            LeaderboardEntry(
                position=driver.best_lap_position or fallback_position,
                reg_number=driver.reg_number,
                number=driver.car_number,
                driver_name=_driver_name(driver),
                race_class=driver.race_class,
                lap_count=len(driver.laps),
                best_lap_time=_round_opt(best),
                best_lap_number=driver.official_best_lap_number,
                gap_to_leader=gap,
            ),
        )
    return entries


def build_progression(
    session: models.Session,
    reg_numbers: Iterable[str] | None = None,
    race_class: str | None = None,
) -> list[DriverProgression]:
    """Return each selected driver's laps in order, with deltas to their best."""
    progressions: list[DriverProgression] = []
    for driver in _select_drivers(session, reg_numbers, race_class):
        laps = sorted(driver.laps, key=lambda lap: lap.lap_number)
        best_time = min((lap.lap_time_seconds for lap in laps), default=None)
        progressions.append(
            DriverProgression(
                reg_number=driver.reg_number,
                number=driver.car_number,
                driver_name=_driver_name(driver),
                race_class=driver.race_class,
                best_lap_time=_round(best_time) if best_time is not None else None,
                laps=[
                    ProgressionLap(
                        lap_number=lap.lap_number,
                        lap_time_seconds=_round(lap.lap_time_seconds),
                        total_time_seconds=_round(lap.total_time_seconds),
                        gap_to_personal_best=(
                            _round(lap.lap_time_seconds - best_time)
                            if best_time is not None
                            else 0.0
                        ),
                        is_personal_best=(
                            best_time is not None and lap.lap_time_seconds == best_time
                        ),
                    )
                    for lap in laps
                ],
            ),
        )
    return progressions


def build_comparison(
    session: models.Session,
    reg_numbers: list[str],
) -> ComparisonResult:
    """Align the lap times of the requested drivers by lap number."""
    by_reg = {driver.reg_number: driver for driver in _select_drivers(session, reg_numbers)}
    ordered = [by_reg[reg] for reg in dict.fromkeys(reg_numbers) if reg in by_reg]
    drivers = [
        ComparisonDriver(
            reg_number=driver.reg_number,
            number=driver.car_number,
            driver_name=_driver_name(driver),
            race_class=driver.race_class,
            best_lap_time=_best_time(driver),
        )
        for driver in ordered
    ]
    lap_index = {
        driver.reg_number: {lap.lap_number: _round(lap.lap_time_seconds) for lap in driver.laps}
        for driver in ordered
    }
    max_laps = max((len(driver.laps) for driver in ordered), default=0)
    rows = [
        ComparisonRow(
            lap_number=lap_number,
            times={
                driver.reg_number: lap_index[driver.reg_number].get(lap_number)
                for driver in ordered
            },
        )
        for lap_number in range(1, max_laps + 1)
    ]
    return ComparisonResult(drivers=drivers, rows=rows)


def _outlier_lap_numbers(laps: list[models.Lap], times: list[float]) -> list[int]:
    """Return lap numbers far slower than the driver's median lap."""
    if len(times) < _MIN_LAPS_FOR_OUTLIERS:
        return []
    threshold = statistics.median(times) * _OUTLIER_MEDIAN_MULTIPLIER
    return [lap.lap_number for lap in laps if lap.lap_time_seconds > threshold]


def build_stats(
    session: models.Session,
    reg_numbers: Iterable[str] | None = None,
    race_class: str | None = None,
) -> list[DriverStats]:
    """Compute aggregate lap statistics for each selected driver with laps."""
    stats: list[DriverStats] = []
    for driver in _select_drivers(session, reg_numbers, race_class):
        laps = list(driver.laps)
        if not laps:
            continue
        times = [lap.lap_time_seconds for lap in laps]
        std_dev = statistics.stdev(times) if len(times) >= _MIN_LAPS_FOR_STDEV else 0.0
        stats.append(
            DriverStats(
                reg_number=driver.reg_number,
                number=driver.car_number,
                driver_name=_driver_name(driver),
                race_class=driver.race_class,
                lap_count=len(laps),
                best_lap_time=_round(min(times)),
                worst_lap_time=_round(max(times)),
                mean_lap_time=_round(statistics.fmean(times)),
                median_lap_time=_round(statistics.median(times)),
                std_dev_seconds=_round(std_dev),
                outlier_lap_numbers=_outlier_lap_numbers(laps, times),
            ),
        )
    return stats
