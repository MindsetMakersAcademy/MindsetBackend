from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaginationQueryDTO(BaseModel):
    """DTO for pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


class SortQueryDTO(BaseModel):
    """DTO for sorting query parameters."""
    sort: str = Field(default="id", description="Field to sort by")
    direction: Literal["asc", "desc"] = Field(default="asc", description="Sort direction")


class SearchQueryDTO(BaseModel):
    """DTO for search query parameters."""
    q: str | None = Field(default=None, min_length=1, max_length=100, description="Search query")
    
    @field_validator("q")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        """Strip whitespace from query string."""
        return v.strip() if v else None

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

class DeliveryModeOut(BaseModel):
    """Output DTO for DeliveryMode entity."""
    id: int
    label: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True) 


class VenueOut(BaseModel):
    """Output DTO for Venue entity."""
    id: int
    name: str
    address: str | None = None
    map_url: str | None = None
    room_capacity: int | None = None
    model_config = ConfigDict(from_attributes=True)


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

class CourseOut(BaseModel):
    """Output DTO for full Course details, including relationships."""

    id: int
    title: str
    description: str | None = None
    capacity: int | None = None
    session_counts: int | None = None
    session_duration_minutes: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    delivery_mode: DeliveryModeOut
    venue: VenueOut | None = None
    instructors: list[InstructorOut] = []
    model_config = ConfigDict(from_attributes=True)


class CourseListOut(BaseModel):
    """Output DTO for course list/search results (summary only)."""

    id: int
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    model_config = ConfigDict(from_attributes=True)


class CoursePastOut(BaseModel):
    """Output DTO for past courses, including relationships."""

    id: int
    title: str
    description: str | None = None
    capacity: int | None = None
    session_counts: int | None = None
    session_duration_minutes: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    delivery_mode: DeliveryModeOut
    venue: VenueOut | None = None
    instructors: list[InstructorOut] = []
    model_config = ConfigDict(from_attributes=True)


# TODO: Add validation logic in DTO layer for creation
class CourseCreateIn(BaseModel):
    """Input DTO for creating a course. Only fields accepted from client."""

    title: str
    description: str | None = None
    delivery_mode_id: int
    venue_id: int | None = None
    instructor_ids: list[int] = []
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None
    session_counts: int | None = None
    session_duration_minutes: int | None = None


class CourseUpdateIn(BaseModel):
    """Input DTO for updating a course. All fields optional."""

    title: str | None = None
    description: str | None = None
    delivery_mode_id: int | None = None
    venue_id: int | None = None
    instructor_ids: list[int] | None = None
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None
    session_counts: int | None = None
    session_duration_minutes: int | None = None

class DeliveryModeBaseDTO(BaseModel):
    label: str = Field(..., description="Delivery mode label")
    description: str | None = Field(None, description="Optional description")

class DeliveryModeCreateDTO(DeliveryModeBaseDTO):
    ...

class DeliveryModeUpdateDTO(BaseModel):
    label: str | None = Field(None)
    description: str | None = Field(None)

class DeliveryModeReadDTO(DeliveryModeBaseDTO):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EventTypeBaseDTO(BaseModel):
    label: str = Field(..., description="Event type label")
    description: str | None = Field(None, description="Optional description")

class EventTypeCreateDTO(EventTypeBaseDTO):
    ...

class EventTypeUpdateDTO(BaseModel):
    label: str | None = Field(None)
    description: str | None = Field(None)

class EventTypeReadDTO(EventTypeBaseDTO):
    id: int
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
