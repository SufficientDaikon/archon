"""Archon CLI — main Typer application.

Entry point for ``archon`` command.  Registers all subcommands and
global flags (``--json``, ``--quiet``, ``--verbose``, ``--version``).
"""

from __future__ import annotations

from typing import Optional

import typer

from archon import __version__, __app_name__
from archon.utils.output import set_output_flags, console

# ── Typer app ───────────────────────────────────────────────────

app = typer.Typer(
    name=__app_name__,
    help="Archon — The Virtuoso Engine for AI Agents CLI",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"archon {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error output."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Increase output detail."),
) -> None:
    """Archon — manage skills, agents, bundles & pipelines across AI platforms."""
    set_output_flags(json_flag=json_output, quiet=quiet, verbose=verbose)


# ── Register subcommands ────────────────────────────────────────

from archon.commands.init_cmd import init_cmd          # noqa: E402
from archon.commands.install import install_cmd        # noqa: E402
from archon.commands.uninstall import uninstall_cmd    # noqa: E402
from archon.commands.doctor import doctor_cmd          # noqa: E402
from archon.commands.validate import validate_cmd      # noqa: E402
from archon.commands.list_cmd import list_cmd          # noqa: E402
from archon.commands.search import search_cmd          # noqa: E402
from archon.commands.info import info_cmd              # noqa: E402
from archon.commands.pipeline import pipeline_app      # noqa: E402
from archon.commands.update import update_cmd          # noqa: E402
from archon.commands.migrate import migrate_cmd        # noqa: E402
from archon.commands.admin import admin_cmd            # noqa: E402
from archon.commands.config import config_cmd          # noqa: E402
from archon.commands.generate import generate_app      # noqa: E402
from archon.commands.catalog import catalog_app        # noqa: E402
from archon.commands.cards import cards_cmd             # noqa: E402

app.command("init", help="Initialize Archon — detect platforms, create config.")(init_cmd)
app.command("install", help="Install skills, bundles, or agents to platform(s).")(install_cmd)
app.command("uninstall", help="Remove installed components from platform(s).")(uninstall_cmd)
app.command("doctor", help="Health diagnostics with score and platform status.")(doctor_cmd)
app.command("validate", help="Validate manifests and skill files.")(validate_cmd)
app.command("list", help="List available skills, agents, bundles, or pipelines.")(list_cmd)
app.command("search", help="Search components by keyword, tag, or description.")(search_cmd)
app.command("info", help="Show detailed information about a component.")(info_cmd)
app.add_typer(pipeline_app, name="pipeline", help="Run and manage pipelines.")
app.command("update", help="Check for or apply Archon updates.")(update_cmd)
app.command("migrate", help="Convert legacy skill formats to Archon format.")(migrate_cmd)
app.command("admin", help="Administration dashboard with aggregate statistics.")(admin_cmd)
app.command("config", help="Get or set configuration values.")(config_cmd)
app.add_typer(generate_app, name="generate", help="Generate framework artifacts.")
app.add_typer(catalog_app, name="catalog", help="Browse and manage MCP server integrations.")
app.command("cards", help="View and manage agent cards.")(cards_cmd)
