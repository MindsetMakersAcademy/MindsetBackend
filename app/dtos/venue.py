from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class VenueOut(BaseModel):
    """Output DTO for Venue entity."""

    id: int
    name: str
    address: str | None = None
    map_url: str | None = None
    room_capacity: int | None = None
    model_config = ConfigDict(from_attributes=True)


class VenueCreateDTO(BaseModel):
    name: str
    address: str | None = None
    map_url: str | None = None
    notes: str | None = None
    room_capacity: int | None = None


class VenueUpdateDTO(BaseModel):
    name: str | None = None
    address: str | None = None
    map_url: str | None = None
    notes: str | None = None
    room_capacity: int | None = None


class VenueReadDTO(BaseModel):
    id: int
    name: str
    address: str | None = None
    map_url: str | None = None
    notes: str | None = None
    room_capacity: int | None = None
    model_config = ConfigDict(from_attributes=True)

