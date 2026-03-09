"""``omniskill admin`` — administration dashboard (US-11, FR-056)."""

from __future__ import annotations

import typer

from omniskill.core.registry import Registry
from omniskill.core.platform import detect_platforms
from omniskill.core.config import is_initialized, get_install_records
from omniskill.utils.output import (
    console, print_error, is_json, json_envelope, print_json, make_table,
)
from omniskill import __version__


def admin_cmd() -> None:
    """Display an aggregate statistics dashboard."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    platforms = detect_platforms()
    detected = [p for p in platforms if p.detected]
    records = get_install_records()
    initialized = is_initialized()

    # Per-platform install counts
    platform_installs: dict[str, int] = {}
    for p in detected:
        platform_installs[p.id] = len(p.installed_skills)

    # Tag distribution
    tag_counts: dict[str, int] = {}
    for sk in reg.skills:
        reg.load_skill_manifest(sk)
        for tag in sk.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Priority distribution
    priority_counts: dict[str, int] = {}
    for sk in reg.skills:
        priority_counts[sk.priority] = priority_counts.get(sk.priority, 0) + 1

    data = {
        "framework": {
            "version": reg.version,
            "cli_version": __version__,
            "initialized": initialized,
        },
        "components": {
            "skills": len(reg.skills),
            "agents": len(reg.agents),
            "bundles": len(reg.bundles),
            "pipelines": len(reg.pipelines),
            "total": len(reg.skills) + len(reg.agents) + len(reg.bundles) + len(reg.pipelines),
        },
        "platforms": {
            "detected": len(detected),
            "installs_per_platform": platform_installs,
        },
        "install_records": len(records),
        "tags": tag_counts,
        "priorities": priority_counts,
    }

    if is_json():
        print_json(json_envelope(command="admin", data=data))
        return

    # ── Rich dashboard ──────────────────────────────────────────
    console.print()
    console.rule("[bold cyan]OMNISKILL Admin Dashboard[/bold cyan]")
    console.print()

    # Framework info
    console.print("[bold]Framework:[/bold]")
    console.print(f"  Version:     {reg.version}")
    console.print(f"  CLI Version: {__version__}")
    console.print(f"  Initialized: {'✅' if initialized else '❌'}")
    console.print()

    # Component counts
    console.print("[bold]Components:[/bold]")
    console.print(f"  📦 Skills:    {len(reg.skills)}")
    console.print(f"  🤖 Agents:    {len(reg.agents)}")
    console.print(f"  📚 Bundles:   {len(reg.bundles)}")
    console.print(f"  🔗 Pipelines: {len(reg.pipelines)}")
    console.print(f"  ── Total:     {data['components']['total']}")
    console.print()

    # Platform installs
    if detected:
        console.print("[bold]Platform Installations:[/bold]")
        for p in detected:
            console.print(f"  {p.name} ({p.id}): {len(p.installed_skills)} skills")
        console.print()

    # Priority breakdown
    if priority_counts:
        rows = [[p, str(c)] for p, c in sorted(priority_counts.items())]
        table = make_table(
            "Skills by Priority",
            [("Priority", "bold"), ("Count", "cyan")],
            rows,
        )
        console.print(table)
        console.print()

    # Top tags
    if tag_counts:
        top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:10]
        rows = [[t, str(c)] for t, c in top_tags]
        table = make_table(
            "Top Tags",
            [("Tag", "bold"), ("Count", "cyan")],
            rows,
        )
        console.print(table)
        console.print()

    # Bundle details
    if reg.bundles:
        rows = []
        for bnd in reg.bundles:
            rows.append([bnd.name, str(len(bnd.skills))])
        table = make_table(
            "Bundles",
            [("Bundle", "bold"), ("Skills", "cyan")],
            rows,
        )
        console.print(table)
        console.print()
