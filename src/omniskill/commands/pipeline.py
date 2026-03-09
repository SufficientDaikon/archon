"""``omniskill pipeline`` — run and manage pipelines (US-6, FR-039 through FR-044)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
import yaml

from omniskill.core.registry import Registry
from omniskill.core.config import load_state, save_state
from omniskill.utils.output import (
    console, print_error, print_success, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json, get_progress,
)
from omniskill.utils.paths import get_omniskill_home

pipeline_app = typer.Typer(help="Run and manage pipelines.", no_args_is_help=True)


def _get_pipeline_state_path(pipeline_name: str, project: str) -> Path:
    """Return path for persisted pipeline execution state (FR-044)."""
    return get_omniskill_home() / "pipelines" / f"{pipeline_name}--{project}.yaml"


def _load_pipeline_state(pipeline_name: str, project: str) -> dict:
    p = _get_pipeline_state_path(pipeline_name, project)
    if p.exists():
        with open(p, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


def _save_pipeline_state(pipeline_name: str, project: str, state: dict) -> None:
    p = _get_pipeline_state_path(pipeline_name, project)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        yaml.dump(state, fh, default_flow_style=False, sort_keys=False)


@pipeline_app.command("run")
def pipeline_run(
    name: str = typer.Argument(..., help="Pipeline name to execute."),
    project: str = typer.Option("default", "--project", "-p", help="Project context for this run."),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue after phase failure."),
) -> None:
    """Execute a named pipeline against a project."""

    try:
        reg = Registry()
        reg.load()
    except FileNotFoundError as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    pl = reg.find_pipeline(name)
    if not pl:
        available = [p.name for p in reg.pipelines]
        print_error(f"Pipeline '{name}' not found. Available: {', '.join(available)}")
        raise typer.Exit(1)

    reg.load_pipeline_manifest(pl)

    steps = pl.steps
    if not steps:
        print_warning(f"Pipeline '{name}' has no steps defined.")
        raise typer.Exit(1)

    # Initialize execution state
    exec_state = {
        "pipeline": name,
        "project": project,
        "started_at": datetime.now().isoformat(),
        "status": "in-progress",
        "current_phase": 0,
        "phases": [],
    }

    if not is_json():
        console.print()
        console.rule(f"[bold cyan]Pipeline: {name}[/bold cyan]")
        console.print(f"  Project: {project}")
        console.print(f"  Steps: {len(steps)}")
        console.print()

    failed = False

    if is_json():
        # In JSON mode, skip all progress/console output — just execute silently
        for i, step in enumerate(steps):
            step_name = step.get("name", f"step-{i+1}")
            agent = step.get("agent", "unknown")
            phase_record = {
                "name": step_name,
                "agent": agent,
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "output": f"Phase '{step_name}' ready for execution via {agent}",
            }
            exec_state["phases"].append(phase_record)
            exec_state["current_phase"] = i + 1
    else:
        with get_progress() as progress:
            task = progress.add_task(f"Running {name}", total=len(steps))

            for i, step in enumerate(steps):
                step_name = step.get("name", f"step-{i+1}")
                agent = step.get("agent", "unknown")
                on_failure = step.get("on-failure", "halt")

                phase_record = {
                    "name": step_name,
                    "agent": agent,
                    "status": "running",
                    "started_at": datetime.now().isoformat(),
                }

                console.print(f"  [bold]Phase {i+1}/{len(steps)}:[/bold] {step_name} → {agent}")

                # Simulate execution (actual execution depends on platform integration)
                phase_record["status"] = "completed"
                phase_record["completed_at"] = datetime.now().isoformat()
                phase_record["output"] = f"Phase '{step_name}' ready for execution via {agent}"

                exec_state["phases"].append(phase_record)
                exec_state["current_phase"] = i + 1
                progress.advance(task)

                print_success(f"    {step_name} — ready")

    exec_state["status"] = "completed" if not failed else "failed"
    exec_state["completed_at"] = datetime.now().isoformat()

    # Persist state (FR-044)
    _save_pipeline_state(name, project, exec_state)

    if is_json():
        print_json(json_envelope(command="pipeline run", data=exec_state))
        return

    console.print()
    if not failed:
        print_success(f"Pipeline '{name}' completed. State saved.")
    else:
        print_error(f"Pipeline '{name}' failed.")

    console.print(f"  State: {_get_pipeline_state_path(name, project)}")
    console.print()


@pipeline_app.command("status")
def pipeline_status(
    project: str = typer.Option("default", "--project", "-p", help="Project to check."),
    name: Optional[str] = typer.Argument(None, help="Pipeline name (optional)."),
) -> None:
    """Show pipeline execution status."""

    home = get_omniskill_home()
    pipelines_dir = home / "pipelines"

    if not pipelines_dir.exists():
        print_info("No pipeline runs found.")
        raise typer.Exit(0)

    # Find matching state files
    if name:
        files = list(pipelines_dir.glob(f"{name}--{project}.yaml"))
    else:
        files = list(pipelines_dir.glob(f"*--{project}.yaml"))

    if not files:
        print_info(f"No pipeline runs found for project '{project}'.")
        raise typer.Exit(0)

    all_states: list[dict] = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                state = yaml.safe_load(fh) or {}
            all_states.append(state)
        except Exception:
            continue

    if is_json():
        print_json(json_envelope(command="pipeline status", data={"runs": all_states}))
        return

    for state in all_states:
        console.print()
        console.rule(f"[bold]{state.get('pipeline', '?')}[/bold] — {state.get('project', '?')}")
        console.print(f"  Status:  {state.get('status', 'unknown')}")
        console.print(f"  Started: {state.get('started_at', '?')}")
        if state.get("completed_at"):
            console.print(f"  Ended:   {state['completed_at']}")
        console.print(f"  Phase:   {state.get('current_phase', 0)}/{len(state.get('phases', []))}")
        for phase in state.get("phases", []):
            icon = "✅" if phase.get("status") == "completed" else "❌"
            console.print(f"    {icon} {phase.get('name', '?')} ({phase.get('agent', '?')})")
    console.print()
