"""Base Pydantic schema classes for LapVisualizer."""

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PydanticSchema(BaseModel):
    """Base schema for all API response models.

    Enables ORM mode via `from_attributes=True` so SQLAlchemy model
    instances can be serialised directly.  All subclasses inherit
    enum-value serialisation, assignment validation, and ISO-8601
    timedelta formatting.

    Attributes:
        model_config: Pydantic configuration enabling ORM mode,
            enum-value serialisation, whitespace stripping, and
            ISO-8601 timedelta output.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        validate_default=True,
        from_attributes=True,
        str_strip_whitespace=True,
        ser_json_timedelta="iso8601",
        json_schema_serialization_defaults_required=True,
    )


class RequestSchema(PydanticSchema):
    """Base schema for all API request/input models.

    Extends `PydanticSchema` with stricter validation suitable for
    untrusted input: unknown fields are rejected (`extra='forbid'`),
    field names are accepted in camelCase via an alias generator, and
    string length is capped at 4 096 characters.

    Attributes:
        model_config: Pydantic configuration that forbids extra fields,
            generates camelCase aliases, and limits string length to
            4 096 characters.
    """

    model_config = ConfigDict(
        extra="forbid",
        alias_generator=AliasGenerator(to_camel),
        str_max_length=4096,
    )
