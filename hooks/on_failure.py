"""
Archon On-Failure Hook

Fires when a pipeline step fails. Implements retry, loop, escalation,
and auto-recovery protocols.
"""

from pathlib import Path
from typing import Any

ARCHON_ROOT = Path(__file__).parent.parent


def execute(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    On-failure hook. Determines recovery strategy for failed pipeline steps.

    Args:
        context: Dict with keys:
            - pipeline: Pipeline name
            - step: Failed step name
            - step_index: Step number
            - state: Pipeline state
            - step_config: Step configuration
            - error: Error description
            - attempt: Current attempt number
            - max_retries: Maximum retry attempts

    Returns:
        Dict with:
            - action: "retry" | "loop" | "escalate" | "halt" | "skip"
            - reason: Why this action was chosen
            - modifications: Changes to make before retry
    """
    context = context or {}
    result: dict[str, Any] = {
        "action": "halt",
        "reason": "",
        "modifications": {},
    }

    step_config = context.get("step_config", {})
    attempt = context.get("attempt", 1)
    max_retries = context.get("max_retries", 3)
    error = context.get("error", "Unknown error")
    on_failure = step_config.get("on-failure", "halt")

    # 3-Fix Escape Hatch: If 3+ attempts, architecture may be wrong
    if attempt >= 3:
        result["action"] = "escalate"
        result["reason"] = (
            f"⚠️ 3-FIX ESCAPE HATCH: Step '{context.get('step', 'unknown')}' "
            f"has failed {attempt} times. This suggests an architecture problem, "
            f"not a bug fix problem. Escalating to human review."
        )
        return result

    # Policy-based decision
    if on_failure == "retry" and attempt < max_retries:
        result["action"] = "retry"
        result["reason"] = (
            f"Retry policy: attempt {attempt + 1}/{max_retries} "
            f"for step '{context.get('step', 'unknown')}'"
        )

    elif on_failure == "loop":
        loop_target = step_config.get("loop-target")
        max_iterations = step_config.get("max-iterations", 3)
        if attempt < max_iterations:
            result["action"] = "loop"
            result["reason"] = (
                f"Loop policy: sending back to '{loop_target}' "
                f"(iteration {attempt + 1}/{max_iterations})"
            )
            result["modifications"]["loop_target"] = loop_target
        else:
            result["action"] = "escalate"
            result["reason"] = (
                f"Loop exhausted: max iterations ({max_iterations}) reached "
                f"for loop to '{loop_target}'"
            )

    elif on_failure == "skip":
        result["action"] = "skip"
        result["reason"] = (
            f"Skip policy: skipping step '{context.get('step', 'unknown')}' — "
            f"error: {error}"
        )

    elif on_failure == "escalate":
        result["action"] = "escalate"
        result["reason"] = f"Escalation policy: step '{context.get('step', 'unknown')}' failed"

    else:
        result["action"] = "halt"
        result["reason"] = (
            f"Halt policy (default): pipeline stopped at step "
            f"'{context.get('step', 'unknown')}' — error: {error}"
        )

    return result


def _check_auto_recovery(context: dict[str, Any]) -> dict[str, Any] | None:
    """
    Check if the failure can be auto-recovered.
    Returns recovery action or None.
    """
    error = context.get("error", "")
    error_lower = error.lower()

    recovery_patterns = {
        "file not found": {"action": "retry", "fix": "Check file paths"},
        "permission denied": {"action": "halt", "fix": "Fix permissions"},
        "timeout": {"action": "retry", "fix": "Increase timeout"},
        "connection refused": {"action": "retry", "fix": "Check service availability"},
        "out of memory": {"action": "halt", "fix": "Reduce scope or increase resources"},
    }

    for pattern, recovery in recovery_patterns.items():
        if pattern in error_lower:
            return recovery

    return None


if __name__ == "__main__":
    test_context = {
        "pipeline": "sdd-pipeline",
        "step": "implement",
        "error": "Artifact validation failed: spec.md not found",
        "attempt": 1,
        "max_retries": 3,
        "step_config": {"on-failure": "retry"},
    }
    result = execute(test_context)
    print(f"Failure action: {result['action']}")
    print(f"Reason: {result['reason']}")
