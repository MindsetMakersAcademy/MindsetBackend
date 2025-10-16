"""Test configuration and fixtures."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from app import create_app
from app.config import Config
from app.db import db as _db
from app.models import Course, DeliveryMode, Instructor, Venue


class TestConfig(Config):
    """Test configuration with SQLite memory database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def app() -> Flask:
    """Create Flask application for testing."""
    app = create_app(TestConfig)
    return app


@pytest.fixture(scope="session")
def db(app: Flask):
    """Create database and tables, cleanup after all tests."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def session(db : SQLAlchemy):
    """Create a new database session for a test.
    
    Ensures test isolation by rolling back transaction after each test.
    """
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a scoped session
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    
    # Override the default session
    _db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_data(session):
    """Create sample course data with relationships."""
    # Create delivery modes
    online = DeliveryMode(id=1, label="Online")
    in_person = DeliveryMode(id=2, label="In-Person")
    session.add_all([online, in_person])

    # Create venues
    venue1 = Venue(id=1, name="Main Campus")
    venue2 = Venue(id=2, name="Downtown Branch")
    session.add_all([venue1, venue2])

    # Create instructors
    instructor1 = Instructor(id=1, full_name="John Doe")
    instructor2 = Instructor(id=2, full_name="Jane Smith")
    session.add_all([instructor1, instructor2])

    # Create courses (some past, some future)
    now = datetime.now(UTC)
    
    past_course1 = Course(
        id=1,
        title="Past Python Course",
        description="Basic Python programming",
        delivery_mode=online,
        venue=venue1,
        start_date=(now - timedelta(days=60)).date(),
        end_date=(now - timedelta(days=30)).date(),
    )
    past_course1.instructors.append(instructor1)

    past_course2 = Course(
        id=2,
        title="Past Web Development",
        description="Web development bootcamp",
        delivery_mode=in_person,
        venue=venue2,
        start_date=(now - timedelta(days=45)).date(),
        end_date=(now - timedelta(days=15)).date(),
    )
    past_course2.instructors.extend([instructor1, instructor2])

    future_course = Course(
        id=3,
        title="Upcoming Data Science",
        description="Data science fundamentals",
        delivery_mode=online,
        venue=venue1,
        start_date=(now + timedelta(days=15)).date(),
        end_date=(now + timedelta(days=45)).date(),
    )
    future_course.instructors.append(instructor2)

    session.add_all([past_course1, past_course2, future_course])
    session.commit()

    return {
        "delivery_modes": [online, in_person],
        "venues": [venue1, venue2],
        "instructors": [instructor1, instructor2],
        "courses": [past_course1, past_course2, future_course],
    }