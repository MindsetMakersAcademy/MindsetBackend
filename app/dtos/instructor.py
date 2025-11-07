from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InstructorOut(BaseModel):
    """Output DTO for Instructor entity."""

    id: int
    full_name: str
    phone: str | None = None
    email: str | None = None
    bio: str | None = None
    model_config = ConfigDict(from_attributes=True)


class InstructorCreateDTO(BaseModel):
    """DTO for creating an instructor."""

    full_name: str = Field(..., min_length=1, max_length=120)
    email: str | None = Field(None, max_length=160)
    phone: str | None = Field(None, max_length=40)
    bio: str | None = None


class InstructorUpdateDTO(BaseModel):
    """DTO for updating an instructor."""

    full_name: str | None = Field(None, min_length=1, max_length=120)
    email: str | None = Field(None, max_length=160)
    phone: str | None = Field(None, max_length=40)
    bio: str | None = None


class InstructorReadDTO(BaseModel):
    """DTO for reading instructor data."""

    id: int
    full_name: str
    email: str | None = None
    phone: str | None = None
    bio: str | None = None
    model_config = ConfigDict(from_attributes=True)
