from __future__ import annotations

from collections.abc import Generator, Sequence
from datetime import date
from typing import Any, Generic, Literal, Protocol, Self, TypeVar

import pytest
from flask.testing import FlaskClient

from app import create_app
from app.api.v1 import course as course_api_module
from app.models import Course, DeliveryMode, EventType, RegistrationStatus, Venue
from app.repositories import (
    ICourseRepository,
    IDeliveryModeRepository,
    IEventTypeRepository,
    IRegistrationStatusRepository,
)
from app.services.course import CourseService

ModelT = TypeVar("ModelT", bound=Course | DeliveryMode | EventType | RegistrationStatus | Venue)

class DictFakeRepo(Generic[ModelT]):
    def __init__(self) -> None:
        self._store: dict[int, ModelT] = {}
        self._next_id: int = 1

    def _ensure_id(self, obj: Any) -> int:
        cur = getattr(obj, "id", None)
        if not isinstance(cur, int) or cur <= 0:
            obj.id = self._next_id
            cur = self._next_id
            self._next_id += 1
        return cur

    def get(self, id_: int) -> ModelT | None:
        return self._store.get(id_)

    def add(self, entity: ModelT) -> ModelT:
        eid = self._ensure_id(entity)
        self._store[eid] = entity
        return entity

    def delete(self, entity: ModelT) -> None:
        eid = getattr(entity, "id", None)
        if isinstance(eid, int):
            self._store.pop(eid, None)

    def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        rows = list(self._store.values())
        return rows[offset : offset + limit]

    def seed(self, *entities: ModelT) -> None:
        for e in entities:
            self.add(e)

    def clear(self) -> None:
        self._store.clear()
        self._next_id = 1


class FakeDeliveryModeRepository(DictFakeRepo[DeliveryMode], IDeliveryModeRepository):
    def get_by_id(self, id_: int) -> DeliveryMode | None:
        return self.get(id_)

    def get_by_label(self, label: str) -> DeliveryMode | None:
        lab = label.casefold()
        return next((dm for dm in self._store.values() if dm.label.casefold() == lab), None)

    def _sort_key(self, key: str):
        return (lambda e: e.id) if key == "id" else (lambda e: e.label)

    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "label",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[DeliveryMode]:
        items = list(self._store.values())
        if q:
            qcf = q.casefold()
            items = [e for e in items if qcf in e.label.casefold()]
        items.sort(key=self._sort_key(sort), reverse=(direction == "desc"))
        return items

    def create(self, *, label: str, description: str | None = None) -> DeliveryMode:
        dm = DeliveryMode(label=label, description=description)
        return self.add(dm)

    def update(
        self, entity: DeliveryMode, *, label: str | None = None, description: str | None = None
    ) -> DeliveryMode:
        if label is not None:
            entity.label = label
        if description is not None:
            entity.description = description
        return self.add(entity)


class FakeEventTypeRepository(DictFakeRepo[EventType], IEventTypeRepository):
    def get_by_id(self, id_: int) -> EventType | None:
        return self.get(id_)

    def get_by_label(self, label: str) -> EventType | None:
        lab = label.casefold()
        return next((et for et in self._store.values() if et.label.casefold() == lab), None)

    def _sort_key(self, key: str):
        return (lambda e: e.id) if key == "id" else (lambda e: e.label)

    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "label",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[EventType]:
        items = list(self._store.values())
        if q:
            qcf = q.casefold()
            items = [e for e in items if qcf in e.label.casefold()]
        items.sort(key=self._sort_key(sort), reverse=(direction == "desc"))
        return items

    def create(self, *, label: str, description: str | None = None) -> EventType:
        et = EventType(label=label, description=description)
        return self.add(et)

    def update(
        self, entity: EventType, *, label: str | None = None, description: str | None = None
    ) -> EventType:
        if label is not None:
            entity.label = label
        if description is not None:
            entity.description = description
        return self.add(entity)


