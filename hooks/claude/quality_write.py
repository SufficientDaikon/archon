#!/usr/bin/env python3
"""PostToolUse [Write|Edit|NotebookEdit] hook — tracks file modifications in state.

Fires after every successful Write/Edit/NotebookEdit. Records the modified
file path in archon-state.json for the completion gate to reference.
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.state import append_modified_file


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    tool_input = input_data.get("tool_input", {})
    # Handle both file_path (Write/Edit) and notebook_path (NotebookEdit)
    file_path = tool_input.get("file_path", "") or tool_input.get("notebook_path", "")

    if file_path:
        append_modified_file(file_path)

    # No context injection — pure state tracking
    print(json.dumps({}))


if __name__ == "__main__":
    main()
