#!/usr/bin/env python3
"""PreToolUse [Write|Edit|NotebookEdit] hook — scans file content for secrets.

Fires on every Write/Edit/NotebookEdit tool call. Scans content being written
for API keys, tokens, private keys, and other secrets. Denies if found.
Must be FAST (<100ms).
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.scanner import scan_for_secrets


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    tool_input = input_data.get("tool_input", {})
    tool_name = input_data.get("tool_name", "")

    # Extract content to scan based on tool type
    content = ""
    file_path = tool_input.get("file_path", "")

    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "")
    elif tool_name == "NotebookEdit":
        content = tool_input.get("new_source", "")
        file_path = file_path or tool_input.get("notebook_path", "")

    if not content:
        print(json.dumps({}))
        return

    findings = scan_for_secrets(content, file_path)

    if findings:
        secret_types = list({f["type"] for f in findings})
        reason = f"Archon guard: blocked — detected {', '.join(secret_types)} in {file_path or 'file content'}. Use environment variables instead."

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
