from __future__ import annotations

from datetime import date

import pytest

from app.dtos import CourseCreateIn
from app.exceptions import NotFoundError
from app.services.course import CourseService
from tests.conftest import FakeCourseRepository


def test_list_courses_returned_as_dtos_and_ordering(
    seed_two_courses: tuple[int, int], fake_courses: FakeCourseRepository
):
    """Return DTO-like objects ordered by end_date desc then id desc."""
    svc = CourseService(session=None, repo=fake_courses)

    items = svc.list_courses()

    assert isinstance(items, list)
    assert len(items) == 2

    expected_keys = ("id", "title", "start_date", "end_date")
    for it in items:
        for k in expected_keys:
            assert hasattr(it, k), f"Missing key {k} on item {it!r}"

    ordering = [(it.end_date, it.id) for it in items]
    expected = sorted(ordering, key=lambda t: (t[0], t[1]), reverse=True)
    assert ordering == expected


def test_get_course_by_id_returns_dto(seeded_course_id: int, fake_courses: FakeCourseRepository):
    """Get by id returns a DTO with expected fields and types."""
    svc = CourseService(session=None, repo=fake_courses)

    dto = svc.get_course_by_id(seeded_course_id)

    assert dto.id == seeded_course_id
    assert dto.title == "X"
    for k in ("start_date", "end_date"):
        val = getattr(dto, k)
        assert isinstance(val, date) or val is None


def test_get_course_by_id_raises_not_found_when_missing(fake_courses: FakeCourseRepository):
    """Service raises NotFoundError for missing course id."""
    svc = CourseService(session=None, repo=fake_courses)

    with pytest.raises(NotFoundError):
        svc.get_course_by_id(999999)


def test_create_course_success_and_validation(fake_courses: FakeCourseRepository):
    """Creating a valid course succeeds; invalid date-range fails."""
    svc = CourseService(session=None, repo=fake_courses)

    valid = CourseCreateIn.model_validate({
        "title": "New Course",
        "description": "desc",
        "delivery_mode_id": 1,
        "venue_id": None,
        "instructor_ids": [],
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 2),
    })

    out = svc.create_course(valid)

    assert out.title == "New Course"
    assert hasattr(out, "id") and isinstance(out.id, int)
    assert any(c.title == "New Course" for c in fake_courses.list_all())

    bad = CourseCreateIn.model_validate({
        "title": "Bad Date",
        "description": None,
        "delivery_mode_id": 1,
        "venue_id": None,
        "instructor_ids": [],
        "start_date": date(2024, 2, 2),
        "end_date": date(2024, 1, 1),
    })

    with pytest.raises(ValueError):
        svc.create_course(bad)
