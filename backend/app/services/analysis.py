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
    LeaderboardEntry,
    ProgressionLap,
)

_TIME_PRECISION = 3
_MIN_LAPS_FOR_STDEV = 2
_MIN_LAPS_FOR_OUTLIERS = 3
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


def build_leaderboard(
    session: models.Session,
    race_class: str | None = None,
) -> list[LeaderboardEntry]:
    """Rank drivers by their fastest lap, with the gap to the session leader."""
    ranked: list[tuple[models.Driver, models.Lap]] = []
    for driver in _select_drivers(session, race_class=race_class):
        best = _best_lap(driver)
        if best is not None:
            ranked.append((driver, best))
    ranked.sort(key=lambda item: item[1].lap_time_seconds)
    leader_time = ranked[0][1].lap_time_seconds if ranked else 0.0
    return [
        LeaderboardEntry(
            position=position,
            reg_number=driver.reg_number,
            number=driver.car_number,
            driver_name=_driver_name(driver),
            race_class=driver.race_class,
            best_lap_time=_round(best.lap_time_seconds),
            best_lap_number=best.lap_number,
            lap_count=len(driver.laps),
            gap_to_leader=_round(best.lap_time_seconds - leader_time),
        )
        for position, (driver, best) in enumerate(ranked, start=1)
    ]


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
