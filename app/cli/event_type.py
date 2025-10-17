"""Event Type CLI commands.

Manage EventType lookup (Book Club, Talk, Webinar, Workshop).

Usage:
  flask cli event-type --help
"""

from __future__ import annotations

import json
import sys

import rich_click as click
from flask.cli import with_appcontext

from app.dtos import EventTypeCreateDTO, EventTypeReadDTO, EventTypeUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.services.event_type import EventTypeService

from .common import CONTEXT_SETTINGS

event_type_group = click.Group(
    "event-type",
    help="Manage event types reference data.",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)


class EventTypeCLI:
    """Commands for the EventType entity."""

    @staticmethod
    @event_type_group.command(
        "list", context_settings=CONTEXT_SETTINGS, short_help="List event types."
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
        """List EventType records."""
        svc = EventTypeService()
        items = svc.list(q=query, sort=sort, direction=direction)
        if as_json:
            click.echo(json.dumps([i.model_dump() for i in items], indent=2))
        else:
            for it in items:
                click.echo(f"- [{it.id}] {it.label}  {it.description or ''}")

    @staticmethod
    @event_type_group.command(
        "create", context_settings=CONTEXT_SETTINGS, short_help="Create an event type."
    )
    @with_appcontext
    @click.argument("label", metavar="LABEL")
    @click.option("-D", "--desc", "description", default=None, metavar="TEXT")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def create_(label: str, description: str | None, as_json: bool) -> None:
        """Create a new EventType."""
        svc = EventTypeService()
        try:
            out: EventTypeReadDTO = svc.create(
                EventTypeCreateDTO(label=label, description=description)
            )
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Created [{out.id}] {out.label}"
            )
        except (AlreadyExistsError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @event_type_group.command(
        "update", context_settings=CONTEXT_SETTINGS, short_help="Update an event type by id."
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    @click.option("-l", "--label", default=None, metavar="TEXT")
    @click.option("-D", "--desc", "description", default=None, metavar="TEXT")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def update_(id_: int, label: str | None, description: str | None, as_json: bool) -> None:
        """Update an EventType by id."""
        if label is None and description is None:
            click.echo("❌ Nothing to update. Provide -l/--label and/or -D/--desc.", err=True)
            sys.exit(2)
        svc = EventTypeService()
        try:
            out = svc.update(id_, EventTypeUpdateDTO(label=label, description=description))
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Updated [{out.id}] {out.label}"
            )
        except (NotFoundError, AlreadyExistsError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @event_type_group.command(
        "delete", context_settings=CONTEXT_SETTINGS, short_help="Delete an event type."
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    def delete_(id_: int) -> None:
        """Delete an EventType by id."""
        svc = EventTypeService()
        try:
            svc.delete(id_)
            click.echo("✅ Deleted.")
        except NotFoundError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @event_type_group.command(
        "get", context_settings=CONTEXT_SETTINGS, short_help="Get an event type by id."
    )
    @with_appcontext
    @click.argument("id_", metavar="ID", type=int)
    @click.option("-j", "--json", "as_json", is_flag=True)
    def get_(id_: int, as_json: bool) -> None:
        """Fetch an EventType by id."""
        svc = EventTypeService()
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
