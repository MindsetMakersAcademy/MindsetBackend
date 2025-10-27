"""Shared utilities and configuration for the app."""

from __future__ import annotations

import inspect

import rich_click as click

CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    max_content_width=100,
)

click.rich_click.MAX_WIDTH = 100
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.SHOW_METAVARS_COLUMN = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.APPEND_METAVARS_HELP = True


def attach_commands_from_class(group: click.Group, cls: type) -> None:
    """Attach all @click.command methods defined on ``cls`` to a Click group.

    A method is considered a Click command if Click attached ``__click_params__`` to it.

    Parameters
    ----------
    group:
        The Click group to add commands to.
    cls:
        A class that contains static methods decorated with @click.command.
    """
    for _, func in inspect.getmembers(cls, predicate=inspect.isfunction):
        if hasattr(func, "__click_params__"):
            group.add_command(func)