class FakeRegistrationStatusRepository(
    DictFakeRepo[RegistrationStatus], IRegistrationStatusRepository
):
    def get_by_id(self, id_: int) -> RegistrationStatus | None:
        return self.get(id_)

    def get_by_label(self, label: str) -> RegistrationStatus | None:
        lab = label.casefold()
        return next((rs for rs in self._store.values() if rs.label.casefold() == lab), None)

    def _sort_key(self, key: str):
        return (lambda e: e.id) if key == "id" else (lambda e: e.label)

    def _sort_column(self, key: str):
        return (lambda e: e.id) if key == "id" else (lambda e: e.label)

    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "label",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[RegistrationStatus]:
        items = list(self._store.values())
        if q:
            qcf = q.casefold()
            items = [e for e in items if qcf in e.label.casefold()]
        items.sort(key=self._sort_key(sort), reverse=(direction == "desc"))
        return items

    def create(self, *, label: str, description: str | None = None) -> RegistrationStatus:
        rs = RegistrationStatus(label=label, description=description)
        return self.add(rs)

    def update(
        self,
        entity: RegistrationStatus,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> RegistrationStatus:
        if label is not None:
            entity.label = label
        if description is not None:
            entity.description = description
        return self.add(entity)


class FakeCourseRepository(DictFakeRepo[Course], ICourseRepository):
    def list_courses(self, limit: int | None = None, offset: int = 0) -> Sequence[Course]:
        items = list(self._store.values())
        items.sort(key=lambda c: ((c.end_date or date.min), c.id), reverse=True)
        return items[offset : offset + limit] if limit is not None else items

    def get_course_by_id(self, course_id: int) -> Course | None:
        return self.get(course_id)

    def list_past_courses(self) -> Sequence[Course]:
        today = date.today()
        items = [c for c in self._store.values() if c.end_date and c.end_date < today]
        items.sort(key=lambda c: ((c.end_date or date.min), c.id), reverse=True)
        return items

    def search_courses(self, q: str) -> Sequence[Course]:
        qcf = q.casefold()
        items = [c for c in self._store.values() if qcf in c.title.casefold()]
        items.sort(key=lambda c: ((c.end_date or date.min), c.id), reverse=True)
        return items

    def create_course(
        self,
        *,
        title: str,
        description: str | None,
        delivery_mode_id: int,
        venue_id: int | None,
        instructor_ids: list[int],
        start_date: date | None,
        end_date: date | None,
        **kwargs: Any,
    ) -> Course:
        if not title:
            raise ValueError("title is required")
        if start_date and end_date and end_date < start_date:
            raise ValueError("end_date cannot be before start_date")

        course = Course(
            title=title,
            description=description,
            delivery_mode_id=delivery_mode_id,
            venue_id=venue_id,
            start_date=start_date,
            end_date=end_date,
            **{k: v for k, v in kwargs.items() if hasattr(Course, k)},
        )
        try:
            if delivery_mode_id is not None:
                dm = DeliveryMode(id=delivery_mode_id, label=f"dm-{delivery_mode_id}")
                course.delivery_mode = dm
        except Exception:
            pass
        return self.add(course)


    def add(self, entity: Course) -> Course:
        try:
            from app.models import DeliveryMode

            if getattr(entity, "delivery_mode_id", None) is not None and getattr(entity, "delivery_mode", None) is None:
                entity.delivery_mode = DeliveryMode(id=entity.delivery_mode_id, label=f"dm-{entity.delivery_mode_id}")
        except Exception:
            pass
        return super().add(entity)


# --- Fixtures ---


@pytest.fixture
def fake_delivery_modes() -> FakeDeliveryModeRepository:
    repo = FakeDeliveryModeRepository()
    repo.seed(
        DeliveryMode(label="Online", description="Remote"),
        DeliveryMode(label="In-Person", description="On site"),
        DeliveryMode(label="Hybrid", description="Mix"),
    )
    return repo


@pytest.fixture
def fake_event_types() -> FakeEventTypeRepository:
    return FakeEventTypeRepository()


@pytest.fixture
def fake_reg_statuses() -> FakeRegistrationStatusRepository:
    repo = FakeRegistrationStatusRepository()
    repo.seed(
        RegistrationStatus(label="pending", description=None),
        RegistrationStatus(label="confirmed", description=None),
        RegistrationStatus(label="cancelled", description=None),
    )
    return repo


@pytest.fixture
def fake_courses() -> FakeCourseRepository:
    return FakeCourseRepository()


@pytest.fixture
def fake_venues() -> DictFakeRepo[Venue]:
    return DictFakeRepo()


class _DummyCtx:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:  # type: ignore[override]
        return False


class _TestSessionProtocol(Protocol):
    """A lightweight protocol describing the minimal session-like API used
    by service unit tests. Tests can annotate fixtures with this type to keep
    linters/pyright happy without depending on SQLAlchemy types.
    """

    def begin_nested(self) -> Any: ...

    def begin(self) -> Any: ...

    def delete(self, obj: Any) -> None: ...


class _DummySession:
    def begin_nested(self):
        return _DummyCtx()

    def begin(self):
        return _DummyCtx()

    def delete(self, _):
        # no-op; fake repos are authoritative for tests
        return None


@pytest.fixture
def dummy_session() -> _TestSessionProtocol:
    """A tiny, test-only session-like object used by service unit tests.

    Provides context manager methods used by services (`begin`, `begin_nested`) and a
    `delete` no-op. Keeps service tests independent from SQLAlchemy sessions.
    """
    return _DummySession()


@pytest.fixture
def client(fake_courses: FakeCourseRepository) -> Generator[FlaskClient, Any]:
    app = create_app()
    course_api_module.svc = CourseService(session=None, repo=fake_courses)
    with app.test_client() as c:
        yield c


@pytest.fixture
def seed_two_courses(fake_courses: FakeCourseRepository) -> tuple[int, int]:
    """Seed two deterministic courses and return their IDs in insertion order."""
    c1 = Course(
        title="A",
        description=None,
        delivery_mode_id=1,
        venue_id=None,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2),
    )
    c2 = Course(
        title="B",
        description=None,
        delivery_mode_id=1,
        venue_id=None,
        start_date=date(2024, 1, 3),
        end_date=date(2024, 1, 3),
    )
    fake_courses.seed(c1, c2)
    # Use public API to derive ids deterministically
    items = fake_courses.list_all()
    ids = tuple(i.id for i in items)
    return (ids[0], ids[1])


@pytest.fixture
def seeded_course_id(fake_courses: FakeCourseRepository) -> int:
    c = Course(
        title="X",
        description=None,
        delivery_mode_id=1,
        venue_id=None,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2),
    )
    fake_courses.seed(c)
    # Return the id of the single seeded course
    return fake_courses.list_all()[0].id
