from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.sql.elements import ColumnElement

from app.models import RegistrationStatus
from app.repositories.base import BaseRepository


class IRegistrationStatusRepository(ABC):
    """Abstract interface for RegistrationStatus repository."""

    @abstractmethod
    def get_by_id(self, id_: int) -> RegistrationStatus | None:
        """Retrieve a registration status by its ID."""
        ...

    @abstractmethod
    def get_by_label(self, label: str) -> RegistrationStatus | None:
        """Retrieve a registration status by its label."""
        ...

    @abstractmethod
    def _sort_column(self, key: str) -> ColumnElement[int | str]:
        """Resolve the sort column for a list query."""
        ...

    @abstractmethod
    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "label",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[RegistrationStatus]:
        """
        List registration statuses (optionally filtered and sorted).

        :param q: Optional substring filter on label (ILIKE).
        :param sort: Sort key ('label' or 'id').
        :param direction: 'asc' or 'desc'.
        :return: List of matching statuses.
        """
        ...

    @abstractmethod
    def create(self, *, label: str, description: str | None = None) -> RegistrationStatus:
        """Create a new registration status."""
        ...

    @abstractmethod
    def update(
        self,
        entity: RegistrationStatus,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> RegistrationStatus:
        """Update an existing registration status."""
        ...


class RegistrationStatusRepository(
    BaseRepository[RegistrationStatus], IRegistrationStatusRepository
):
    """Repository implementation for managing RegistrationStatus entities."""

    def __init__(self, session: Session | scoped_session[Session]):
        """
        :param session: SQLAlchemy session or scoped session.
        """
        super().__init__(session, RegistrationStatus)

    def get_by_id(self, id_: int) -> RegistrationStatus | None:
        """Retrieve a registration status by its ID."""
        return self.get(id_)

    def get_by_label(self, label: str) -> RegistrationStatus | None:
        """Retrieve a registration status by its label."""
        stmt = select(RegistrationStatus).where(RegistrationStatus.label == label)
        return self.session.execute(stmt).scalars().one_or_none()

    def _sort_column(self, key: str) -> ColumnElement[int | str]:
        """Resolve the sort column for a list query."""
        if key == "id":
            return RegistrationStatus.id
        return RegistrationStatus.label

    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "label",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[RegistrationStatus]:
        """
        List registration statuses (optionally filtered and sorted).
        """
        stmt = select(RegistrationStatus)
        if q:
            stmt = stmt.where(RegistrationStatus.label.ilike(f"%{q}%"))

        sort_col = self._sort_column(sort)
        stmt = stmt.order_by(sort_col.desc() if direction == "desc" else sort_col.asc())

        rows = cast(list[RegistrationStatus], self.session.execute(stmt).scalars().all())
        return rows

    def create(self, *, label: str, description: str | None = None) -> RegistrationStatus:
        """Create a new registration status."""
        entity = RegistrationStatus(label=label, description=description)
        self.add(entity)
        return entity

    def update(
        self,
        entity: RegistrationStatus,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> RegistrationStatus:
        """Update an existing registration status."""
        if label is not None:
            entity.label = label
        if description is not None:
            entity.description = description
        return entity
