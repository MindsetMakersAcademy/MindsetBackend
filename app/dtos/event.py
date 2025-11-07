from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EventTypeBaseDTO(BaseModel):
    label: str = Field(..., description="Event type label")
    description: str | None = Field(None, description="Optional description")


class EventTypeCreateDTO(EventTypeBaseDTO): ...


class EventTypeUpdateDTO(BaseModel):
    label: str | None = Field(None)
    description: str | None = Field(None)


class EventTypeReadDTO(EventTypeBaseDTO):
    id: int
    model_config = ConfigDict(from_attributes=True)
