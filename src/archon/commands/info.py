"""``archon info`` — detailed component info (US-4, FR-033)."""

from __future__ import annotations

import typer

from archon.core.registry import Registry
from archon.core.platform import detect_platforms
from archon.core.config import get_install_records
from archon.utils.output import (
    console, print_error, is_json, json_envelope, print_json,
)


def info_cmd(
    name: str = typer.Argument(..., help="Component name (skill, agent, bundle, or pipeline)."),
) -> None:
    """Show detailed information about any Archon component."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    found = reg.find_component(name)
    if not found:
        similar = reg.similar_names(name)
        msg = f"Component '{name}' not found."
        if similar:
            msg += f" Did you mean: {', '.join(similar)}?"
        print_error(msg)
        raise typer.Exit(1)

    comp_type, comp = found

    # Load detailed manifest
    if comp_type == "skill":
        manifest = reg.load_skill_manifest(comp)
    elif comp_type == "agent":
        manifest = reg.load_agent_manifest(comp)
    elif comp_type == "bundle":
        manifest = reg.load_bundle_manifest(comp)
    elif comp_type == "pipeline":
        manifest = reg.load_pipeline_manifest(comp)
    elif comp_type == "synapse":
        manifest = reg.load_synapse_manifest(comp)
    else:
        manifest = {}

    # Installation status per platform
    platforms = detect_platforms()
    install_status: dict[str, str] = {}
    records = get_install_records(name)
    record_platforms = {r["platform"] for r in records}
    for p in platforms:
        if p.detected:
            if p.id in record_platforms:
                install_status[p.id] = "installed"
            elif p.skills_target and (p.skills_target / name).exists():
                install_status[p.id] = "installed (untracked)"
            else:
                install_status[p.id] = "not installed"

    data = {
        "name": comp.name,
        "type": comp_type,
        "version": getattr(comp, "version", ""),
        "description": getattr(comp, "description", ""),
        "path": getattr(comp, "path", ""),
        "manifest": manifest,
        "install_status": install_status,
    }

    # Add type-specific fields
    if comp_type == "skill":
        data["author"] = getattr(comp, "author", "")
        data["tags"] = getattr(comp, "tags", [])
        data["priority"] = getattr(comp, "priority", "")
        data["platforms"] = getattr(comp, "platforms", [])
        data["triggers"] = getattr(comp, "triggers", {})
    elif comp_type == "agent":
        data["role"] = getattr(comp, "role", "")
    elif comp_type == "bundle":
        data["skills"] = getattr(comp, "skills", [])
    elif comp_type == "pipeline":
        data["trigger"] = getattr(comp, "trigger", "")
        data["steps"] = getattr(comp, "steps", [])
    elif comp_type == "synapse":
        data["synapse_type"] = getattr(comp, "synapse_type", "")
        data["tags"] = getattr(comp, "tags", [])
        data["firing_phases"] = getattr(comp, "firing_phases", [])
        data["author"] = getattr(comp, "author", "")

    if is_json():
        print_json(json_envelope(command="info", data=data))
        return

    # ── Rich output ─────────────────────────────────────────────
    console.print()
    console.rule(f"[bold cyan]{comp.name}[/bold cyan]")
    console.print()
    console.print(f"  [bold]Type:[/bold]        {comp_type}")
    console.print(f"  [bold]Version:[/bold]     {data['version']}")
    console.print(f"  [bold]Path:[/bold]        {data['path']}")

    if data.get("description"):
        console.print(f"  [bold]Description:[/bold] {data['description']}")
    if data.get("author"):
        console.print(f"  [bold]Author:[/bold]      {data['author']}")
    if data.get("priority"):
        console.print(f"  [bold]Priority:[/bold]    {data['priority']}")
    if data.get("tags"):
        console.print(f"  [bold]Tags:[/bold]        {', '.join(data['tags'])}")
    if data.get("platforms"):
        console.print(f"  [bold]Platforms:[/bold]   {', '.join(data['platforms'])}")
    if data.get("role"):
        console.print(f"  [bold]Role:[/bold]        {data['role']}")

    # Triggers
    triggers = data.get("triggers", {})
    if triggers:
        keywords = triggers.get("keywords", [])
        if keywords:
            console.print(f"  [bold]Triggers:[/bold]    {', '.join(keywords[:5])}")

    # Synapse-specific fields
    if data.get("synapse_type"):
        console.print(f"  [bold]Synapse Type:[/bold] {data['synapse_type']}")
    if data.get("firing_phases"):
        console.print(f"\n  [bold]Firing Phases ({len(data['firing_phases'])}):[/bold]")
        for phase in data["firing_phases"]:
            phase_name = phase.get("name", "?")
            timing = phase.get("timing", "?")
            desc = phase.get("description", "")
            console.print(f"    🧠 {phase_name} ({timing}): {desc}")

    # Bundle skills
    if data.get("skills"):
        console.print(f"\n  [bold]Skills ({len(data['skills'])}):[/bold]")
        for s in data["skills"]:
            console.print(f"    • {s}")

    # Pipeline steps
    if data.get("steps"):
        console.print(f"\n  [bold]Steps ({len(data['steps'])}):[/bold]")
        for i, step in enumerate(data["steps"], 1):
            step_name = step.get("name", f"step-{i}")
            agent = step.get("agent", "?")
            console.print(f"    {i}. {step_name} → {agent}")

    # Install status
    if install_status:
        console.print(f"\n  [bold]Installation Status:[/bold]")
        for pid, status in install_status.items():
            icon = "✅" if "installed" in status else "❌"
            console.print(f"    {icon} {pid}: {status}")

    console.print()
