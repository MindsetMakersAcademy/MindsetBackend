from __future__ import annotations

import pytest

from app.dtos import RegistrationStatusCreateDTO, RegistrationStatusUpdateDTO
from app.exceptions import AlreadyExistsError, ValidationError
from app.models import RegistrationStatus
from app.services.registration_status import RegistrationStatusService
from tests.conftest import FakeRegistrationStatusRepository, _TestSessionProtocol


class TestRegistrationStatusService:
    def test_list_default_sort_and_get(
        self, fake_reg_statuses: FakeRegistrationStatusRepository, dummy_session: _TestSessionProtocol
    ):
        """Listing returns seeded default statuses and maintains expected labels."""
        svc = RegistrationStatusService(session=dummy_session)
        svc.repo = fake_reg_statuses

        items = svc.list()
        assert isinstance(items, list)
        labels = {it.label for it in items}
        assert labels >= {"pending", "confirmed", "cancelled"}

    def test_create_duplicate_raises(
        self, fake_reg_statuses: FakeRegistrationStatusRepository, dummy_session: _TestSessionProtocol
    ):
        """Creating a duplicate registration status label raises AlreadyExistsError."""
        svc = RegistrationStatusService(session=dummy_session)
        svc.repo = fake_reg_statuses

        fake_reg_statuses.seed(RegistrationStatus(label="dup"))
        payload = RegistrationStatusCreateDTO.model_validate({"label": "dup", "description": None})
        with pytest.raises(AlreadyExistsError):
            svc.create(payload)

    def test_update_label_conflict_raises(
        self, fake_reg_statuses: FakeRegistrationStatusRepository, dummy_session: _TestSessionProtocol
    ):
        """Updating a status label to one that already exists raises AlreadyExistsError."""
        svc = RegistrationStatusService(session=dummy_session)
        svc.repo = fake_reg_statuses

        a = fake_reg_statuses.create(label="a")
        b = fake_reg_statuses.create(label="b")

        payload = RegistrationStatusUpdateDTO.model_validate({"label": "b", "description": None})
        with pytest.raises(AlreadyExistsError):
            svc.update(a.id, payload)

    @pytest.mark.parametrize("badlabel", ["", "   ", "x" * 65])
    def test_invalid_label_raises(
        self, fake_reg_statuses: FakeRegistrationStatusRepository, badlabel: str, dummy_session: _TestSessionProtocol
    ):
        """Creating with invalid labels is rejected by validation."""
        svc = RegistrationStatusService(session=dummy_session)
        svc.repo = fake_reg_statuses

        payload = RegistrationStatusCreateDTO.model_validate({"label": badlabel, "description": None})
        with pytest.raises(ValidationError):
            svc.create(payload)
