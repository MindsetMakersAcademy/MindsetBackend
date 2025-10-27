from __future__ import annotations

import pytest

from app.dtos import EventTypeCreateDTO
from app.exceptions import AlreadyExistsError, ValidationError
from app.models import EventType
from app.services.event_type import EventTypeService
from tests.conftest import FakeEventTypeRepository, _TestSessionProtocol


class TestEventTypeService:
    def test_create_and_get(self, fake_event_types: FakeEventTypeRepository, dummy_session: _TestSessionProtocol):
        """Creating an event type should return an object which we can fetch by label."""
        svc = EventTypeService(session=dummy_session)
        svc.repo = fake_event_types

        payload = EventTypeCreateDTO.model_validate({"label": "ET", "description": "d"})
        out = svc.create(payload)
        assert out.label == "ET"
        assert isinstance(out.id, int)

        fetched = svc.get_by_label("ET")
        assert fetched.id == out.id

    def test_create_duplicate_raises(self, fake_event_types: FakeEventTypeRepository, dummy_session: _TestSessionProtocol):
        """Attempting to create a duplicate event type label raises AlreadyExistsError."""
        svc = EventTypeService(session=dummy_session)
        svc.repo = fake_event_types

        fake_event_types.seed(EventType(label="Y"))

        payload = EventTypeCreateDTO.model_validate({"label": "Y", "description": None})
        with pytest.raises(AlreadyExistsError):
            svc.create(payload)

    @pytest.mark.parametrize("badlabel", ["", "   ", "a" * 161])
    def test_invalid_label_raises(
        self, fake_event_types: FakeEventTypeRepository, badlabel: str, dummy_session: _TestSessionProtocol
    ):
        """Validation rejects empty or too-long labels."""
        svc = EventTypeService(session=dummy_session)
        svc.repo = fake_event_types

        payload = EventTypeCreateDTO.model_validate({"label": badlabel, "description": None})
        with pytest.raises(ValidationError):
            svc.create(payload)
