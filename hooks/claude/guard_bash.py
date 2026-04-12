#!/usr/bin/env python3
"""PreToolUse [Bash] hook — blocks dangerous commands.

Fires on every Bash tool call. Scans the command for destructive patterns
(rm -rf /, force push main, curl|bash, etc.) and denies if found.
Must be FAST (<50ms).
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.scanner import scan_bash_command


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
        print(json.dumps(output))
        sys.exit(0)
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
