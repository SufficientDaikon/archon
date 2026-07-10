"""``archon info`` — component info, or an environment report with no args.

``archon info <name>`` keeps its original behavior (detailed component info).
``archon info`` with no argument prints a gcloud-info-style environment
report: version, paths, resolved properties with sources, hook registrations,
state and log locations.
"""

from __future__ import annotations

import json as _json
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer

from archon import __version__
from archon.core.config import get_install_records
from archon.core.platform import detect_platforms
from archon.core.registry import Registry
from archon.utils.output import (
    console,
    is_json,
    json_envelope,
    make_table,
    print_error,
    print_json,
)
from archon.utils.paths import get_archon_home, get_archon_root


def info_cmd(
    name: str = typer.Argument(
        None, help="Component name (skill, agent, bundle, or pipeline). Omit for environment info."
    ),
) -> None:
    """Show component details, or the Archon environment report with no args."""

    if name is None:
        _environment_report()
        return

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from None

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
        console.print("\n  [bold]Installation Status:[/bold]")
        for pid, status in install_status.items():
            icon = "✅" if "installed" in status else "❌"
            console.print(f"    {icon} {pid}: {status}")

    console.print()


def _environment_report() -> None:
    """gcloud-info-style environment snapshot: paths, properties, hooks, logs."""
    from archon.core.hooks_bridge import HooksBridgeError, load_shared

    root = Path(get_archon_root())
    home = get_archon_home()

    data: dict = {
        "version": __version__,
        "python": sys.version.split()[0],
        "paths": {
            "archon_root": str(root),
            "archon_home": str(home),
            "logs_dir": str(home / "logs"),
            "projects_dir": str(home / "projects"),
        },
    }

    # Properties with sources (via the hook-shared registry)
    properties: dict = {}
    try:
        props = load_shared("config")
        properties = {
            key: {"value": value, "source": source}
            for key, (value, source) in props.load_all(cwd=str(Path.cwd())).items()
        }
        data["paths"]["user_config"] = str(props.user_config_path())
    except HooksBridgeError as exc:
        data["properties_error"] = str(exc)
    data["properties"] = properties

    # Active project state
    try:
        state_mod = load_shared("state")
        slug = state_mod.project_slug(str(Path.cwd()))
        data["project"] = {
            "slug": slug,
            "state_file": str(home / "projects" / slug / "state.json"),
            "state_exists": (home / "projects" / slug / "state.json").exists(),
        }
    except HooksBridgeError:
        pass

    # Hook registrations from .claude/settings.json, with script-exists checks
    hooks: list[dict] = []
    settings_path = root / ".claude" / "settings.json"
    if settings_path.is_file():
        try:
            settings = _json.loads(settings_path.read_text(encoding="utf-8"))
            for event, registrations in settings.get("hooks", {}).items():
                for registration in registrations:
                    for hook in registration.get("hooks", []):
                        command = hook.get("command", "")
                        script = command.split("/")[-1].rstrip('"') if command else ""
                        script_path = root / "hooks" / "claude" / script
                        hooks.append(
                            {
                                "event": event,
                                "matcher": registration.get("matcher", ""),
                                "script": script,
                                "exists": script_path.is_file(),
                            }
                        )
        except (_json.JSONDecodeError, OSError):
            pass
    data["hooks"] = hooks

    # Today's hook log volume
    today = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    log_file = home / "logs" / f"hooks-{today}.jsonl"
    data["log_today"] = {
        "file": str(log_file),
        "records": sum(1 for _ in log_file.open(encoding="utf-8")) if log_file.is_file() else 0,
    }

    # Registry counts
    try:
        reg = Registry()
        reg.load()
        data["registry"] = {
            "skills": len(reg.skills),
            "agents": len(reg.agents),
            "bundles": len(reg.bundles),
            "pipelines": len(reg.pipelines),
            "synapses": len(reg.synapses),
        }
    except FileNotFoundError:
        data["registry"] = {}

    if is_json():
        print_json(json_envelope(command="info", data=data))
        return

    console.print()
    console.rule("[bold cyan]Archon Environment[/bold cyan]")
    console.print(f"  Version: {data['version']}    Python: {data['python']}")
    console.print()
    for label, value in data["paths"].items():
        console.print(f"  {label}: {value}")
    if data.get("project"):
        proj = data["project"]
        marker = "" if proj["state_exists"] else " [dim](no state yet)[/dim]"
        console.print(f"  project state: {proj['state_file']}{marker}")
    console.print(
        f"  log today: {data['log_today']['file']} ({data['log_today']['records']} records)"
    )
    console.print()

    if properties:
        rows = [[k, str(v["value"]), v["source"]] for k, v in properties.items()]
        console.print(
            make_table(
                "Properties (resolved)",
                [("Property", "bold"), ("Value", ""), ("Source", "dim")],
                rows,
            )
        )
        console.print()

    if hooks:
        rows = [
            [h["event"], h["matcher"] or "—", h["script"], "✅" if h["exists"] else "❌ missing"]
            for h in hooks
        ]
        console.print(
            make_table(
                "Hook registrations (.claude/settings.json)",
                [("Event", "bold"), ("Matcher", "dim"), ("Script", ""), ("Status", "")],
                rows,
            )
        )
        console.print()

    if data.get("registry"):
        counts = data["registry"]
        console.print(
            "  Registry: " + ", ".join(f"{count} {kind}" for kind, count in counts.items())
        )
    console.print()
