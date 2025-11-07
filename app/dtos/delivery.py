from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DeliveryModeOut(BaseModel):
    """Output DTO for DeliveryMode entity."""

    id: int
    label: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)


class DeliveryModeBaseDTO(BaseModel):
    label: str = Field(..., description="Delivery mode label")
    description: str | None = Field(None, description="Optional description")


class DeliveryModeCreateDTO(DeliveryModeBaseDTO): ...


class DeliveryModeUpdateDTO(BaseModel):
    label: str | None = Field(None)
    description: str | None = Field(None)


class DeliveryModeReadDTO(DeliveryModeBaseDTO):
    id: int
    model_config = ConfigDict(from_attributes=True)
