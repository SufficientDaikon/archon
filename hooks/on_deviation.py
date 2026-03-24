"""
Archon On-Deviation Hook

Fires when an agent requests a deviation from the spec or plan.
Implements the STOP → DOCUMENT → ASK → LOG protocol.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARCHON_ROOT = Path(__file__).parent.parent


def execute(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    On-deviation hook. Records and manages deviation requests.

    Args:
        context: Dict with keys:
            - pipeline: Pipeline name
            - step: Current step
            - agent: Agent requesting deviation
            - what: Description of the deviation
            - why: Technical justification
            - impact: What the deviation affects
            - alternatives: List of alternatives considered
            - severity: critical / major / minor

    Returns:
        Dict with:
            - status: "logged" | "escalated"
            - deviation_id: Unique deviation identifier
            - action: Next step for the agent
    """
    context = context or {}
    result: dict[str, Any] = {
        "status": "logged",
        "deviation_id": "",
        "action": "",
    }

    deviation = {
        "id": _generate_deviation_id(context),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": context.get("pipeline", "unknown"),
        "step": context.get("step", "unknown"),
        "agent": context.get("agent", "unknown"),
        "what": context.get("what", "No description provided"),
        "why": context.get("why", "No justification provided"),
        "impact": context.get("impact", "Unknown impact"),
        "alternatives": context.get("alternatives", []),
        "severity": context.get("severity", "major"),
        "status": "requested",
    }

    result["deviation_id"] = deviation["id"]

    # Log the deviation
    _log_deviation(deviation)

    # Determine action based on severity
    severity = deviation["severity"]
    if severity == "critical":
        result["status"] = "escalated"
        result["action"] = (
            "HALT: Critical deviation requires human approval. "
            "Do NOT proceed until deviation is approved."
        )
    elif severity == "major":
        result["status"] = "logged"
        result["action"] = (
            "PAUSE: Major deviation logged. Request approval before implementing. "
            f"Deviation ID: {deviation['id']}"
        )
    else:
        result["status"] = "logged"
        result["action"] = (
            "CONTINUE with caution: Minor deviation logged. "
            f"Deviation ID: {deviation['id']}"
        )

    return result


def _generate_deviation_id(context: dict[str, Any]) -> str:
    """Generate a unique deviation ID."""
    import hashlib

    pipeline = context.get("pipeline", "unknown")
    step = context.get("step", "unknown")
    timestamp = datetime.now(timezone.utc).isoformat()
    hash_input = f"{pipeline}:{step}:{timestamp}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    return f"DEV-{short_hash[:3].upper()}"


def _log_deviation(deviation: dict[str, Any]) -> None:
    """Write deviation to log file."""
    import json

    log_dir = Path.home() / ".copilot" / ".archon" / "deviations"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{deviation['pipeline']}-deviations.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(deviation) + "\n")


if __name__ == "__main__":
    test_context = {
        "pipeline": "sdd-pipeline",
        "step": "implement",
        "agent": "implementer",
        "what": "Using SQLite instead of PostgreSQL",
        "why": "Development environment doesn't have PostgreSQL",
        "impact": "Database schema may need adjustment for production",
        "alternatives": ["Docker PostgreSQL", "In-memory database"],
        "severity": "major",
    }
    result = execute(test_context)
    print(f"Deviation {result['deviation_id']}: {result['status']}")
    print(f"Action: {result['action']}")
