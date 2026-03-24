"""``archon config`` — get/set configuration (US-10, FR-052 through FR-055)."""

from __future__ import annotations

from typing import Optional

import typer

from archon.core.config import (
    load_config, get_config_value, set_config_value,
    VALID_KEY_NAMES, is_initialized,
)
from archon.utils.output import (
    console, print_error, print_success, print_info,
    is_json, json_envelope, print_json, make_table,
)
from archon.utils.paths import get_config_path


def config_cmd(
    key: Optional[str] = typer.Argument(None, help="Configuration key to get or set."),
    value: Optional[str] = typer.Argument(None, help="Value to set (omit to get current value)."),
) -> None:
    """Get or set Archon configuration values."""

    if not is_initialized():
        print_error("Archon is not initialized. Run [bold]archon init[/bold] first.")
        raise typer.Exit(1)

    # FR-052: No arguments → show all
    if key is None:
        cfg = load_config()
        if is_json():
            print_json(json_envelope(command="config", data=cfg))
            return
        console.print()
        console.rule("[bold cyan]Archon Configuration[/bold cyan]")
        console.print(f"  Config file: {get_config_path()}")
        console.print()
        rows = [[k, str(v) if v is not None else "[dim]not set[/dim]"] for k, v in cfg.items()]
        table = make_table(
            "Settings",
            [("Key", "bold"), ("Value", "")],
            rows,
        )
        console.print(table)
        console.print()
        return

    # FR-055: Validate key
    if key not in VALID_KEY_NAMES:
        print_error(f"Unknown config key: '{key}'")
        console.print(f"  Valid keys: {', '.join(VALID_KEY_NAMES)}")
        raise typer.Exit(1)

    # FR-053: One argument → get
    if value is None:
        try:
            val = get_config_value(key)
        except KeyError:
            print_error(f"Unknown key: {key}")
            raise typer.Exit(1)

        if is_json():
            print_json(json_envelope(command="config", data={key: val}))
            return

        display = str(val) if val is not None else "[dim]not set[/dim]"
        console.print(f"  {key} = {display}")
        return

    # FR-054: Two arguments → set
    try:
        path = set_config_value(key, value)
    except KeyError:
        print_error(f"Unknown key: {key}")
        raise typer.Exit(1)

    if is_json():
        print_json(json_envelope(command="config", data={key: value, "path": str(path)}))
        return

    print_success(f"Set [bold]{key}[/bold] = {value}")
    console.print(f"  Saved to {path}")
