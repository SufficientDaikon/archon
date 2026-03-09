"""``omniskill list`` — list components (US-4, FR-028 through FR-030)."""

from __future__ import annotations

from typing import Optional

import typer

from omniskill.core.registry import Registry
from omniskill.utils.output import (
    console, print_error, is_json, json_envelope, print_json, make_table,
)


COMPONENT_TYPES = ["skills", "agents", "bundles", "pipelines"]


def list_cmd(
    component_type: Optional[str] = typer.Argument(
        None,
        help="Component type to list: skills, agents, bundles, pipelines.",
    ),
) -> None:
    """List available skills, agents, bundles, or pipelines."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    # FR-030: No type → show summary
    if component_type is None:
        _show_summary(reg)
        return

    ct = component_type.lower().rstrip("s") + "s"  # normalize
    if ct not in COMPONENT_TYPES:
        print_error(f"Unknown type '{component_type}'. Choose from: {', '.join(COMPONENT_TYPES)}")
        raise typer.Exit(1)

    if ct == "skills":
        _list_skills(reg)
    elif ct == "agents":
        _list_agents(reg)
    elif ct == "bundles":
        _list_bundles(reg)
    elif ct == "pipelines":
        _list_pipelines(reg)


# ── Summary ─────────────────────────────────────────────────────

def _show_summary(reg: Registry) -> None:
    data = {
        "skills": len(reg.skills),
        "agents": len(reg.agents),
        "bundles": len(reg.bundles),
        "pipelines": len(reg.pipelines),
    }

    if is_json():
        print_json(json_envelope(command="list", data=data))
        return

    console.print()
    console.rule(f"[bold cyan]OMNISKILL Registry — v{reg.version}[/bold cyan]")
    console.print()
    console.print(f"  📦 Skills:    [bold cyan]{data['skills']}[/bold cyan]")
    console.print(f"  🤖 Agents:    [bold cyan]{data['agents']}[/bold cyan]")
    console.print(f"  📚 Bundles:   [bold cyan]{data['bundles']}[/bold cyan]")
    console.print(f"  🔗 Pipelines: [bold cyan]{data['pipelines']}[/bold cyan]")
    console.print()
    console.print("[muted]Use:[/muted]")
    console.print("  omniskill list skills      — list all skills")
    console.print("  omniskill list agents      — list all agents")
    console.print("  omniskill list bundles     — list all bundles")
    console.print("  omniskill list pipelines   — list all pipelines")
    console.print()


# ── Skills ──────────────────────────────────────────────────────

def _list_skills(reg: Registry) -> None:
    rows_data = []
    for sk in reg.skills:
        reg.load_skill_manifest(sk)
        rows_data.append({
            "name": sk.name,
            "version": sk.version,
            "priority": sk.priority,
            "tags": ", ".join(sk.tags[:3]) if sk.tags else "",
            "description": (sk.description[:60] + "…") if len(sk.description) > 60 else sk.description,
        })

    if is_json():
        print_json(json_envelope(command="list", data={"type": "skills", "count": len(rows_data), "items": rows_data}))
        return

    rows = [[r["name"], r["version"], r["priority"], r["tags"], r["description"]] for r in rows_data]
    table = make_table(
        f"Skills ({len(rows)})",
        [("Name", "bold"), ("Version", "cyan"), ("Priority", ""), ("Tags", "dim"), ("Description", "")],
        rows,
    )
    console.print()
    console.print(table)
    console.print()


# ── Agents ──────────────────────────────────────────────────────

def _list_agents(reg: Registry) -> None:
    rows_data = []
    for ag in reg.agents:
        reg.load_agent_manifest(ag)
        rows_data.append({
            "name": ag.name,
            "version": ag.version,
            "role": ag.role or "",
            "description": (ag.description[:60] + "…") if len(ag.description) > 60 else ag.description,
        })

    if is_json():
        print_json(json_envelope(command="list", data={"type": "agents", "count": len(rows_data), "items": rows_data}))
        return

    rows = [[r["name"], r["version"], r["role"], r["description"]] for r in rows_data]
    table = make_table(
        f"Agents ({len(rows)})",
        [("Name", "bold"), ("Version", "cyan"), ("Role", ""), ("Description", "")],
        rows,
    )
    console.print()
    console.print(table)
    console.print()


# ── Bundles ─────────────────────────────────────────────────────

def _list_bundles(reg: Registry) -> None:
    rows_data = []
    for bnd in reg.bundles:
        reg.load_bundle_manifest(bnd)
        rows_data.append({
            "name": bnd.name,
            "version": bnd.version,
            "skills_count": len(bnd.skills),
            "skills": bnd.skills,
            "description": (bnd.description[:60] + "…") if len(bnd.description) > 60 else bnd.description,
        })

    if is_json():
        print_json(json_envelope(command="list", data={"type": "bundles", "count": len(rows_data), "items": rows_data}))
        return

    rows = [[r["name"], r["version"], str(r["skills_count"]), r["description"]] for r in rows_data]
    table = make_table(
        f"Bundles ({len(rows)})",
        [("Name", "bold"), ("Version", "cyan"), ("Skills", ""), ("Description", "")],
        rows,
    )
    console.print()
    console.print(table)
    console.print()


# ── Pipelines ───────────────────────────────────────────────────

def _list_pipelines(reg: Registry) -> None:
    rows_data = []
    for pl in reg.pipelines:
        reg.load_pipeline_manifest(pl)
        rows_data.append({
            "name": pl.name,
            "version": pl.version,
            "trigger": pl.trigger,
            "steps": len(pl.steps),
            "description": (pl.description[:60] + "…") if len(pl.description) > 60 else pl.description,
        })

    if is_json():
        print_json(json_envelope(command="list", data={"type": "pipelines", "count": len(rows_data), "items": rows_data}))
        return

    rows = [[r["name"], r["version"], str(r["steps"]), r["trigger"], r["description"]] for r in rows_data]
    table = make_table(
        f"Pipelines ({len(rows)})",
        [("Name", "bold"), ("Version", "cyan"), ("Steps", ""), ("Trigger", "dim"), ("Description", "")],
        rows,
    )
    console.print()
    console.print(table)
    console.print()
