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
    state = load_state()

    if is_test_command(command):
        state["session"]["tests_passed"] = passed
        updated = True

    if is_build_command(command):
        state["session"]["build_passed"] = passed
        updated = True

    if updated:
        save_state(state)

    print(json.dumps({}))


# Case-insensitive failure indicators
_FAIL_PATTERN = re.compile(r'\b(fail|failed|error)\b', re.I)


def _extract_exit_code(tool_response) -> int | None:
    """Try to extract exit code from PostToolUse tool_response.

    Returns int exit code if determinable, None if unknown.
    Checks both snake_case and camelCase field names.
    """
    if isinstance(tool_response, dict):
        # Check both naming conventions
        for key in ("exit_code", "exitCode"):
            if key in tool_response:
                try:
                    return int(tool_response[key])
                except (ValueError, TypeError):
                    continue

        # Fallback: case-insensitive string matching on stdout
        stdout = tool_response.get("stdout", "")
        if isinstance(stdout, str) and _FAIL_PATTERN.search(stdout):
            return 1

    if isinstance(tool_response, str) and _FAIL_PATTERN.search(tool_response):
        return 1

    # Unknown — cannot determine pass/fail
    return None


if __name__ == "__main__":
    main()
