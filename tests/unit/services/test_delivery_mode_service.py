from __future__ import annotations

import pytest

from app.dtos import DeliveryModeCreateDTO, DeliveryModeUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.models import DeliveryMode
from app.services.delivery_mode import DeliveryModeService
from tests.conftest import FakeDeliveryModeRepository, _TestSessionProtocol


class TestDeliveryModeService:
    def test_get_not_found_raises(
        self, fake_delivery_modes: FakeDeliveryModeRepository, dummy_session: _TestSessionProtocol
    ):
        """Requesting a non-existent delivery mode id raises NotFoundError."""
        svc = DeliveryModeService(session=dummy_session)
        svc.repo = fake_delivery_modes

        with pytest.raises(NotFoundError):
            svc.get(9999)

    @pytest.mark.parametrize("label,desc", [("New", "d"), ("Another", None)])
    def test_create_and_get(
        self,
        fake_delivery_modes: FakeDeliveryModeRepository,
        label: str,
        desc: str | None,
        dummy_session: _TestSessionProtocol,
    ):
        """Creating valid delivery modes returns the created DTO and can be fetched."""
        svc = DeliveryModeService(session=dummy_session)
        svc.repo = fake_delivery_modes

        payload = DeliveryModeCreateDTO.model_validate({"label": label, "description": desc})
        out = svc.create(payload)

        assert out.label == label
        assert isinstance(out.id, int)

        fetched = svc.get(out.id)
        assert fetched.label == label

    def test_create_duplicate_raises(
        self, fake_delivery_modes: FakeDeliveryModeRepository, dummy_session: _TestSessionProtocol
    ):
        """Creating a delivery mode with an existing label raises AlreadyExistsError."""
        svc = DeliveryModeService(session=dummy_session)
        svc.repo = fake_delivery_modes

        fake_delivery_modes.seed(DeliveryMode(label="X"))

        payload = DeliveryModeCreateDTO.model_validate({"label": "X", "description": None})
        with pytest.raises(AlreadyExistsError):
            svc.create(payload)

    @pytest.mark.parametrize("badlabel", ["", "   ", "a" * 161])
    def test_create_invalid_label_raises(
        self, fake_delivery_modes: FakeDeliveryModeRepository, badlabel: str, dummy_session: _TestSessionProtocol
    ):
        """Invalid label values are rejected by validation logic."""
        svc = DeliveryModeService(session=dummy_session)
        svc.repo = fake_delivery_modes

        payload = DeliveryModeCreateDTO.model_validate({"label": badlabel, "description": None})
        with pytest.raises(ValidationError):
            svc.create(payload)

    def test_update_changes_label_and_description(
        self, fake_delivery_modes: FakeDeliveryModeRepository, dummy_session: _TestSessionProtocol
    ):
        """Update modifies label and description on existing delivery mode."""
        svc = DeliveryModeService(session=dummy_session)
        svc.repo = fake_delivery_modes

        dm = fake_delivery_modes.create(label="orig", description="o")
        payload = DeliveryModeUpdateDTO.model_validate({"label": "new", "description": "n"})

        out = svc.update(dm.id, payload)
        assert out.label == "new"
        assert out.description == "n"
