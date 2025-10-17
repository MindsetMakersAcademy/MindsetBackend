"""Database CLI commands.

Schema initialization and idempotent seeders for reference data.

Usage:
  flask cli db --help
  flask cli db init
  flask cli db seed
"""

from __future__ import annotations

import rich_click as click
from flask.cli import with_appcontext
from sqlalchemy import select

from app.db import db
from app.models import DeliveryMode, EventType, RegistrationStatus

from .common import CONTEXT_SETTINGS

db_group = click.Group(
    "db",
    help="Database operations: initialize schema and seed reference data.",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)


class DatabaseCLI:
    """Database schema and seed commands."""

    @staticmethod
    @db_group.command(
        name="init",
        short_help="Create all tables (no migrations).",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    def initialize_database_schema() -> None:
        """Create all tables using SQLAlchemy's metadata (no migrations)."""
        db.create_all()
        click.echo("✅ Initialized database schema.")

    @staticmethod
    @db_group.command(
        name="seed-modes",
        short_help="Seed DeliveryMode reference rows.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    def seed_delivery_modes() -> None:
        """Seed DeliveryMode records (idempotent)."""
        click.echo("Seeding DeliveryMode…")
        delivery_modes = [
            {"label": "In-Person", "description": None},
            {"label": "Online", "description": None},
            {"label": "Hybrid", "description": None},
        ]
        created = updated = 0
        with db.session.no_autoflush:
            for mode in delivery_modes:
                existing = (
                    db.session.execute(
                        select(DeliveryMode).where(DeliveryMode.label == mode["label"])
                    )
                    .scalars()
                    .one_or_none()
                )
                if not existing:
                    db.session.add(DeliveryMode(**mode))
                    created += 1
                elif existing.description != mode["description"]:
                    existing.description = mode["description"]
                    updated += 1
        db.session.commit()
        click.echo(f"✅ DeliveryMode: created={created} updated={updated}")

    @staticmethod
    @db_group.command(
        name="seed-registration-statuses",
        short_help="Seed RegistrationStatus reference rows.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    def seed_registration_statuses() -> None:
        """Seed RegistrationStatus records (idempotent)."""
        click.echo("Seeding RegistrationStatus…")
        statuses = [
            {
                "label": "Registered",
                "description": "Enrollment is confirmed and a seat is reserved for the participant. All required steps (e.g., approval/payment) have been completed.",
            },
            {
                "label": "Submitted",
                "description": "Registration request has been received but is not yet confirmed. Pending review, approval, or payment.",
            },
            {
                "label": "Waitlisted",
                "description": "The class is currently full; the participant is queued for a seat. No guarantee of placement; will be notified if a spot opens.",
            },
            {
                "label": "Cancelled",
                "description": "The registration was withdrawn by the participant or an admin. The seat (if any) is released; refund policies may apply.",
            },
        ]
        created = updated = 0
        with db.session.no_autoflush:
            for s in statuses:
                existing = (
                    db.session.execute(
                        select(RegistrationStatus).where(RegistrationStatus.label == s["label"])
                    )
                    .scalars()
                    .one_or_none()
                )
                if not existing:
                    db.session.add(RegistrationStatus(**s))
                    created += 1
                elif existing.description != s["description"]:
                    existing.description = s["description"]
                    updated += 1
        db.session.commit()
        click.echo(f"✅ RegistrationStatus: created={created} updated={updated}")

    @staticmethod
    @db_group.command(
        name="seed-event-types",
        short_help="Seed EventType reference rows.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    def seed_event_types() -> None:
        """Seed EventType records (idempotent)."""
        click.echo("Seeding EventType…")
        event_types = [
            {"label": "Book Club", "description": None},
            {"label": "Talk", "description": None},
            {"label": "Webinar", "description": None},
            {"label": "Workshop", "description": None},
        ]
        created = updated = 0
        with db.session.no_autoflush:
            for et in event_types:
                existing = (
                    db.session.execute(select(EventType).where(EventType.label == et["label"]))
                    .scalars()
                    .one_or_none()
                )
                if not existing:
                    db.session.add(EventType(**et))
                    created += 1
                elif existing.description != et["description"]:
                    existing.description = et["description"]
                    updated += 1
        db.session.commit()
        click.echo(f"✅ EventType: created={created} updated={updated}")

    @staticmethod
    @db_group.command(
        name="seed", short_help="Seed all reference data.", context_settings=CONTEXT_SETTINGS
    )
    @with_appcontext
    def seed_all_reference_data() -> None:
        """Seed DeliveryMode + RegistrationStatus + EventType (idempotent)."""
        DatabaseCLI.seed_delivery_modes.callback()  # type: ignore[attr-defined]
        DatabaseCLI.seed_registration_statuses.callback()  # type: ignore[attr-defined]
        DatabaseCLI.seed_event_types.callback()  # type: ignore[attr-defined]
        click.echo("✅ All reference data seeded.")
