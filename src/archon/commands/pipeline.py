"""``archon pipeline`` — run and manage pipelines (US-6, FR-039 through FR-044)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from archon.core.pipeline_engine import PipelineExecutor, PipelineStatus, StepStatus
from archon.core.pipeline_state import PipelineState
from archon.utils.output import (
    console, print_error, print_success, print_warning, print_info,
    is_json, json_envelope, print_json,
)

pipeline_app = typer.Typer(help="Run and manage pipelines.", no_args_is_help=True)

ARCHON_ROOT = Path(__file__).parent.parent.parent.parent
HOOKS_DIR = ARCHON_ROOT / "hooks"
from archon.utils.paths import get_archon_home
STATE_DIR = get_archon_home() / "pipeline-states"
PIPELINES_DIR = ARCHON_ROOT / "pipelines"


def _create_executor() -> PipelineExecutor:
    """Create a PipelineExecutor with standard paths."""
    return PipelineExecutor(hooks_dir=HOOKS_DIR, state_dir=STATE_DIR)


_STATUS_ICONS = {
    "completed": "✅",
    "running": "🔄",
    "executing": "🔄",
    "pending": "⏳",
    "failed": "❌",
    "cancelled": "🚫",
    "skipped": "⏭️",
    "paused": "⏸️",
    "looping": "🔁",
    "validating": "🔍",
}


def _icon(status: str) -> str:
    return _STATUS_ICONS.get(status, "❓")


def _print_state_detail(state: PipelineState) -> None:
    """Print detailed status output for a single pipeline state."""
    data = state.to_dict()
    console.print()
    console.rule(f"[bold]{state.pipeline_name}[/bold] — {state.state_id}")
    console.print(f"  Status:  {_icon(state.status)} {state.status}")
    console.print(f"  Project: {state.project_dir}")
    console.print(f"  Health:  {data.get('health_score', '?')}/100")
    console.print(f"  Created: {state.metadata.get('created_at', '?')}")
    console.print(f"  Updated: {state.metadata.get('updated_at', '?')}")

    if state.steps:
        completed = len(state.completed_step_names())
        console.print(f"  Steps ({completed}/{len(state.steps)}):")
        for step in state.steps:
            s_status = step.get("status", "unknown")
            dur = step.get("duration_ms", 0)
            dur_str = f" ({dur}ms)" if dur else ""
            console.print(f"    {_icon(s_status)} {step.get('name', '?')}{dur_str}")

    if state.deviations:
        console.print(f"  Deviations ({len(state.deviations)}):")
        for dev in state.deviations:
            console.print(
                f"    ⚠️  [{dev.get('severity', '?')}] {dev.get('description', '?')}"
            )


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


@pipeline_app.command("run")
def pipeline_run(
    name: str = typer.Argument(..., help="Pipeline name to execute."),
    project: str = typer.Option(".", "--project", "-p", help="Project directory for this run."),
    continue_on_error: bool = typer.Option(
        False, "--continue-on-error", help="Continue after phase failure."
    ),
) -> None:
    """Execute a named pipeline using the pipeline engine."""
    executor = _create_executor()

    try:
        pipeline = executor.load_pipeline(name)
    except (FileNotFoundError, ValueError) as exc:
        print_error(str(exc))
        raise typer.Exit(1)

    step_count = len(pipeline.steps)

    if not is_json():
        console.print()
        console.rule(f"[bold cyan]Pipeline: {pipeline.name}[/bold cyan]")
        console.print(f"  Project:   {project}")
        console.print(f"  Steps:     {step_count}")
        console.print(f"  Resumable: {pipeline.resumable}")
        console.print()

    def _cli_step_handler(step_config, context):
        step_name = step_config.get("name", "unknown")
        step_agent = step_config.get("agent", "unknown")
        step_index = context.get("step_index", 0)

        if not is_json():
            console.print(
                f"  [bold]Phase {step_index + 1}/{step_count}:[/bold] "
                f"{step_name} -> {step_agent}"
            )

        # Build a lightweight state proxy from context for the real handler
        state_dict = context.get("state", {})

        class _StateProxy:
            def __init__(self, d):
                self.accumulated = d.get("accumulated", {})
                self.steps = d.get("steps", [])
                self.project_dir = context.get("project_dir", ".")

        result = executor._default_step_handler(step_config, _StateProxy(state_dict))

        if not is_json():
            icon = _icon(result.status.value)
            console.print(f"    {icon} {step_name} -- {result.status.value}")
            if result.artifacts:
                for a in result.artifacts:
                    console.print(f"      -> {a}")
            if result.errors:
                for e in result.errors:
                    print_warning(f"      {e}")

        return result

    try:
        final_state = executor.execute(
            pipeline=pipeline,
            project_dir=project,
            step_handler=_cli_step_handler,
        )
    except Exception as exc:
        print_error(f"Pipeline execution failed: {exc}")
        raise typer.Exit(1)

    state_id = final_state.get("state_id", "unknown")
    status = final_state.get("status", "unknown")

    if is_json():
        print_json(json_envelope(command="pipeline run", data=final_state))
        return

    console.print()
    if status == PipelineStatus.COMPLETED.value:
        print_success(f"Pipeline '{name}' completed successfully.")
    elif status == PipelineStatus.FAILED.value:
        print_error(f"Pipeline '{name}' failed.")
    else:
        print_info(f"Pipeline '{name}' finished with status: {status}")

    console.print(f"  State ID: {state_id}")
    console.print(f"  Health:   {final_state.get('health_score', '?')}/100")
    console.print()


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


@pipeline_app.command("status")
def pipeline_status(
    state_id: Optional[str] = typer.Argument(None, help="Pipeline state ID to inspect."),
) -> None:
    """Show pipeline execution status by loading PipelineState."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    if state_id:
        state = PipelineState.load(state_id, STATE_DIR)
        if not state:
            print_error(f"Pipeline state '{state_id}' not found.")
            raise typer.Exit(1)
        states = [state]
    else:
        state_files = sorted(
            STATE_DIR.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        if not state_files:
            print_info("No pipeline runs found.")
            raise typer.Exit(0)
        states = [
            s
            for sf in state_files
            if (s := PipelineState.load(sf.stem, STATE_DIR)) is not None
        ]

    if is_json():
        print_json(json_envelope(
            command="pipeline status",
            data={"runs": [s.to_dict() for s in states]},
        ))
        return

    for state in states:
        _print_state_detail(state)
    console.print()


# ---------------------------------------------------------------------------
# resume
# ---------------------------------------------------------------------------


@pipeline_app.command("resume")
def pipeline_resume(
    state_id: str = typer.Argument(..., help="Pipeline state ID to resume."),
) -> None:
    """Resume a paused or failed pipeline from its last checkpoint."""
    executor = _create_executor()

    state = PipelineState.load(state_id, STATE_DIR)
    if not state:
        print_error(f"Pipeline state '{state_id}' not found.")
        raise typer.Exit(1)

    if state.status == PipelineStatus.COMPLETED.value:
        print_warning(f"Pipeline '{state_id}' is already completed.")
        raise typer.Exit(0)

    if state.status == PipelineStatus.CANCELLED.value:
        print_error(f"Pipeline '{state_id}' was cancelled and cannot be resumed.")
        raise typer.Exit(1)

    if not is_json():
        completed = state.completed_step_names()
        console.print()
        console.rule(f"[bold cyan]Resuming: {state.pipeline_name}[/bold cyan]")
        console.print(f"  State ID:  {state_id}")
        console.print(f"  Completed: {len(completed)} step(s)")
        console.print()

    try:
        final_state = executor.resume(state_id)
    except (FileNotFoundError, ValueError) as exc:
        print_error(str(exc))
        raise typer.Exit(1)
    except Exception as exc:
        print_error(f"Resume failed: {exc}")
        raise typer.Exit(1)

    status = final_state.get("status", "unknown")

    if is_json():
        print_json(json_envelope(command="pipeline resume", data=final_state))
        return

    console.print()
    if status == PipelineStatus.COMPLETED.value:
        print_success(f"Pipeline '{state.pipeline_name}' resumed and completed.")
    elif status == PipelineStatus.FAILED.value:
        print_error(f"Pipeline '{state.pipeline_name}' failed after resume.")
    else:
        print_info(f"Pipeline '{state.pipeline_name}' status: {status}")

    console.print(f"  Health: {final_state.get('health_score', '?')}/100")
    console.print()


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


@pipeline_app.command("list")
def pipeline_list() -> None:
    """List all active pipeline execution states."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    state_files = sorted(
        STATE_DIR.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    if not state_files:
        if is_json():
            print_json(json_envelope(command="pipeline list", data={"pipelines": []}))
        else:
            print_info("No pipeline runs found.")
        raise typer.Exit(0)

    entries: list[PipelineState] = [
        s
        for sf in state_files
        if (s := PipelineState.load(sf.stem, STATE_DIR)) is not None
    ]

    if is_json():
        print_json(json_envelope(
            command="pipeline list",
            data={"pipelines": [s.to_dict() for s in entries]},
        ))
        return

    console.print()
    console.rule("[bold cyan]Pipeline Runs[/bold cyan]")
    console.print()

    for state in entries:
        completed = len(state.completed_step_names())
        total = len(state.steps)
        console.print(
            f"  {_icon(state.status)} [bold]{state.state_id}[/bold]  "
            f"{state.pipeline_name}  "
            f"[dim]{state.project_dir}[/dim]  "
            f"steps: {completed}/{total}  "
            f"health: {state.get_health_score()}/100"
        )

    console.print()
    console.print(f"  Total: {len(entries)} pipeline run(s)")
    console.print()


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------


@pipeline_app.command("cancel")
def pipeline_cancel(
    state_id: str = typer.Argument(..., help="Pipeline state ID to cancel."),
) -> None:
    """Cancel an active pipeline execution."""
    state = PipelineState.load(state_id, STATE_DIR)
    if not state:
        print_error(f"Pipeline state '{state_id}' not found.")
        raise typer.Exit(1)

    if state.status in (PipelineStatus.COMPLETED.value, PipelineStatus.CANCELLED.value):
        print_warning(f"Pipeline '{state_id}' is already {state.status}.")
        raise typer.Exit(0)

    previous_status = state.status
    state.update_status(PipelineStatus.CANCELLED.value)
    state.save(STATE_DIR)

    if is_json():
        print_json(json_envelope(command="pipeline cancel", data=state.to_dict()))
        return

    print_success(f"Pipeline '{state_id}' cancelled.")
    console.print(f"  Pipeline: {state.pipeline_name}")
    console.print(f"  Previous: {previous_status}")
    console.print()
