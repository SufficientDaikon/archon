"""``archon config`` — properties and CLI preferences.

Two key families share this surface:

- **Properties** (``section/name``, e.g. ``gate/max_blocks``) — the hook-layer
  knobs defined in ``hooks/claude/shared/config.py``. Resolution order is
  env var (``ARCHON_SECTION_NAME``) > project ``.archon/config`` > user
  ``<ARCHON_HOME>/config`` > default, and ``config list`` shows each value
  with its source (gcloud-style).
- **Legacy CLI preferences** (flat keys, e.g. ``default_platform``) — stored
  in ``<ARCHON_HOME>/config.yaml`` via :mod:`archon.core.config`, unchanged.
"""

from __future__ import annotations

import typer

from archon.core.config import (
    VALID_KEY_NAMES,
    get_config_value,
    load_config,
    set_config_value,
)
from archon.core.hooks_bridge import HooksBridgeError, load_shared
from archon.utils.output import (
    console,
    is_json,
    json_envelope,
    make_table,
    print_error,
    print_json,
    print_success,
)
from archon.utils.paths import get_config_path

config_app = typer.Typer(
    help="Get and set Archon configuration (properties and CLI preferences).",
    invoke_without_command=True,
)


def _properties():
    """The hook-shared properties module, or None with a warning."""
    try:
        return load_shared("config")
    except HooksBridgeError as exc:
        console.print(f"[yellow]⚠[/yellow] {exc}")
        return None


@config_app.callback()
def config_main(ctx: typer.Context) -> None:
    """Bare ``archon config`` lists everything (legacy behavior preserved)."""
    if ctx.invoked_subcommand is None:
        list_cmd()


@config_app.command("list")
def list_cmd() -> None:
    """List all properties (with sources) and CLI preferences."""
    props = _properties()
    prop_rows = []
    if props is not None:
        for key, (value, source) in props.load_all(cwd=None).items():
            prop_rows.append([key, str(value), source, props.PROPERTIES[key].help])

    cli_cfg = load_config()

    if is_json():
        print_json(
            json_envelope(
                command="config",
                data={
                    "properties": {
                        key: {"value": value, "source": source}
                        for key, (value, source) in (
                            props.load_all(cwd=None).items() if props else []
                        )
                    },
                    "cli": cli_cfg,
                },
            )
        )
        return

    console.print()
    console.rule("[bold cyan]Archon Configuration[/bold cyan]")
    if props is not None:
        console.print(f"  User file: {props.user_config_path()}")
        console.print(
            "  Project file: .archon/config (per repo) — env vars ARCHON_SECTION_NAME override"
        )
        console.print()
        console.print(
            make_table(
                "Properties",
                [("Property", "bold"), ("Value", ""), ("Source", "dim"), ("Help", "dim")],
                prop_rows,
            )
        )
    console.print()
    console.print(f"  CLI preferences file: {get_config_path()}")
    cli_rows = [[k, str(v) if v is not None else "[dim]not set[/dim]"] for k, v in cli_cfg.items()]
    console.print(make_table("CLI Preferences", [("Key", "bold"), ("Value", "")], cli_rows))
    console.print()


@config_app.command("get")
def get_cmd(key: str = typer.Argument(..., help="Property (section/name) or CLI key.")) -> None:
    """Get one configuration value (properties show their source)."""
    if "/" in key:
        props = _properties()
        if props is None:
            raise typer.Exit(1)
        try:
            value, source = props.resolve_property(key, cwd=None)
        except KeyError:
            print_error(f"Unknown property: '{key}'")
            console.print(f"  Known: {', '.join(sorted(props.PROPERTIES))}")
            raise typer.Exit(1) from None
        if is_json():
            print_json(
                json_envelope(command="config", data={key: {"value": value, "source": source}})
            )
            return
        console.print(f"  {key} = {value}  [dim]({source})[/dim]")
        return

    if key not in VALID_KEY_NAMES:
        print_error(f"Unknown config key: '{key}'")
        console.print(f"  Valid CLI keys: {', '.join(VALID_KEY_NAMES)}")
        raise typer.Exit(1)
    val = get_config_value(key)
    if is_json():
        print_json(json_envelope(command="config", data={key: val}))
        return
    display = str(val) if val is not None else "[dim]not set[/dim]"
    console.print(f"  {key} = {display}")


@config_app.command("set")
def set_cmd(
    key: str = typer.Argument(..., help="Property (section/name) or CLI key."),
    value: str = typer.Argument(..., help="Value to set."),
    project: bool = typer.Option(
        False, "--project", help="Write to the project .archon/config instead of the user file."
    ),
) -> None:
    """Set a configuration value."""
    if "/" in key:
        props = _properties()
        if props is None:
            raise typer.Exit(1)
        try:
            path = props.set_property(key, value, project=project)
        except KeyError:
            print_error(f"Unknown property: '{key}'")
            raise typer.Exit(1) from None
        except ValueError as exc:
            print_error(str(exc))
            raise typer.Exit(1) from None
    else:
        if project:
            print_error("--project applies only to section/name properties.")
            raise typer.Exit(1)
        try:
            path = set_config_value(key, value)
        except KeyError:
            print_error(f"Unknown key: {key}")
            raise typer.Exit(1) from None

    if is_json():
        print_json(json_envelope(command="config", data={key: value, "path": str(path)}))
        return
    print_success(f"Set [bold]{key}[/bold] = {value}")
    console.print(f"  Saved to {path}")


@config_app.command("unset")
def unset_cmd(
    key: str = typer.Argument(..., help="Property (section/name) to remove."),
    project: bool = typer.Option(False, "--project", help="Remove from the project file."),
) -> None:
    """Remove a property from the user or project config file."""
    if "/" not in key:
        print_error("unset applies to section/name properties; CLI keys can be re-set instead.")
        raise typer.Exit(1)
    props = _properties()
    if props is None:
        raise typer.Exit(1)
    try:
        path = props.unset_property(key, project=project)
    except KeyError:
        print_error(f"Unknown property: '{key}'")
        raise typer.Exit(1) from None
    if path is None:
        console.print(f"  {key} was not set in the {'project' if project else 'user'} file.")
        return
    if is_json():
        print_json(json_envelope(command="config", data={key: None, "path": str(path)}))
        return
    print_success(f"Unset [bold]{key}[/bold]")
    console.print(f"  Updated {path}")
