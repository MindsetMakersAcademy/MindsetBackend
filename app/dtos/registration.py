from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RegistrationStatusBaseDTO(BaseModel):
    """Shared fields for RegistrationStatus."""

    label: str = Field(..., description="Registration status label")
    description: str | None = Field(None, description="Optional description")


class RegistrationStatusCreateDTO(RegistrationStatusBaseDTO):
    """Used for creating a new RegistrationStatus entry."""


class RegistrationStatusUpdateDTO(BaseModel):
    """Used for updating a RegistrationStatus entry."""

    label: str | None = Field(None, description="New label")
    description: str | None = Field(None, description="New description")


class RegistrationStatusReadDTO(RegistrationStatusBaseDTO):
    """Returned when fetching RegistrationStatus entries."""

    id: int
    model_config = ConfigDict(from_attributes=True)
