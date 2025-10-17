"""Delivery Mode CLI commands.

Manage DeliveryMode lookup used by Courses and Events (In-Person, Online, Hybrid).

Usage:
  flask cli delivery-mode --help
"""

from __future__ import annotations

import json
import sys

import rich_click as click
from flask.cli import with_appcontext

from app.dtos import DeliveryModeCreateDTO, DeliveryModeReadDTO, DeliveryModeUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.services.delivery_mode import DeliveryModeService

from .common import CONTEXT_SETTINGS

delivery_mode_group = click.Group(
    "delivery-mode",
    help="Manage delivery modes reference data.",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)


class DeliveryModeCLI:
    """Commands for the DeliveryMode entity."""

    @staticmethod
    @delivery_mode_group.command(
        "list", context_settings=CONTEXT_SETTINGS, short_help="List delivery modes."
    )
    @with_appcontext
    @click.option("-q", "--query", default=None, metavar="TEXT", help="ILIKE filter on label.")
    @click.option(
        "-s", "--sort", type=click.Choice(["label", "id"]), default="label", show_default=True
    )
    @click.option(
        "-d",
        "--dir",
        "direction",
        type=click.Choice(["asc", "desc"]),
        default="asc",
        show_default=True,
    )
    @click.option("-j", "--json", "as_json", is_flag=True, help="Output JSON.")
    def list_(query: str | None, sort: str, direction: str, as_json: bool) -> None:
        """List DeliveryMode records."""
        svc = DeliveryModeService()
        items = svc.list(q=query, sort=sort, direction=direction)
        if as_json:
            click.echo(json.dumps([i.model_dump() for i in items], indent=2))
        else:
            for it in items:
                click.echo(f"- [{it.id}] {it.label}  {it.description or ''}")

    @staticmethod
    @delivery_mode_group.command(
        "create", context_settings=CONTEXT_SETTINGS, short_help="Create a delivery mode."
    )
    @with_appcontext
    @click.argument("label", metavar="LABEL")
    @click.option("-D", "--desc", "description", default=None, metavar="TEXT")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def create_(label: str, description: str | None, as_json: bool) -> None:
        """Create a new DeliveryMode."""
        svc = DeliveryModeService()
        try:
            out: DeliveryModeReadDTO = svc.create(
                DeliveryModeCreateDTO(label=label, description=description)
            )
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Created [{out.id}] {out.label}"
            )
        except (AlreadyExistsError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @delivery_mode_group.command(
        "update", context_settings=CONTEXT_SETTINGS, short_help="Update a delivery mode by id."
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    @click.option("-l", "--label", default=None, metavar="TEXT")
    @click.option("-D", "--desc", "description", default=None, metavar="TEXT")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def update_(id_: int, label: str | None, description: str | None, as_json: bool) -> None:
        """Update a DeliveryMode by id."""
        if label is None and description is None:
            click.echo("❌ Nothing to update. Provide -l/--label and/or -D/--desc.", err=True)
            sys.exit(2)
        svc = DeliveryModeService()
        try:
            out = svc.update(id_, DeliveryModeUpdateDTO(label=label, description=description))
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Updated [{out.id}] {out.label}"
            )
        except (NotFoundError, AlreadyExistsError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @delivery_mode_group.command(
        "delete", context_settings=CONTEXT_SETTINGS, short_help="Delete a delivery mode."
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    def delete_(id_: int) -> None:
        """Delete a DeliveryMode by id."""
        svc = DeliveryModeService()
        try:
            svc.delete(id_)
            click.echo("✅ Deleted.")
        except NotFoundError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @delivery_mode_group.command(
        "get", context_settings=CONTEXT_SETTINGS, short_help="Get a delivery mode by id."
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    @click.option("-j", "--json", "as_json", is_flag=True)
    def get_(id_: int, as_json: bool) -> None:
        """Fetch a DeliveryMode by id."""
        svc = DeliveryModeService()
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
