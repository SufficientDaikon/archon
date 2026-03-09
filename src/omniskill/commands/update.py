"""``omniskill update`` — check for and apply updates (US-9, FR-049 through FR-051)."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
import yaml

from omniskill.core.registry import Registry
from omniskill.core.platform import detect_platforms
from omniskill.core.config import get_install_records
from omniskill.utils.output import (
    console, print_error, print_success, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json,
)
from omniskill.utils.paths import get_omniskill_home


def _parse_version(v: str) -> tuple[int, int, int]:
    try:
        parts = v.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return (0, 0, 0)


def _check_skill_updates(reg: Registry) -> list[dict]:
    """Compare installed skill versions against registry versions."""
    updates: list[dict] = []
    records = get_install_records()

    for record in records:
        if record.get("type") != "skill":
            continue
        skill = reg.find_skill(record["name"])
        if not skill:
            continue
        reg.load_skill_manifest(skill)
        installed_ver = record.get("version", "0.0.0")
        registry_ver = skill.version
        if _parse_version(installed_ver) < _parse_version(registry_ver):
            updates.append({
                "name": skill.name,
                "platform": record.get("platform", "unknown"),
                "installed_version": installed_ver,
                "available_version": registry_ver,
            })
    return updates


def update_cmd(
    check: bool = typer.Option(False, "--check", help="Check for updates without applying."),
) -> None:
    """Check for or apply OMNISKILL updates."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    from omniskill import __version__
    current_ver = __version__
    registry_ver = reg.version

    updates = _check_skill_updates(reg)

    if check or True:  # For now, always check mode (actual update requires network)
        data = {
            "current_version": current_ver,
            "registry_version": registry_ver,
            "skill_updates": updates,
            "up_to_date": len(updates) == 0 and current_ver == registry_ver,
        }

        if is_json():
            print_json(json_envelope(command="update", data=data))
            return

        console.print()
        console.rule("[bold cyan]OMNISKILL Update Check[/bold cyan]")
        console.print()
        console.print(f"  CLI Version:      {current_ver}")
        console.print(f"  Registry Version: {registry_ver}")
        console.print()

        if not updates:
            print_success("All installed skills are up to date!")
        else:
            console.print(f"  [bold]{len(updates)} update(s) available:[/bold]")
            for u in updates:
                console.print(
                    f"    • {u['name']} on {u['platform']}: "
                    f"{u['installed_version']} → {u['available_version']}"
                )
            console.print()
            console.print("  To apply updates, reinstall with:")
            console.print("    omniskill install --all --force")

        console.print()
