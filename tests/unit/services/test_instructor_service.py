from __future__ import annotations

import pytest

from app.dtos import InstructorCreateDTO, InstructorUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.models import Instructor
from app.services.instructor import InstructorService
from tests.conftest import FakeInstructorRepository, _TestSessionProtocol


class TestInstructorService:
    """Tests for InstructorService."""

    def test_get_not_found_raises(
        self,
        fake_instructors: FakeInstructorRepository,
        dummy_session: _TestSessionProtocol,
    ):
        """Requesting a non-existent instructor ID raises NotFoundError."""
        svc = InstructorService(session=dummy_session)
        svc.repo = fake_instructors

        with pytest.raises(NotFoundError):
            svc.get(9999)

    def test_create_and_get(
        self,
        fake_instructors: FakeInstructorRepository,
        dummy_session: _TestSessionProtocol,
    ):
        """Creating an instructor returns DTO and can be fetched."""
        svc = InstructorService(session=dummy_session)
        svc.repo = fake_instructors

        payload = InstructorCreateDTO.model_validate(
            {
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+1234567890",
                "bio": "Expert instructor",
            }
        )

        created = svc.create(payload)
        assert created.full_name == "Jane Doe"
        assert isinstance(created.id, int)

        fetched = svc.get(created.id)
        assert fetched.full_name == "Jane Doe"
        assert fetched.email == "jane@example.com"

    def test_create_duplicate_email_raises(
        self,
        fake_instructors: FakeInstructorRepository,
        dummy_session: _TestSessionProtocol,
    ):
        """Creating instructor with existing email raises AlreadyExistsError."""
        svc = InstructorService(session=dummy_session)
        svc.repo = fake_instructors

        fake_instructors.seed(Instructor(full_name="John", email="john@example.com"))

        payload = InstructorCreateDTO.model_validate(
            {
                "full_name": "Jane",
                "email": "john@example.com",
            }
        )

        with pytest.raises(AlreadyExistsError):
            svc.create(payload)

    @pytest.mark.parametrize("bad_name", [" ", "   "])
    def test_create_empty_name_raises(
        self,
        fake_instructors: FakeInstructorRepository,
        bad_name: str,
        dummy_session: _TestSessionProtocol,
    ):
        """Creating with empty name is rejected."""
        svc = InstructorService(session=dummy_session, repo=fake_instructors)
        payload = InstructorCreateDTO.model_validate({"full_name": bad_name})

        with pytest.raises(ValidationError):
            svc.create(payload)

    def test_update_changes_fields(
        self,
        fake_instructors: FakeInstructorRepository,
        dummy_session: _TestSessionProtocol,
    ):
        """Update modifies instructor fields."""
        svc = InstructorService(session=dummy_session)
        svc.repo = fake_instructors

        instructor = fake_instructors.create(
            full_name="Old Name",
            email="old@example.com",
        )

        payload = InstructorUpdateDTO.model_validate(
            {
                "full_name": "New Name",
                "bio": "Updated bio",
            }
        )

        updated = svc.update(instructor.id, payload)
        assert updated.full_name == "New Name"
        assert updated.bio == "Updated bio"
        assert updated.email == "old@example.com"  
    def test_list_filters_by_query(
        self,
        fake_instructors: FakeInstructorRepository,
        dummy_session: _TestSessionProtocol,
    ):
        """List method filters by name query."""
        svc = InstructorService(session=dummy_session)
        svc.repo = fake_instructors

        fake_instructors.seed(
            Instructor(full_name="Alice Smith"),
            Instructor(full_name="Bob Jones"),
            Instructor(full_name="Alice Johnson"),
        )

        results = svc.list(q="alice")
        assert len(results) == 2
        assert all("alice" in r.full_name.lower() for r in results)
