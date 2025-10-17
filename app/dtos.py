from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


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
    class Config:
        from_attributes = True 

class DeliveryModeOut(BaseModel):
    """Output DTO for DeliveryMode entity."""
    id: int
    label: str
    description: str | None = None
    model_config = {"from_attributes": True}


class VenueOut(BaseModel):
    """Output DTO for Venue entity."""
    id: int
    name: str
    address: str | None = None
    map_url: str | None = None
    room_capacity: int | None = None
    model_config = {"from_attributes": True}


class InstructorOut(BaseModel):
    """Output DTO for Instructor entity."""

    id: int
    full_name: str
    phone: str | None = None
    email: str | None = None
    bio: str | None = None
    model_config = {"from_attributes": True}


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
    model_config = {"from_attributes": True}


class CourseListOut(BaseModel):
    """Output DTO for course list/search results (summary only)."""

    id: int
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    model_config = {"from_attributes": True}


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
    model_config = {"from_attributes": True}


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
    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True
