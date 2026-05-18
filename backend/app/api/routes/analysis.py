"""Endpoints powering the lap-analysis dashboards."""

from fastapi import APIRouter, HTTPException, status

from backend.app.api.deps import DbSession, get_session_or_404
from backend.app.schemas.analysis import (
    ComparisonResult,
    DriverProgression,
    DriverStats,
    LeaderboardEntry,
)
from backend.app.services import analysis

router = APIRouter(prefix="/sessions", tags=["analysis"])

_MIN_COMPARISON_DRIVERS = 2


def _split_regs(value: str | None) -> list[str] | None:
    """Split a comma-separated `drivers` query value into reg numbers."""
    if value is None:
        return None
    regs = [item.strip() for item in value.split(",") if item.strip()]
    return regs or None


@router.get("/{session_id}/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(
    session_id: str,
    db: DbSession,
    race_class: str | None = None,
) -> list[LeaderboardEntry]:
    """Rank drivers by their fastest lap, optionally filtered to one class."""
    session = get_session_or_404(db, session_id)
    return analysis.build_leaderboard(session, race_class=race_class)


@router.get("/{session_id}/progression", response_model=list[DriverProgression])
def progression(
    session_id: str,
    db: DbSession,
    drivers: str | None = None,
    race_class: str | None = None,
) -> list[DriverProgression]:
    """Return lap-by-lap progressions for the selected drivers."""
    session = get_session_or_404(db, session_id)
    return analysis.build_progression(session, _split_regs(drivers), race_class)


@router.get("/{session_id}/comparison", response_model=ComparisonResult)
def comparison(
    session_id: str,
    db: DbSession,
    drivers: str,
) -> ComparisonResult:
    """Align the lap times of two or more drivers for head-to-head charts."""
    regs = _split_regs(drivers) or []
    if len(regs) < _MIN_COMPARISON_DRIVERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least two comma-separated driver reg numbers.",
        )
    session = get_session_or_404(db, session_id)
    return analysis.build_comparison(session, regs)


@router.get("/{session_id}/stats", response_model=list[DriverStats])
def stats(
    session_id: str,
    db: DbSession,
    drivers: str | None = None,
    race_class: str | None = None,
) -> list[DriverStats]:
    """Return per-driver lap statistics, including likely-traffic outliers."""
    session = get_session_or_404(db, session_id)
    return analysis.build_stats(session, _split_regs(drivers), race_class)
