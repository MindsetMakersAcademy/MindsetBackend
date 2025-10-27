"""Venue CLI commands.

Administer venues used by courses/events (create/list/update/delete/get).

Usage:
  flask cli venue --help
"""

from __future__ import annotations

import json
import sys

import rich_click as click
from flask.cli import with_appcontext

from app.dtos import VenueCreateDTO, VenueReadDTO, VenueUpdateDTO
from app.exceptions import NotFoundError, ValidationError
from app.services.venue import VenueService

from .common import CONTEXT_SETTINGS

venue_group = click.Group(
    "venue",
    help="Manage venues (CRUD admin).",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)


class VenueCLI:
    """Commands for the Venue entity."""

    @staticmethod
    @venue_group.command("list", context_settings=CONTEXT_SETTINGS, short_help="List venues.")
    @with_appcontext
    @click.option("-q", "--query", default=None, metavar="TEXT", help="ILIKE filter on name.")
    @click.option(
        "-s", "--sort", type=click.Choice(["name", "id"]), default="name", show_default=True
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
        """List Venue records."""
        svc = VenueService()
        items = svc.list(q=query, sort=sort, direction=direction)
        if as_json:
            click.echo(json.dumps([i.model_dump() for i in items], indent=2))
        else:
            for it in items:
                click.echo(
                    f"- [{it.id}] {it.name}  cap={it.room_capacity or '-'}  {it.address or ''}"
                )

    @staticmethod
    @venue_group.command("create", context_settings=CONTEXT_SETTINGS, short_help="Create a venue.")
    @with_appcontext
    @click.argument("name")
    @click.option("--address", default=None, metavar="TEXT")
    @click.option("--map-url", "map_url", default=None, metavar="URL")
    @click.option("--notes", default=None, metavar="TEXT")
    @click.option("--room-capacity", "room_capacity", type=int, default=None, metavar="INT")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def create_(
        name: str,
        address: str | None,
        map_url: str | None,
        notes: str | None,
        room_capacity: int | None,
        as_json: bool,
    ) -> None:
        """Create a new Venue."""
        svc = VenueService()
        try:
            out: VenueReadDTO = svc.create(
                VenueCreateDTO(
                    name=name,
                    address=address,
                    map_url=map_url,
                    notes=notes,
                    room_capacity=room_capacity,
                )
            )
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Created [{out.id}] {out.name}"
            )
        except ValidationError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @venue_group.command(
        "update", context_settings=CONTEXT_SETTINGS, short_help="Update a venue by id."
    )
    @with_appcontext
    @click.argument("id_", type=int, metavar="ID")
    @click.option("--name", default=None, metavar="TEXT")
    @click.option("--address", default=None, metavar="TEXT")
    @click.option("--map-url", "map_url", default=None, metavar="URL")
    @click.option("--notes", default=None, metavar="TEXT")
    @click.option("--room-capacity", "room_capacity", type=int, default=None, metavar="INT")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def update_(
        id_: int,
        name: str | None,
        address: str | None,
        map_url: str | None,
        notes: str | None,
        room_capacity: int | None,
        as_json: bool,
    ) -> None:
        """Update a Venue by id."""
        if all(v is None for v in [name, address, map_url, notes, room_capacity]):
            click.echo("❌ Nothing to update.", err=True)
            sys.exit(2)
        svc = VenueService()
        try:
            out = svc.update(
                id_,
                VenueUpdateDTO(
                    name=name,
                    address=address,
                    map_url=map_url,
                    notes=notes,
                    room_capacity=room_capacity,
                ),
            )
            click.echo(
                out.model_dump_json(indent=2) if as_json else f"✅ Updated [{out.id}] {out.name}"
            )
        except (NotFoundError, ValidationError) as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @venue_group.command("delete", context_settings=CONTEXT_SETTINGS, short_help="Delete a venue.")
    @with_appcontext
    @click.argument("id_", type=int, metavar="ID")
    def delete_(id_: int) -> None:
        """Delete a Venue by id."""
        svc = VenueService()
        try:
            svc.delete(id_)
            click.echo("✅ Deleted.")
        except NotFoundError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)

    @staticmethod
    @venue_group.command("get", context_settings=CONTEXT_SETTINGS, short_help="Get a venue by id.")
    @with_appcontext
    @click.argument("id_", type=int, metavar="ID")
    @click.option("-j", "--json", "as_json", is_flag=True)
    def get_(id_: int, as_json: bool) -> None:
        """Fetch a Venue by id."""
        svc = VenueService()
        try:
            dto = svc.get(id_)
            click.echo(
                dto.model_dump_json(indent=2)
                if as_json
                else f"[{dto.id}] {dto.name}  cap={dto.room_capacity or '-'}"
            )
        except NotFoundError as e:
            click.echo(f"❌ {e}", err=True)
            sys.exit(1)
