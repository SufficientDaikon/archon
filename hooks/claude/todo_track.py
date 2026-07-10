#!/usr/bin/env python3
"""PostToolUse [TodoWrite] hook — tracks todo progress in session state.

Fires after every TodoWrite call. Records total/completed counts and the
first few pending titles so session_boot can surface unfinished work in the
next session and after compaction.
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

    todos = input_data.get("tool_input", {}).get("todos", [])
    if not isinstance(todos, list):
        print(json.dumps({}))
        return

    completed = sum(1 for t in todos if isinstance(t, dict) and t.get("status") == "completed")
    pending_titles = [
        str(t.get("content") or t.get("subject") or "")
        for t in todos
        if isinstance(t, dict) and t.get("status") != "completed"
    ]

    state = load_state()
    session = state["session"]
    session["todos_total"] = len(todos)
    session["todos_completed"] = completed
    session["todos_pending_titles"] = [title for title in pending_titles if title][:5]
    save_state(state)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
