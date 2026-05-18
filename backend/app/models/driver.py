"""ORM model for a competitor within a session."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base

if TYPE_CHECKING:
    from backend.app.models.lap import Lap
    from backend.app.models.session import Session


class Driver(Base):
    """A competitor and their identifying details for one session.

    The `chassis` and `team` fields come from RMonitor's "Nationality" and
    `$COMP` "Additional data" fields, which karting timing exports repurpose.
    """

    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        index=True,
    )
    reg_number: Mapped[str] = mapped_column(index=True)
    car_number: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    transponder: Mapped[str | None]
    chassis: Mapped[str | None]
    team: Mapped[str | None]
    race_class: Mapped[str | None]

    # Resolved from the final `$G` race-information record.
    finish_position: Mapped[int | None]
    laps_completed: Mapped[int | None]
    total_time_seconds: Mapped[float | None]
    # Resolved from the final `$H` practice/qualifying record.
    best_lap_position: Mapped[int | None]
    official_best_lap_number: Mapped[int | None]
    official_best_lap_time: Mapped[float | None]

    session: Mapped[Session] = relationship(back_populates="drivers")
    laps: Mapped[list[Lap]] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan",
        order_by="Lap.lap_number",
    )
