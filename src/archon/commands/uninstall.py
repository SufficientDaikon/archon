"""``archon uninstall`` — remove components (US-7, FR-019 through FR-022)."""

from __future__ import annotations

from typing import Optional

import typer

from archon.core.registry import Registry
from archon.core.installer import uninstall_skill_from_platform, resolve_target_platforms
from archon.core.config import get_install_records
from archon.utils.output import (
    console, print_success, print_error, print_warning, print_info,
    is_json, json_envelope, print_json,
)


def uninstall_cmd(
    component: str = typer.Argument(..., help="Name of skill, agent, or bundle to uninstall."),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Target a specific platform."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompts."),
) -> None:
    """Remove installed components from platform(s)."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    targets = resolve_target_platforms(reg, platform)
    if not targets:
        print_error("No target platforms found.")
        raise typer.Exit(1)

    # Is it a bundle?
    bnd = reg.find_bundle(component)
    if bnd:
        skills_to_remove = bnd.skills
        if not force:
            if not is_json():
                console.print(
                    f"\n[bold]Bundle '{bnd.name}' contains {len(skills_to_remove)} skill(s):[/bold]"
                )
                for s in skills_to_remove:
                    console.print(f"  • {s}")
                confirm = typer.confirm("Remove all these skills?", default=False)
                if not confirm:
                    print_info("Aborted.")
                    raise typer.Exit(0)
    else:
        skills_to_remove = [component]

    results: list[dict] = []
    for skill_name in skills_to_remove:
        for plat in targets:
            removed = uninstall_skill_from_platform(skill_name, plat)
            results.append({"skill": skill_name, "platform": plat.id, "removed": removed})
            if removed:
                print_success(f"Removed [bold]{skill_name}[/bold] from {plat.name}")

    removed_count = sum(1 for r in results if r["removed"])
    if removed_count == 0:
        # FR-020: idempotent
        if is_json():
            print_json(json_envelope(
                command="uninstall",
                data={"removed": 0, "message": f"'{component}' is not installed."},
            ))
        else:
            print_info(f"'{component}' is not installed on any target platform.")
        return

    if is_json():
        print_json(json_envelope(
            command="uninstall",
            data={"removed": removed_count, "results": results},
        ))
    else:
        console.print(f"\n  Removed {removed_count} component(s).")
