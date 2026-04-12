#!/usr/bin/env python3
"""Stop hook — completion gate that enforces quality before session ends.

Fires when Claude stops responding. Checks if tests/build passed when code
was modified. Blocks completion (exit 2) if quality gates fail. Persists
final session state for next-session continuity.

This is the most valuable single hook — it prevents declaring "done" when
things are broken.
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.state import load_state, save_state


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    state = load_state()
    session = state["session"]
    files_modified = session.get("files_modified", [])

    # No code modified — conversational session, no gates needed
    if not files_modified:
        persist_and_archive(state)
        print(json.dumps({}))
        return

    # Quality gate checks
    passed, failures, warnings = check_quality_gates(session)

    # Always persist state (even if blocking)
    persist_and_archive(state)

    if not passed:
        failure_text = "\n".join(f"  - {f}" for f in failures)
        reason = f"Archon completion gate: quality checks failed.\n{failure_text}\nPlease address these before finishing."

        # Exit 2 = block the stop, force Claude to continue
        sys.stderr.write(reason)
        sys.exit(2)
    else:
        # Pass with summary (include warnings as advisory context)
        summary = build_completion_summary(session, warnings)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": summary,
            }
        }
        print(json.dumps(output))


def check_quality_gates(session: dict) -> tuple[bool, list[str], list[str]]:
    """Check quality gates. Returns (passed, [blocking failures], [advisory warnings])."""
    failures = []
    warnings = []
    files_modified = session.get("files_modified", [])

    # Only check code files (skip markdown, configs)
    code_files = [
        f for f in files_modified
        if any(f.endswith(ext) for ext in (
            ".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go",
            ".java", ".c", ".cpp", ".cs", ".rb", ".php",
        ))
    ]

    if not code_files:
        return True, [], []

    tests_passed = session.get("tests_passed")
    build_passed = session.get("build_passed")

    # Block: tests explicitly failed
    if tests_passed is False:
        failures.append(f"Tests FAILED. {len(code_files)} code file(s) were modified — tests must pass.")

    # Block: build explicitly failed
    if build_passed is False:
        failures.append(f"Build FAILED. {len(code_files)} code file(s) were modified — build must pass.")

    # Warn (don't block): tests were never run on substantial changes
    if tests_passed is None and len(code_files) >= 3:
        warnings.append(f"Tests were NEVER RUN this session. {len(code_files)} code files modified — consider running tests.")

    return len(failures) == 0, failures, warnings


def persist_and_archive(state: dict) -> None:
    """Save final state. Archive to history if session had activity."""
    session = state["session"]

    if session.get("files_modified"):
        # Build session summary for history
        summary = {
            "id": session.get("id", ""),
            "started": session.get("started", ""),
            "files_modified_count": len(session.get("files_modified", [])),
            "tests_passed": session.get("tests_passed"),
            "build_passed": session.get("build_passed"),
            "complexity_tier": session.get("complexity_tier", ""),
            "todos_completed": session.get("todos_completed", 0),
            "todos_total": session.get("todos_total", 0),
        }

        history = state.setdefault("history", {"last_sessions": [], "unfinished_work": []})
        # Dedup check — don't double-archive if session_boot already did it
        existing_ids = [s.get("id") for s in history.get("last_sessions", [])]
        if summary["id"] and summary["id"] not in existing_ids:
            history["last_sessions"].insert(0, summary)
            history["last_sessions"] = history["last_sessions"][:3]

    save_state(state)


def build_completion_summary(session: dict, warnings: list[str]) -> str:
    """Build a brief completion summary."""
    files_count = len(session.get("files_modified", []))
    tests = session.get("tests_passed")
    build = session.get("build_passed")
    tier = session.get("complexity_tier", "N/A")

    parts = [f'<archon-completion tier="{tier}" files="{files_count}"']
    if tests is not None:
        parts.append(f' tests="{"pass" if tests else "fail"}"')
    if build is not None:
        parts.append(f' build="{"pass" if build else "fail"}"')
    parts.append(" />")

    result = "".join(parts)

    # Append warnings as advisory context
    if warnings:
        warning_lines = "\n".join(f"  - {w}" for w in warnings)
        result += f"\n<archon-warnings>\n{warning_lines}\n</archon-warnings>"

    return result


if __name__ == "__main__":
    main()
