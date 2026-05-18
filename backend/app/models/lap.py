"""ORM model for a single timed lap."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base

if TYPE_CHECKING:
    from backend.app.models.driver import Driver


class Lap(Base):
    """One completed lap by a driver, sourced from an RMonitor `$J` record."""

    __tablename__ = "laps"
    __table_args__ = (UniqueConstraint("driver_id", "lap_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"),
        index=True,
    )
    lap_number: Mapped[int]
    lap_time_seconds: Mapped[float]
    total_time_seconds: Mapped[float]

    driver: Mapped[Driver] = relationship(back_populates="laps")
