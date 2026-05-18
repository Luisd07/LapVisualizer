"""Endpoints for inspecting the drivers within a session."""

from fastapi import APIRouter, HTTPException, status

from backend.app.api.deps import DbSession, get_session_or_404
from backend.app.api.mappers import to_driver_detail, to_driver_summary
from backend.app.schemas.driver import DriverDetail, DriverSummary

router = APIRouter(prefix="/sessions", tags=["drivers"])


@router.get("/{session_id}/drivers", response_model=list[DriverSummary])
def list_drivers(session_id: str, db: DbSession) -> list[DriverSummary]:
    """List every driver entered in a session."""
    session = get_session_or_404(db, session_id)
    return [to_driver_summary(driver) for driver in session.drivers]


@router.get("/{session_id}/drivers/{reg_number}", response_model=DriverDetail)
def get_driver(session_id: str, reg_number: str, db: DbSession) -> DriverDetail:
    """Return one driver with their full lap list and summary metrics."""
    session = get_session_or_404(db, session_id)
    driver = next(
        (d for d in session.drivers if d.reg_number == reg_number),
        None,
    )
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found in this session",
        )
    return to_driver_detail(driver)
