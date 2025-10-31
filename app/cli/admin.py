"""Admin CLI commands for Mindset Backend."""

from __future__ import annotations

import rich_click as click

from app.dtos import AdminCreate, AdminUpdate
from app.services.admin import AdminService
from .common import CONTEXT_SETTINGS

admin_group = click.Group(
    "admin",
    help="Admin management commands.",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)


class AdminCLI:
    @staticmethod
    @admin_group.command("list", help="List all admins.")
    def list_admins() -> None:
        svc = AdminService()
        admins = svc.list_admins()
        for admin in admins:
            click.echo(f"{admin.id}: {admin.email} ({admin.full_name}) - Active: {admin.is_active}")

    @staticmethod
    @admin_group.command("create", help="Create a new admin.")
    @click.option("--email", required=True, help="Admin email.")
    @click.option("--full-name", required=True, help="Admin full name.")
    @click.option("--password", required=True, help="Admin password.")
    def create_admin(email: str, full_name: str, password: str) -> None:
        svc = AdminService()
        payload = AdminCreate(email=email, full_name=full_name, password=password)
        admin = svc.create_admin(payload)
        click.echo(f"Created admin: {admin.email} ({admin.full_name})")

    @staticmethod
    @admin_group.command("update", help="Update an admin.")
    @click.option("--id", required=True, type=int, help="Admin ID.")
    @click.option("--email", help="New email.")
    @click.option("--full-name", help="New full name.")
    @click.option("--password", help="New password.")
    @click.option("--is-active", type=bool, help="Set active status.")
    def update_admin(
        id: int,
        email: str | None,
        full_name: str | None,
        password: str | None,
        is_active: bool | None,
    ) -> None:
        svc = AdminService()
        payload = AdminUpdate(
            email=email, full_name=full_name, password=password, is_active=is_active
        )
        admin = svc.update_admin(id, payload)
        click.echo(f"Updated admin: {admin.email} ({admin.full_name})")

    @staticmethod
    @admin_group.command("delete", help="Delete an admin.")
    @click.option("--id", required=True, type=int, help="Admin ID.")
    def delete_admin(id: int) -> None:
        svc = AdminService()
        svc.delete_admin(id)
        click.echo(f"Deleted admin with ID: {id}")

    @staticmethod
    @admin_group.command("get", help="Get admin by ID.")
    @click.option("--id", required=True, type=int, help="Admin ID.")
    def get_admin(id: int) -> None:
        svc = AdminService()
        admin = svc.get_admin(id)
        click.echo(f"{admin.id}: {admin.email} ({admin.full_name}) - Active: {admin.is_active}")
