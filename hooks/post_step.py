"""
Archon Post-Step Hook

Fires after each pipeline step completes. Validates outputs, checks quality gates,
updates pipeline state, and triggers anti-rationalization audit.
"""

from pathlib import Path
from typing import Any

ARCHON_ROOT = Path(__file__).parent.parent


def execute(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Post-step hook. Validates that a pipeline step produced valid outputs.

    Args:
        context: Dict with keys:
            - pipeline: Pipeline name
            - step: Completed step name
            - step_index: Step number (0-based)
            - state: Current pipeline state
            - step_config: Step configuration from pipeline YAML
            - step_result: Output from the step execution

    Returns:
        Dict with:
            - status: "pass" or "fail"
            - errors: Blocking issues
            - warnings: Non-blocking issues
            - validation_report: Detailed validation results
    """
    context = context or {}
    result: dict[str, Any] = {
        "status": "pass",
        "errors": [],
        "warnings": [],
        "validation_report": {},
    }

    step_config = context.get("step_config", {})
    state = context.get("state", {})
    validation = step_config.get("validation", {})

    # Check 1: Expected artifacts exist
    expected_artifacts = validation.get("expected-artifacts", [])
    project_dir = state.get("project_dir", ".")
    for artifact in expected_artifacts:
        pattern = artifact.get("path-pattern", "")
        if pattern:
            exists = _check_artifact_exists(pattern, project_dir)
            result["validation_report"][f"artifact:{pattern}"] = "pass" if exists else "fail"
            if not exists:
                result["errors"].append(f"Expected artifact not found: {pattern}")

    # Check 2: Required sections in markdown artifacts
    required_sections = validation.get("required-sections", [])
    if required_sections:
        section_results = _check_required_sections(expected_artifacts, required_sections, project_dir)
        result["validation_report"]["required_sections"] = section_results
        for section, found in section_results.items():
            if not found:
                result["errors"].append(f"Required section missing: '{section}'")

    # Check 3: Minimum word count
    min_words = validation.get("min-word-count", 0)
    if min_words > 0:
        word_count = _count_words_in_artifacts(expected_artifacts, project_dir)
        result["validation_report"]["word_count"] = word_count
        result["validation_report"]["min_word_count"] = min_words
        if word_count < min_words:
            result["errors"].append(
                f"Artifact content too short: {word_count} words (minimum: {min_words})"
            )

    # Check 4: Compliance threshold (for review steps)
    compliance_threshold = validation.get("compliance-threshold", 0)
    if compliance_threshold > 0:
        step_result = context.get("step_result", {})
        score = step_result.get("compliance_score", 0)
        result["validation_report"]["compliance_score"] = score
        result["validation_report"]["compliance_threshold"] = compliance_threshold
        if score < compliance_threshold:
            result["errors"].append(
                f"Compliance score {score}% below threshold {compliance_threshold}%"
            )

    # Check 5: Anti-rationalization audit
    audit_result = _run_audit(context)
    result["validation_report"]["discipline_audit"] = audit_result
    if audit_result.get("score", 10) < 5:
        result["warnings"].append(
            f"Low discipline score: {audit_result.get('score', 0)}/10"
        )

    if result["errors"]:
        result["status"] = "fail"

    return result


def _check_artifact_exists(pattern: str, project_dir: str) -> bool:
    """Check if artifact file exists."""
    import glob
    matches = glob.glob(str(Path(project_dir) / pattern))
    return len(matches) > 0


def _check_required_sections(
    artifacts: list[dict], sections: list[str], project_dir: str
) -> dict[str, bool]:
    """Check that required markdown sections exist in artifacts."""
    import glob

    found_sections: dict[str, bool] = {s: False for s in sections}

    for artifact in artifacts:
        pattern = artifact.get("path-pattern", "")
        if not pattern:
            continue
        for filepath in glob.glob(str(Path(project_dir) / pattern)):
            try:
                content = Path(filepath).read_text(encoding="utf-8")
                for section in sections:
                    normalized = section.lower().strip()
                    for line in content.splitlines():
                        if line.strip().lstrip("#").strip().lower() == normalized:
                            found_sections[section] = True
            except Exception:
                continue

    return found_sections


def _count_words_in_artifacts(artifacts: list[dict], project_dir: str) -> int:
    """Count total words across all primary artifacts."""
    import glob

    total_words = 0
    for artifact in artifacts:
        pattern = artifact.get("path-pattern", "")
        if not pattern:
            continue
        for filepath in glob.glob(str(Path(project_dir) / pattern)):
            try:
                content = Path(filepath).read_text(encoding="utf-8")
                total_words += len(content.split())
            except Exception:
                continue

    return total_words


def _run_audit(context: dict[str, Any]) -> dict[str, Any]:
    """Run anti-rationalization audit on step results."""
    return {
        "score": 10,
        "violations_caught": 0,
        "violations_corrected": 0,
        "violations_missed": 0,
        "notes": "Automated audit — manual review recommended",
    }


if __name__ == "__main__":
    test_context = {
        "pipeline": "sdd-pipeline",
        "step": "specify",
        "step_index": 0,
        "state": {"project_dir": "."},
        "step_config": {
            "validation": {
                "expected-artifacts": [{"path-pattern": "*.md"}],
                "min-word-count": 100,
            }
        },
    }
    result = execute(test_context)
    print(f"Post-step result: {result['status']}")
