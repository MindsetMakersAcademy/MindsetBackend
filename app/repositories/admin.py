from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, scoped_session

from app.db import db
from app.models import Admin
from app.repositories.base import BaseRepository


class IAdminRepository(ABC):
    """
    CRUD interface for admin users.
    """

    @abstractmethod
    def list_admins(self, *, limit: int = 100, offset: int = 0) -> Sequence[Admin]:
        """List admins ordered by id (desc)."""
        ...

    @abstractmethod
    def get_admin_by_id(self, admin_id: int) -> Admin | None:
        """Get an admin by id."""
        ...

    @abstractmethod
    def get_admin_by_email(self, email: str) -> Admin | None:
        """Get an admin by unique email."""
        ...

    @abstractmethod
    def create_admin(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        is_active: bool = True,
        **kwargs: Any,
    ) -> Admin:
        """Create an admin and return it."""
        ...

    @abstractmethod
    def update_admin(
        self,
        admin_id: int,
        *,
        email: str | None = None,
        full_name: str | None = None,
        password_hash: str | None = None,
        is_active: bool | None = None,
        **kwargs: Any,
    ) -> Admin | None:
        """Update an admin and return it (None if not found)."""
        ...

    @abstractmethod
    def delete_admin(self, admin_id: int) -> Admin | None:
        """Delete an admin and return the deleted row (None if not found)."""
        ...


class AdminRepository(BaseRepository[Admin], IAdminRepository):
    """
    Repository for Admin.

    - Eager loading is not necessary here (no heavy relationships by default).
    - Commits happen inside write methods for simplicity.
    """

    def __init__(self, session: Session | scoped_session[Session] | None = None) -> None:
        super().__init__(session or db.session, Admin)

    def _base_query(self) -> Select[tuple[Admin]]:
        return select(Admin)

    def _get_fully_loaded(self, admin_id: int) -> Admin | None:
        stmt = self._base_query().where(Admin.id == admin_id)
        return self.session.execute(stmt).scalars().first()

    def list_admins(self, *, limit: int = 100, offset: int = 0) -> Sequence[Admin]:
        stmt = self._base_query().order_by(Admin.id.desc()).limit(limit).offset(offset)
        return self.session.execute(stmt).scalars().all()

    def get_admin_by_id(self, admin_id: int) -> Admin | None:
        return self._get_fully_loaded(admin_id)

    def get_admin_by_email(self, email: str) -> Admin | None:
        stmt = self._base_query().where(Admin.email == email)
        return self.session.execute(stmt).scalars().first()

    def create_admin(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        is_active: bool = True,
        **kwargs,
    ) -> Admin:
        admin = Admin(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            is_active=is_active,
            **kwargs,
        )
        self.session.add(admin)
        self.session.commit()
        return self._get_fully_loaded(admin.id) or admin

    def update_admin(
        self,
        admin_id: int,
        *,
        email: str | None = None,
        full_name: str | None = None,
        password_hash: str | None = None,
        is_active: bool | None = None,
        **kwargs,
    ) -> Admin | None:
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            return None

        if email is not None:
            admin.email = email
        if full_name is not None:
            admin.full_name = full_name
        if password_hash is not None:
            admin.password_hash = password_hash
        if is_active is not None:
            admin.is_active = is_active

        for k, v in kwargs.items():
            if v is not None and hasattr(admin, k):
                setattr(admin, k, v)

        self.session.commit()
        return self._get_fully_loaded(admin.id)

    def delete_admin(self, admin_id: int) -> Admin | None:
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            return None
        self.session.delete(admin)
        self.session.commit()
        return admin
