from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Contract(BaseModel):
    """Base model that serializes to camelCase JSON to match the TS contracts."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )
