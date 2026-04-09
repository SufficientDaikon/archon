"""
Archon Pipeline Engine — Core execution engine for enforced pipelines.

Provides PipelineExecutor class that:
- Loads pipeline YAML definitions
- Executes steps in order with state machine transitions
- Validates artifacts between steps via hooks
- Handles failures with configurable policies
- Supports loop/retry/escalation
- Maintains accumulated state across phases
"""

from __future__ import annotations

import importlib.util
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import yaml

ARCHON_ROOT = Path(__file__).parent.parent.parent.parent


class PipelineStatus(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    LOOPING = "looping"


@dataclass
class StepResult:
    """Result of executing a single pipeline step."""
    step_name: str
    status: StepStatus
    duration_ms: int = 0
    artifacts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    compliance_score: float = 0.0
    thinking_trace: dict[str, Any] | None = None
    attempt: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_name": self.step_name,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "artifacts": self.artifacts,
            "errors": self.errors,
            "warnings": self.warnings,
            "compliance_score": self.compliance_score,
            "attempt": self.attempt,
        }


@dataclass
class PipelineDefinition:
    """Parsed pipeline YAML definition."""
    name: str
    version: str
    description: str
    trigger: str
    tags: list[str]
    synapse_mode: str
    steps: list[dict[str, Any]]
    resumable: bool = True
    artifact_persistence: str = "project-local"

    @classmethod
    def from_yaml(cls, path: Path) -> PipelineDefinition:
        """Load pipeline definition from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description", ""),
            trigger=data.get("trigger", ""),
            tags=data.get("tags", []),
            synapse_mode=data.get("synapse-mode", "standard"),
            steps=data.get("steps", []),
            resumable=data.get("resumable", True),
            artifact_persistence=data.get("artifact-persistence", "project-local"),
        )


class PipelineExecutor:
    """
    Core pipeline execution engine.

    Orchestrates step-by-step pipeline execution with:
    - State machine transitions (pending → validating → executing → completed/failed)
    - Pre/post step hooks for validation
    - Failure handling (retry, loop, escalate, halt, skip)
    - Accumulated state management
    - Artifact validation between steps
    """

    def __init__(
        self,
        hooks_dir: Path | None = None,
        state_dir: Path | None = None,
        simulation: bool = False,
    ):
        self.hooks_dir = hooks_dir or ARCHON_ROOT / "hooks"
        from archon.utils.paths import get_archon_home
        self.state_dir = state_dir or get_archon_home() / "pipeline-states"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.simulation = simulation

        self._hooks: dict[str, Callable] = {}
        self._load_hooks()

    def _load_hooks(self) -> None:
        """Load hook handlers from hooks directory."""
        hook_names = ["session_start", "pre_step", "post_step", "on_failure", "on_deviation"]
        for hook_name in hook_names:
            hook_path = self.hooks_dir / f"{hook_name}.py"
            if hook_path.exists():
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"hooks.{hook_name}", hook_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        if hasattr(module, "execute"):
                            self._hooks[hook_name] = module.execute
                except Exception as e:
                    print(f"Warning: Failed to load hook '{hook_name}': {e}", file=sys.stderr)

    def load_pipeline(self, name: str) -> PipelineDefinition:
        """Load a pipeline definition by name."""
        pipelines_dir = ARCHON_ROOT / "pipelines"
        pipeline_path = pipelines_dir / f"{name}.yaml"

        if not pipeline_path.exists():
            raise FileNotFoundError(f"Pipeline '{name}' not found at {pipeline_path}")

        pipeline = PipelineDefinition.from_yaml(pipeline_path)

        if not pipeline.steps:
            raise ValueError(f"Pipeline '{name}' has no steps defined")

        return pipeline

    def execute(
        self,
        pipeline: PipelineDefinition,
        project_dir: str = ".",
        config: dict[str, Any] | None = None,
        step_handler: Callable[[dict[str, Any], dict[str, Any]], StepResult] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a full pipeline.

        Args:
            pipeline: Loaded pipeline definition
            project_dir: Project directory for artifacts
            config: Additional pipeline configuration
            step_handler: Callback to execute each step
                         Signature: (step_config, context) -> StepResult

        Returns:
            Final pipeline state dict
        """
        from .pipeline_state import PipelineState

        config = config or {}
        state = PipelineState.create(pipeline.name, project_dir)
        state._state_dir = self.state_dir
        state.save(self.state_dir)

        # Fire session-start hook
        self._fire_hook("session_start", {"pipeline": pipeline.name})

        state.update_status(PipelineStatus.EXECUTING.value)

        for step_index, step_config in enumerate(pipeline.steps):
            step_name = step_config.get("name", f"step-{step_index}")
            step_agent = step_config.get("agent", "unknown")

            # Fire pre-step hook
            pre_result = self._fire_hook("pre_step", {
                "pipeline": pipeline.name,
                "step": step_name,
                "step_index": step_index,
                "state": state.to_dict(),
                "step_config": step_config,
            })

            if pre_result and pre_result.get("status") == "fail":
                state.record_step(step_name, StepStatus.FAILED.value, {
                    "errors": pre_result.get("errors", []),
                    "phase": "pre-validation",
                })
                failure_action = self._handle_failure(
                    step_config, step_name, pre_result.get("errors", []), 1, state
                )
                if failure_action == "halt":
                    state.update_status(PipelineStatus.FAILED.value)
                    state.save(self.state_dir)
                    return state.to_dict()
                elif failure_action == "skip":
                    continue

            # Execute the step
            state.record_step(step_name, StepStatus.RUNNING.value)
            start_time = time.time()

            try:
                if step_handler:
                    step_result = step_handler(step_config, {
                        "state": state.to_dict(),
                        "project_dir": project_dir,
                        "config": config,
                        "step_index": step_index,
                    })
                else:
                    step_result = self._default_step_handler(step_config, state)
            except Exception as e:
                step_result = StepResult(
                    step_name=step_name,
                    status=StepStatus.FAILED,
                    errors=[str(e)],
                )

            duration_ms = int((time.time() - start_time) * 1000)
            step_result.duration_ms = duration_ms

            # Reload state from disk in case step handler modified it
            from .pipeline_state import PipelineState as _PS
            reloaded = _PS.load(state.state_id, self.state_dir)
            if reloaded:
                state.accumulated = reloaded.accumulated
                state.deviations = reloaded.deviations

            # Fire post-step hook
            post_result = self._fire_hook("post_step", {
                "pipeline": pipeline.name,
                "step": step_name,
                "step_index": step_index,
                "state": state.to_dict(),
                "step_config": step_config,
                "step_result": step_result.to_dict(),
            })

            # Handle post-step validation failure
            if post_result and post_result.get("status") == "fail":
                step_result.status = StepStatus.FAILED
                step_result.errors.extend(post_result.get("errors", []))

            # Record step result in state
            state.record_step(step_name, step_result.status.value, step_result.to_dict())
            state.save(self.state_dir)

            # Handle failure
            if step_result.status == StepStatus.FAILED:
                failure_action = self._handle_failure(
                    step_config, step_name, step_result.errors, step_result.attempt, state
                )
                if failure_action == "halt":
                    state.update_status(PipelineStatus.FAILED.value)
                    state.save(self.state_dir)
                    return state.to_dict()
                elif failure_action == "skip":
                    continue

        # All steps completed
        state.update_status(PipelineStatus.COMPLETED.value)
        state.save(self.state_dir)
        return state.to_dict()

    def validate_transition(
        self,
        from_step: dict[str, Any],
        to_step: dict[str, Any],
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate that transition from one step to another is allowed."""
        result = {"valid": True, "errors": [], "warnings": []}

        # Check that from_step has required output artifacts
        validation = to_step.get("validation", {})
        expected = validation.get("expected-artifacts", [])

        for artifact in expected:
            pattern = artifact.get("path-pattern", "")
            if pattern:
                project_dir = state.get("project_dir", ".")
                import glob
                matches = glob.glob(str(Path(project_dir) / pattern))
                if not matches:
                    result["valid"] = False
                    result["errors"].append(f"Transition blocked: missing artifact '{pattern}'")

        return result

    def resume(self, state_id: str, step_handler: Callable | None = None) -> dict[str, Any]:
        """Resume a paused or failed pipeline from its last checkpoint."""
        from .pipeline_state import PipelineState

        state = PipelineState.load(state_id, self.state_dir)
        if not state:
            raise ValueError(f"Pipeline state '{state_id}' not found")

        pipeline = self.load_pipeline(state.pipeline_name)

        # Find the step to resume from
        completed_steps = set(state.completed_step_names())
        remaining_steps = [
            (i, s) for i, s in enumerate(pipeline.steps)
            if s.get("name", f"step-{i}") not in completed_steps
        ]

        if not remaining_steps:
            state.update_status(PipelineStatus.COMPLETED.value)
            return state.to_dict()

        state.update_status(PipelineStatus.EXECUTING.value)

        for step_index, step_config in remaining_steps:
            step_name = step_config.get("name", f"step-{step_index}")

            state.record_step(step_name, StepStatus.RUNNING.value)
            start_time = time.time()

            try:
                if step_handler:
                    step_result = step_handler(step_config, {
                        "state": state.to_dict(),
                        "project_dir": state.project_dir,
                        "step_index": step_index,
                    })
                else:
                    step_result = self._default_step_handler(step_config, state)
            except Exception as e:
                step_result = StepResult(
                    step_name=step_name,
                    status=StepStatus.FAILED,
                    errors=[str(e)],
                )

            step_result.duration_ms = int((time.time() - start_time) * 1000)
            state.record_step(step_name, step_result.status.value, step_result.to_dict())

            if step_result.status == StepStatus.FAILED:
                state.update_status(PipelineStatus.FAILED.value)
                return state.to_dict()

        state.update_status(PipelineStatus.COMPLETED.value)
        return state.to_dict()

    def _default_step_handler(self, step_config: dict[str, Any], state: Any) -> StepResult:
        """Execute a pipeline step by dispatching to the named agent via Claude Code CLI.

        Resolves the agent's AGENT.md, constructs a prompt with the agent's
        instructions plus accumulated pipeline state, and dispatches via
        ``claude --print -p <prompt>``.

        In simulation mode (``self.simulation=True``), marks steps as completed
        immediately without executing anything -- useful for tests and dry runs.
        """
        step_name = step_config.get("name", "unknown")

        # Simulation mode: mark completed without doing work
        if self.simulation:
            return StepResult(
                step_name=step_name,
                status=StepStatus.COMPLETED,
                artifacts=[step_config.get("output", "")],
            )

        import json
        import subprocess

        step_name = step_config.get("name", "unknown")
        agent_name = step_config.get("agent", "")

        if not agent_name:
            return StepResult(
                step_name=step_name,
                status=StepStatus.FAILED,
                errors=["No agent specified for step"],
            )

        # Resolve agent AGENT.md
        agent_dir = ARCHON_ROOT / "agents" / agent_name
        agent_md = agent_dir / "AGENT.md"

        if not agent_md.exists():
            return StepResult(
                step_name=step_name,
                status=StepStatus.FAILED,
                errors=[f"Agent '{agent_name}' not found at {agent_dir}"],
            )

        agent_instructions = agent_md.read_text(encoding="utf-8")
        step_input = step_config.get("input", "")
        step_output_desc = step_config.get("output", "")

        # Build context from accumulated state
        context_payload = ""
        if hasattr(state, "accumulated"):
            context_payload = json.dumps(state.accumulated, indent=2, default=str)

        # Gather previous step artifacts
        prev_artifacts = ""
        if hasattr(state, "steps") and state.steps:
            artifact_lines = []
            for prev in state.steps:
                if prev.get("status") == "completed" and prev.get("artifacts"):
                    artifact_lines.append(
                        f"- {prev['step_name']}: {', '.join(prev['artifacts'])}"
                    )
            if artifact_lines:
                prev_artifacts = "\n".join(artifact_lines)

        # Construct the prompt
        prompt_parts = [
            f"# Agent: {agent_name}",
            "",
            agent_instructions,
            "",
            f"# Step: {step_name}",
            f"## Input\n{step_input}",
            f"## Expected Output\n{step_output_desc}",
        ]
        if context_payload:
            prompt_parts.append(f"## Accumulated Context\n```json\n{context_payload}\n```")
        if prev_artifacts:
            prompt_parts.append(f"## Previous Step Artifacts\n{prev_artifacts}")

        prompt = "\n\n".join(prompt_parts)

        # Resolve project directory
        project_dir = "."
        if hasattr(state, "project_dir"):
            project_dir = state.project_dir

        # Execute via Claude Code CLI
        try:
            result = subprocess.run(
                ["claude", "--print", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=project_dir,
            )

            if result.returncode != 0:
                stderr_snippet = result.stderr[:500] if result.stderr else "no stderr"
                return StepResult(
                    step_name=step_name,
                    status=StepStatus.FAILED,
                    errors=[f"Claude CLI exited with code {result.returncode}: {stderr_snippet}"],
                )

            # Write output artifact to project dir
            artifacts = []
            if result.stdout:
                output_dir = Path(project_dir) / ".archon" / "artifacts"
                output_dir.mkdir(parents=True, exist_ok=True)
                out_file = output_dir / f"{step_name}-output.md"
                out_file.write_text(result.stdout, encoding="utf-8")
                artifacts.append(str(out_file))

            return StepResult(
                step_name=step_name,
                status=StepStatus.COMPLETED,
                artifacts=artifacts,
            )

        except subprocess.TimeoutExpired:
            return StepResult(
                step_name=step_name,
                status=StepStatus.FAILED,
                errors=["Agent execution timed out (600s)"],
            )
        except FileNotFoundError:
            return StepResult(
                step_name=step_name,
                status=StepStatus.FAILED,
                errors=[
                    "Claude Code CLI not found. "
                    "Install with: npm install -g @anthropic-ai/claude-code"
                ],
            )

    def _handle_failure(
        self,
        step_config: dict[str, Any],
        step_name: str,
        errors: list[str],
        attempt: int,
        state: Any,
    ) -> str:
        """Handle step failure using on-failure hook and policy."""
        failure_result = self._fire_hook("on_failure", {
            "pipeline": state.pipeline_name if hasattr(state, "pipeline_name") else "unknown",
            "step": step_name,
            "error": "; ".join(errors),
            "attempt": attempt,
            "max_retries": 3,
            "step_config": step_config,
        })

        if failure_result:
            return failure_result.get("action", "halt")
        return "halt"

    def _fire_hook(self, hook_name: str, context: dict[str, Any]) -> dict[str, Any] | None:
        """Fire a hook and return its result."""
        handler = self._hooks.get(hook_name)
        if handler:
            try:
                return handler(context)
            except Exception as e:
                print(f"Warning: Hook '{hook_name}' failed: {e}", file=sys.stderr)
                return None
        return None
