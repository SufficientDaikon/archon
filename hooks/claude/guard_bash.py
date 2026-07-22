#!/usr/bin/env python3
"""PreToolUse [Bash] hook — blocks dangerous commands.

Fires on every Bash tool call. Scans the command for destructive patterns
(rm -rf /, force push main, curl|bash, etc.) and denies if found.
Must be FAST (<50ms).
"""

import json
import sys
import time
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.hooklog import write_record
from shared.scanner import scan_bash_command


def main() -> None:
    t0 = time.perf_counter()
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

    findings = scan_bash_command(command)

    if findings:
        descriptions = [f["description"] for f in findings]
        reason = f"Archon guard: blocked dangerous command — {'; '.join(descriptions)}"

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
        write_record("guard_bash", "PreToolUse", cwd, t0, decision="deny", findings=descriptions)
        print(json.dumps(output))
        sys.exit(0)
    else:
        write_record("guard_bash", "PreToolUse", cwd, t0, decision="allow")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
