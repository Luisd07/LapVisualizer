from backend.app.schemas.base import PydanticSchema


class LapSchema(PydanticSchema):
    """Schema for creating a new lap (lap-level fields only)."""

    lap_number: int
    lap_time_seconds: float
    total_time: float
