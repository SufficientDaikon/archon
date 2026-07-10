#!/usr/bin/env python3
"""PostToolUse [Bash] hook — tracks test and build results in state.

Fires after every Bash command. Detects test/build commands and records
their pass/fail status in archon-state.json for the completion gate.
"""

import json
import re
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.scanner import is_build_command, is_test_command
from shared.state import load_state, save_state


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")
    cwd = input_data.get("cwd")

    if not command:
        print(json.dumps({}))
        return

    # Check tool_response for exit code
    tool_response = input_data.get("tool_response", {})
    exit_code = _extract_exit_code(tool_response)
    # None = unknown (not verified), True = pass, False = fail
    if exit_code is None:
        passed = None
    else:
        passed = exit_code == 0

    updated = False
    state = load_state(cwd)

    if is_test_command(command):
        state["session"]["tests_passed"] = passed
        updated = True

    if is_build_command(command):
        state["session"]["build_passed"] = passed
        updated = True

    if updated:
        save_state(state, cwd)

    print(json.dumps({}))


# Test-runner summary lines. These are matched only when no exit code field
# exists. A bare word like "error" in output must NOT mark failure — passing
# runs legitimately print "0 errors" — so only explicit runner summaries count.
_RUNNER_SUMMARIES: list[tuple[re.Pattern, str]] = [
    # pytest / jest / vitest / mocha: "3 failed", "12 passed"
    (re.compile(r"\b(\d+)\s+failed\b", re.I), "failed_count"),
    (re.compile(r"\b\d+\s+(?:passed|passing)\b", re.I), "passed"),
    # cargo test: "test result: ok." / "test result: FAILED."
    (re.compile(r"\btest result:\s*ok\b", re.I), "passed"),
    (re.compile(r"\btest result:\s*FAILED\b", re.I), "failed"),
    # go test: leading "ok  <pkg>" / "FAIL<tab or space>"
    (re.compile(r"^ok\s+\S+", re.M), "passed"),
    (re.compile(r"^FAIL\s+\S+", re.M), "failed"),
]


def _parse_runner_summary(text: str) -> int | None:
    """Determine pass/fail from an explicit test-runner summary line."""
    failed = False
    passed = False
    for pattern, kind in _RUNNER_SUMMARIES:
        match = pattern.search(text)
        if not match:
            continue
        if kind == "failed_count":
            if int(match.group(1)) > 0:
                failed = True
        elif kind == "failed":
            failed = True
        elif kind == "passed":
            passed = True
    if failed:
        return 1
    if passed:
        return 0
    return None


def _extract_exit_code(tool_response) -> int | None:
    """Extract the exit code from a PostToolUse tool_response.

    Order: explicit exit_code/exitCode field, then runner-summary parsing,
    then None (unknown). Unknown never marks failure — an honest "not
    verified" beats a false FAIL that would block the completion gate.
    """
    if isinstance(tool_response, dict):
        for key in ("exit_code", "exitCode"):
            if key in tool_response:
                try:
                    return int(tool_response[key])
                except (ValueError, TypeError):
                    continue

        text_parts = [
            part
            for part in (tool_response.get("stdout"), tool_response.get("stderr"))
            if isinstance(part, str)
        ]
        if text_parts:
            return _parse_runner_summary("\n".join(text_parts))

    if isinstance(tool_response, str):
        return _parse_runner_summary(tool_response)

    return None


if __name__ == "__main__":
    main()
