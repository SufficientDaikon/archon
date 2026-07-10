#!/usr/bin/env python3
"""Stop hook — completion gate that enforces quality before session ends.

Fires when Claude stops responding. Blocks completion (exit 2) if code was
modified and tests or build are known to have failed. Persists final session
state for next-session continuity.

Loop protection: respects stop_hook_active (never re-block a stop that a Stop
hook already blocked) and caps blocks at 2 per session — after that the gate
downgrades to a stderr warning so a persistently failing session can still end.

Note: Stop hooks cannot inject context (additionalContext is not consumed for
Stop) — the only mechanisms that work are exit 2 + stderr, so the pass path is
silent by design.
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.config import get_property
from shared.state import archive_session, load_state, save_state


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    cwd = input_data.get("cwd")
    state = load_state(cwd)
    session = state["session"]
    files_modified = session.get("files_modified", [])

    # No code modified — conversational session, no gates needed
    if not files_modified:
        persist_and_archive(state, cwd)
        print(json.dumps({}))
        return

    passed, failures = check_quality_gates(session)

    if passed:
        persist_and_archive(state, cwd)
        print(json.dumps({}))
        return

    # Gate disabled by config: warn on stderr but never block. State is
    # still persisted and archived — disabling the gate must not lose data.
    if not get_property("gate/enabled", cwd):
        sys.stderr.write(
            f"Archon completion gate (disabled by gate/enabled=false): {'; '.join(failures)}\n"
        )
        persist_and_archive(state, cwd)
        print(json.dumps({}))
        return

    # stop_hook_active means a Stop hook already blocked this stop once —
    # blocking again would loop forever.
    already_blocking = bool(input_data.get("stop_hook_active"))
    blocks_so_far = session.get("gate_blocks", 0)

    if already_blocking or blocks_so_far >= get_property("gate/max_blocks", cwd):
        sys.stderr.write(
            "Archon completion gate: quality checks still failing "
            f"({'; '.join(failures)}) — allowing stop after "
            f"{blocks_so_far} block(s) to avoid a loop.\n"
        )
        persist_and_archive(state, cwd)
        print(json.dumps({}))
        return

    session["gate_blocks"] = blocks_so_far + 1
    persist_and_archive(state, cwd)

    failure_text = "\n".join(f"  - {f}" for f in failures)
    reason = (
        "Archon completion gate: quality checks failed.\n"
        f"{failure_text}\n"
        "Please address these before finishing."
    )
    # Exit 2 = block the stop, force Claude to continue
    sys.stderr.write(reason)
    sys.exit(2)


def check_quality_gates(session: dict) -> tuple[bool, list[str]]:
    """Check quality gates. Returns (passed, [blocking failures])."""
    failures = []
    files_modified = session.get("files_modified", [])

    # Only check code files (skip markdown, configs)
    code_files = [
        f
        for f in files_modified
        if any(
            f.endswith(ext)
            for ext in (
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".rs",
                ".go",
                ".java",
                ".c",
                ".cpp",
                ".cs",
                ".rb",
                ".php",
            )
        )
    ]

    if not code_files:
        return True, []

    # Block only on confirmed failure — "tests never ran" is not a failure.
    if session.get("tests_passed") is False:
        failures.append(
            f"Tests FAILED. {len(code_files)} code file(s) were modified — tests must pass."
        )
    if session.get("build_passed") is False:
        failures.append(
            f"Build FAILED. {len(code_files)} code file(s) were modified — build must pass."
        )

    return len(failures) == 0, failures


def persist_and_archive(state: dict, cwd: str | None = None) -> None:
    """Save final state. Archive to history if session had activity."""
    if state["session"].get("files_modified"):
        archive_session(state)
    save_state(state, cwd)


if __name__ == "__main__":
    main()
