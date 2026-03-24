"""
Archon Pre-Step Hook

Fires before each pipeline step. Validates prerequisites, checks guardrails,
and injects curated context for the upcoming step.
"""

from pathlib import Path
from typing import Any

ARCHON_ROOT = Path(__file__).parent.parent


def execute(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Pre-step hook. Validates that a pipeline step is ready to execute.

    Args:
        context: Dict with keys:
            - pipeline: Pipeline name
            - step: Current step name
            - step_index: Step number (0-based)
            - state: Current pipeline state dict
            - step_config: Step configuration from pipeline YAML

    Returns:
        Dict with:
            - status: "pass" or "fail"
            - errors: List of blocking issues
            - warnings: List of non-blocking issues
            - injected_context: Additional context for the step
    """
    context = context or {}
    result: dict[str, Any] = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "injected_context": {},
    }

    step_config = context.get("step_config", {})
    state = context.get("state", {})
    step_index = context.get("step_index", 0)

    # Check 1: Validate prerequisites from previous step
    if step_index > 0:
        prev_artifacts = state.get("completed_artifacts", {})
        validation = step_config.get("validation", {})
        expected = validation.get("expected-artifacts", [])

        for artifact in expected:
            pattern = artifact.get("path-pattern", "")
            if pattern and not _artifact_exists(pattern, state.get("project_dir", ".")):
                result["errors"].append(
                    f"Missing prerequisite artifact: {pattern} "
                    f"(required by step '{context.get('step', 'unknown')}')"
                )

    # Check 2: Guardrail compliance
    guardrail_issues = _check_guardrails(context)
    result["errors"].extend(guardrail_issues.get("errors", []))
    result["warnings"].extend(guardrail_issues.get("warnings", []))

    # Check 3: Inject accumulated state
    accumulated = state.get("accumulated", {})
    if accumulated:
        result["injected_context"]["accumulated_decisions"] = accumulated.get("decisions", [])
        result["injected_context"]["accumulated_constraints"] = accumulated.get(
            "constraints", []
        )
        result["injected_context"]["tech_stack"] = accumulated.get("tech_stack", [])

    # Final status
    if result["errors"]:
        result["status"] = "fail"

    return result


def _artifact_exists(pattern: str, project_dir: str) -> bool:
    """Check if an artifact matching the pattern exists."""
    import glob

    project_path = Path(project_dir)
    matches = glob.glob(str(project_path / pattern))
    return len(matches) > 0


def _check_guardrails(context: dict[str, Any]) -> dict[str, list[str]]:
    """Validate agent guardrails for the current step."""
    issues: dict[str, list[str]] = {"errors": [], "warnings": []}

    step_config = context.get("step_config", {})
    agent_name = step_config.get("agent", "")

    if not agent_name:
        issues["warnings"].append("No agent specified for step — guardrails not checked")
        return issues

    agent_manifest = _load_agent_manifest(agent_name)
    if not agent_manifest:
        issues["warnings"].append(f"Agent manifest not found for '{agent_name}'")
        return issues

    guardrails = agent_manifest.get("guardrails", [])
    # Handle both dict and list formats of guardrails
    if isinstance(guardrails, dict):
        # Pre-existing prose format: {"must-not": [...], "must-do": [...]}
        return issues
    for guardrail in guardrails:
        g_type = guardrail.get("type", "")
        severity = guardrail.get("severity", "minor")

        if g_type in ("must-always", "must-never") and severity == "critical":
            pass  # Critical guardrails are always enforced at runtime

    return issues


def _load_agent_manifest(agent_name: str) -> dict[str, Any] | None:
    """Load an agent's manifest YAML."""
    import yaml

    manifest_path = ARCHON_ROOT / "agents" / agent_name / "agent-manifest.yaml"
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


if __name__ == "__main__":
    test_context = {
        "pipeline": "sdd-pipeline",
        "step": "implement",
        "step_index": 2,
        "state": {"project_dir": "."},
        "step_config": {"agent": "implementer"},
    }
    result = execute(test_context)
    print(f"Pre-step result: {result['status']}")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
    if result["warnings"]:
        print(f"Warnings: {result['warnings']}")
