"""This cli is intended for making complex migrations a little bit easier to interact for later."""
from __future__ import annotations

import click
from flask import Flask
from flask.cli import with_appcontext

from .db import db


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    db.create_all()
    click.echo("Initialized the database.")


def register_cli(app: Flask) -> None:
    app.cli.add_command(init_db_command)