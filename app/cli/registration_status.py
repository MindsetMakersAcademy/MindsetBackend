"""Registration Status CLI commands.

Manage the registration lifecycle lookup (Submitted, Registered, Waitlisted, etc).

Usage:
  flask cli registration-status --help
  flask cli registration-status list
  flask cli registration-status create "Registered"
"""

from __future__ import annotations

import json
import sys

import rich_click as click
from flask.cli import with_appcontext

from app.dtos import (
    RegistrationStatusCreateDTO,
    RegistrationStatusReadDTO,
    RegistrationStatusUpdateDTO,
)
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.services.registration_status import RegistrationStatusService

from .common import CONTEXT_SETTINGS

registration_status_group = click.Group(
    "registration-status",
    help="Manage registration status reference data.",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)


class RegistrationStatusCLI:
    """Commands for the RegistrationStatus entity."""

    @staticmethod
    @registration_status_group.command(
        name="list",
        short_help="List registration statuses (filter/sort, text or JSON).",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    @click.option("-q", "--query", default=None, metavar="TEXT", help="ILIKE filter on label.")
    @click.option(
        "-s",
        "--sort",
        type=click.Choice(["label", "id"]),
        default="label",
        show_default=True,
        help="Sort field.",
    )
    @click.option(
        "-d",
        "--dir",
        "direction",
        type=click.Choice(["asc", "desc"]),
        default="asc",
        show_default=True,
        help="Sort direction.",
    )
    @click.option("-j", "--json", "as_json", is_flag=True, help="Output JSON.")
    def list_(query: str | None, sort: str, direction: str, as_json: bool) -> None:
        """List registration statuses."""
        svc = RegistrationStatusService()
        items = svc.list(q=query, sort=sort, direction=direction)
        if as_json:
            click.echo(json.dumps([i.model_dump() for i in items], indent=2))
        else:
            for it in items:
                click.echo(f"- [{it.id}] {it.label}  {it.description or ''}")

    @staticmethod
    @registration_status_group.command(
        name="create",
        short_help="Create a new registration status.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    @click.argument("label", metavar="LABEL", type=str)
    @click.option("-D", "--desc", "description", default=None, metavar="TEXT", help="Description.")
    @click.option("-j", "--json", "as_json", is_flag=True, help="Output JSON.")
    def create_(label: str, description: str | None, as_json: bool) -> None:
        """Create a new registration status."""
        svc = RegistrationStatusService()
        try:
            out: RegistrationStatusReadDTO = svc.create(
                RegistrationStatusCreateDTO(label=label, description=description)
            )
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Created [{out.id}] {out.label}"
            )
        except (AlreadyExistsError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @registration_status_group.command(
        name="update",
        short_help="Update a registration status by id.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    @click.option("-l", "--label", default=None, metavar="TEXT", help="New label.")
    @click.option(
        "-D", "--desc", "description", default=None, metavar="TEXT", help="New description."
    )
    @click.option("-j", "--json", "as_json", is_flag=True, help="Output JSON.")
    def update_(id_: int, label: str | None, description: str | None, as_json: bool) -> None:
        """Update a registration status by id."""
        if label is None and description is None:
            click.echo("❌ Nothing to update. Provide -l/--label and/or -D/--desc.", err=True)
            sys.exit(2)
        svc = RegistrationStatusService()
        try:
            out = svc.update(id_, RegistrationStatusUpdateDTO(label=label, description=description))
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Updated [{out.id}] {out.label}"
            )
        except (NotFoundError, AlreadyExistsError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @registration_status_group.command(
        name="delete",
        short_help="Delete a registration status.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    def delete_(id_: int) -> None:
        """Delete a registration status."""
        svc = RegistrationStatusService()
        try:
            svc.delete(id_)
            click.echo("✅ Deleted.")
        except NotFoundError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @registration_status_group.command(
        name="get",
        short_help="Get a registration status by id.",
        context_settings=CONTEXT_SETTINGS,
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    @click.option("-j", "--json", "as_json", is_flag=True, help="Output JSON.")
    def get_(id_: int, as_json: bool) -> None:
        """Fetch a registration status by id."""
        svc = RegistrationStatusService()
        try:
            dto = svc.get(id_)
            click.echo(
                dto.model_dump_json(indent=2)
                if as_json
                else f"[{dto.id}] {dto.label}  {dto.description or ''}"
            )
        except NotFoundError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)
