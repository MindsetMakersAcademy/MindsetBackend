from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.dtos import CourseCreateIn, CourseUpdateIn
from app.exceptions import NotFoundError
from app.models import Instructor
from app.services.course import CourseService


def test_list_courses_returned_as_dtos_and_ordering(
    seed_two_courses: tuple[int, int],
    course_svc: CourseService,
):
    """
    Returns DTO-like objects ordered by end_date desc then id desc.
    Uses real repository + SQLite, seeded via seed_two_courses fixture.
    """
    # Act
    items = course_svc.list_courses()

    # Assert (shape)
    assert isinstance(items, list)
    assert len(items) == 2
    expected_keys = ("id", "title", "start_date", "end_date")
    for it in items:
        for k in expected_keys:
            assert hasattr(it, k), f"Missing key {k} on item {it!r}"

    # Assert (ordering) — end_date desc then id desc
    ordering = [(it.end_date, it.id) for it in items]
    expected = sorted(ordering, key=lambda t: (t[0], t[1]), reverse=True)
    assert ordering == expected


@pytest.mark.parametrize(
    "index,expected_title,expected_start,expected_end",
    [
        (
            0,
            "A",
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
        ),
        (
            1,
            "B",
            datetime(2024, 1, 3),
            datetime(2024, 1, 4),
        ),
    ],
)
def test_get_course_by_id_returns_dto(
    course_svc: CourseService,
    seed_two_courses: tuple[int, int],
    index: int,
    expected_title: str,
    expected_start: datetime,
    expected_end: datetime,
) -> None:
    """
    Uses only seeds; no assumptions about auto IDs or list ordering.
    """
    # Arrange
    course_id = seed_two_courses[index]

    # Act
    dto = course_svc.get_course_by_id(course_id)

    # Assert
    assert dto.id == course_id
    assert dto.title == expected_title

    # start_date / end_date should be dates (repo normalizes)
    assert dto.start_date == expected_start
    assert dto.end_date == expected_end
    assert isinstance(dto.start_date, datetime) or dto.start_date is None
    assert isinstance(dto.end_date, datetime) or dto.end_date is None


def test_get_course_by_id_raises_not_found_when_missing(course_svc: CourseService):
    """
    Service raises NotFoundError for missing course id (matches service contract).
    """
    with pytest.raises(NotFoundError):
        course_svc.get_course_by_id(999_999)


def test_create_course_success(
    course_svc: CourseService,
    seed_delivery_modes,
):
    """
    Creating a valid course succeeds.
    """
    # arrange
    valid = CourseCreateIn(
        title="New Course",
        description="desc",
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
    )

    # act
    out = course_svc.create_course(valid)

    # assert
    assert out.title == "New Course"
    assert hasattr(out, "id") and isinstance(out.id, int)


def test_create_course_validation(
    course_svc: CourseService,
    seed_delivery_modes,
):
    """
    Creating an invalid date-range fails (if service validates).
    """
    bad = CourseCreateIn(
        title="Bad Date",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 2, 2),
        end_date=datetime(2024, 1, 1),
    )
    with pytest.raises(ValueError):
        course_svc.create_course(bad)


# ---------- Additional high-value unit tests ----------


@pytest.mark.parametrize(
    "q,expected_titles",
    [
        ("A", ["A"]),
        ("b", ["B"]),  # case-insensitive
        ("Z", []),
    ],
)
def test_search_courses(
    q: str,
    expected_titles: list[str],
    course_repo,
    scoped_test_session,
    seed_delivery_modes,
    course_svc: CourseService,
):
    # Arrange
    course_repo.create_course(
        title="A",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
    )
    course_repo.create_course(
        title="B",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 3),
        end_date=datetime(2024, 1, 4),
    )
    scoped_test_session.flush()

    # Act
    items = course_svc.search_courses(q)

    # Assert
    titles = [it.title for it in items]
    assert titles == expected_titles


def test_update_course_success(
    course_repo,
    scoped_test_session,
    seed_delivery_modes,
    course_svc: CourseService,
):
    # Arrange: create a course to update
    created = course_repo.create_course(
        title="Old",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
    )
    scoped_test_session.flush()

    # Act
    updated = course_svc.update_course(
        created.id,
        {"title": "New", "description": "updated", "end_date": datetime(2024, 1, 3)},
    )

    # Assert
    assert updated.id == created.id
    assert updated.title == "New"
    assert updated.description == "updated"
    assert updated.end_date == datetime(2024, 1, 3)


def test_update_course_not_found_raises(course_svc: CourseService):
    course_id = 999_999
    data = CourseUpdateIn(title="Nothing")
    with pytest.raises(NotFoundError):
        course_svc.update_course(
            course_id=course_id,
            data=data,
        )


def test_create_course_with_unknown_instructor_ids_raises(
    course_svc: CourseService,
    seed_delivery_modes,
):
    """
    The repository checks that all instructor_ids exist; the service should bubble an error.
    """
    dto = CourseCreateIn.model_validate(
        {
            "title": "With Instructor",
            "description": None,
            "delivery_mode_id": seed_delivery_modes["online"].id,
            "venue_id": None,
            "instructor_ids": [999],  # does not exist
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 1, 2),
        }
    )
    with pytest.raises(ValueError):
        course_svc.create_course(dto)


def test_create_course_with_existing_instructor_succeeds(
    course_svc: CourseService,
    seed_delivery_modes,
    scoped_test_session,
):
    """
    Positive control: if we insert an Instructor row first, creation should succeed.
    """
    # Arrange: create an instructor row directly
    inst = Instructor(full_name="Ada Lovelace", email="ada@example.com")
    scoped_test_session.add(inst)
    scoped_test_session.flush()

    dto = CourseCreateIn.model_validate(
        {
            "title": "With Real Instructor",
            "description": None,
            "delivery_mode_id": seed_delivery_modes["online"].id,
            "venue_id": None,
            "instructor_ids": [inst.id],
            "start_date": datetime(2024, 1, 1),
            "end_date": datetime(2024, 1, 2),
        }
    )

    # Act
    out = course_svc.create_course(dto)

    # Assert
    assert out.title == "With Real Instructor"
    # If your DTO exposes instructors, you could assert len(out.instructors) == 1 here.


def test_list_past_courses_uses_current_date_boundary(
    course_repo,
    course_svc: CourseService,
    scoped_test_session,
    seed_delivery_modes,
    monkeypatch,
):
    """
    Freeze 'today' to make past-course boundary deterministic.
    """
    # Freeze now() used in repository (patch at lookup site)
    import app.repositories.course as course_repo_module

    fixed_now = datetime(2024, 3, 10, tzinfo=UTC)
    monkeypatch.setattr(
        course_repo_module,
        "datetime",
        type("D", (), {"now": staticmethod(lambda tz=None: fixed_now)}),
    )

    # A is past, B is ongoing/future relative to fixed_now.date()
    course_repo.create_course(
        title="Past",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 3, 1),
    )
    course_repo.create_course(
        title="Future",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 3, 10),
        end_date=datetime(2024, 3, 11),
    )
    scoped_test_session.flush()

    items = course_svc.list_past_courses()
    titles = [it.title for it in items]
    assert titles == ["Past"]
