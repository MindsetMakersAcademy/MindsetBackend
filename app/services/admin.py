from __future__ import annotations

from collections.abc import Sequence

from werkzeug.security import generate_password_hash

from app.dtos import AdminCreate, AdminOut, AdminUpdate
from app.exceptions import ConflictError, NotFoundError
from app.repositories import AdminRepository, IAdminRepository


class AdminService:
    """Application service for admin users."""

    def __init__(self, repo: IAdminRepository | None = None) -> None:
        self.repo = repo or AdminRepository()

    def list_admins(self, *, limit: int = 100, offset: int = 0) -> Sequence[AdminOut]:
        rows = self.repo.list_admins(limit=limit, offset=offset)
        return [AdminOut.model_validate(r) for r in rows]

    def get_admin(self, admin_id: int) -> AdminOut:
        row = self.repo.get_admin_by_id(admin_id)
        if not row:
            raise NotFoundError("Admin not found")
        return AdminOut.model_validate(row)

    def create_admin(self, payload: AdminCreate) -> AdminOut:
        if self.repo.get_admin_by_email(payload.email):
            raise ConflictError("Email already exists")
        pw_hash = generate_password_hash(payload.password)
        row = self.repo.create_admin(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=pw_hash,
            is_active=True,
        )
        return AdminOut.model_validate(row)

    def update_admin(self, admin_id: int, payload: AdminUpdate) -> AdminOut:
        if payload.password:
            payload.password = generate_password_hash(payload.password)

        row = self.repo.update_admin(
            admin_id=admin_id,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=payload.password,
            is_active=payload.is_active,
        )
        if not row:
            raise NotFoundError("Admin not found")
        return AdminOut.model_validate(row)

    def delete_admin(self, admin_id: int) -> None:
        row = self.repo.delete_admin(admin_id)
        if not row:
            raise NotFoundError("Admin not found")
