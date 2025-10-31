"""CLI entrypoint for Mindset Backend.

This package wires a rich Click-based CLI under the top-level `cli` group and
registers the modular command groups:

  • registration-status
  • delivery-mode
  • event-type
  • venue
  • db

Usage (top-level):
  flask cli --help
  flask cli <group> --help
  flask cli <group> <command> --help
"""

from __future__ import annotations

import rich_click as click
from flask import Flask

from .admin import AdminCLI, admin_group
from .common import CONTEXT_SETTINGS, attach_commands_from_class
from .db import DatabaseCLI, db_group
from .delivery_mode import DeliveryModeCLI, delivery_mode_group
from .event_type import EventTypeCLI, event_type_group
from .registration_status import RegistrationStatusCLI, registration_status_group
from .venue import VenueCLI, venue_group


@click.group(
    name="cli",
    help="Mindset Backend CLI.",
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)
def top_cli() -> None:
    """Top-level CLI group.

    Use:
      • `flask cli --help` for an overview
      • `flask cli <group> --help` for a group
      • `flask cli <group> <command> --help` for details
    """

def register_cli(app: Flask) -> None:
    """
    Register all CLI groups and commands on the Flask app.

    After registration, you'll have:

      • `flask cli`
      • `flask cli registration-status --help`
      • `flask cli delivery-mode --help`
      • `flask cli event-type --help`
      • `flask cli venue --help`
      • `flask cli db --help`
      • `flask cli admin --help`

    This function is intended to be called from your app factory.
    """
    pairs: list[tuple[click.Group, type]] = [
        (registration_status_group, RegistrationStatusCLI),
        (delivery_mode_group, DeliveryModeCLI),
        (event_type_group, EventTypeCLI),
        (venue_group, VenueCLI),
        (db_group, DatabaseCLI),
        (admin_group, AdminCLI),
    ]
    for group, cls in pairs:
        attach_commands_from_class(group, cls)
        top_cli.add_command(group)
    app.cli.add_command(top_cli)
