from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.dtos.delivery import DeliveryModeOut
from app.dtos.instructor import InstructorOut
from app.dtos.venue import VenueOut


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
