from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest
from flask.testing import FlaskClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from app import create_app
from app.api.v1 import course as course_api_module
from app.api.v1 import instructor as instructor_api_module
from app.db import Base, db
from app.repositories import CourseRepository, DeliveryModeRepository, InstructorRepository
from app.services.course import CourseService
from app.services.instructor import InstructorService


@pytest.fixture
def file_engine(tmp_path: Path):
    """
    Per-test SQLite file database. This avoids teardown conflicts
    with Flask-SQLAlchemy and gives each test a fully isolated DB.
    """
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_file}", future=True)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        # drop everything for good measure
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def scoped_test_session(file_engine):
    """
    Flask-SQLAlchemy works with a *scoped_session*. We create one bound
    to the per-test file engine so teardown can safely call .remove().
    """
    SessionLocal = scoped_session(
        sessionmaker(bind=file_engine, future=True, expire_on_commit=False)
    )
    try:
        yield SessionLocal
    finally:
        # make sure Flask teardown sees a clean scoped session
        SessionLocal.remove()


@pytest.fixture
def course_repo(scoped_test_session) -> CourseRepository:
    return CourseRepository(session=scoped_test_session)

@pytest.fixture
def instructor_repo(scoped_test_session) -> InstructorRepository:
    return InstructorRepository(session=scoped_test_session)


@pytest.fixture
def delivery_mode_repo(scoped_test_session) -> DeliveryModeRepository:
    return DeliveryModeRepository(session=scoped_test_session)


@pytest.fixture
def course_svc(course_repo, scoped_test_session) -> CourseService:
    return CourseService(session=scoped_test_session, repo=course_repo)

@pytest.fixture
def instructor_svc(instructor_repo, scoped_test_session) -> CourseService:
    return InstructorService(session=scoped_test_session, repo=instructor_repo)


@pytest.fixture
def client(course_svc,instructor_svc, scoped_test_session, monkeypatch) -> Generator[FlaskClient]:
    """
    Flask client where:
      - the API module’s service is patched to our per-test service
      - Flask-SQLAlchemy’s db.session is the same scoped_session
    This keeps the app and tests on the same session/engine and lets
    Flask teardown call db.session.remove() without conflicts.
    """
    app = create_app()
    app.config.update(TESTING=True)

    # Route API module to our test service
    monkeypatch.setattr(course_api_module, "svc", course_svc, raising=True)
    monkeypatch.setattr(instructor_api_module, "svc", instructor_svc, raising=True)

    # Ensure anything in the app using db.session touches our scoped test session
    monkeypatch.setattr(db, "session", scoped_test_session, raising=True)

    with app.test_client() as c, app.app_context():
        yield c


# --- tiny seed helpers used by the tests ---


@pytest.fixture
def seed_delivery_modes(delivery_mode_repo, scoped_test_session):
    online = delivery_mode_repo.create(label="Online", description="Remote")
    inperson = delivery_mode_repo.create(label="In-Person", description="On site")
    scoped_test_session.flush()
    return {"online": online, "inperson": inperson}


@pytest.fixture
def seed_two_courses(course_repo, scoped_test_session, seed_delivery_modes):
    """
    Seed two deterministic courses with datetime values for start/end dates.
    This ensures the repository's date normalization works for datetime inputs too.
    """
    c1 = course_repo.create_course(
        title="A",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
    )

    c2 = course_repo.create_course(
        title="B",
        description=None,
        delivery_mode_id=seed_delivery_modes["online"].id,
        venue_id=None,
        instructor_ids=[],
        start_date=datetime(2024, 1, 3, 9, 0, 0),
        end_date=datetime(2024, 1, 4, 17, 0, 0),
    )

    scoped_test_session.flush()
    return (c1.id, c2.id)