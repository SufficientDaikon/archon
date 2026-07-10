#!/usr/bin/env python3
"""SessionEnd hook — final state archival.

Fires when the session ends (including /clear and terminal exit, which the
Stop hook does not cover). Archives the session into history and persists
state. No output is consumed for SessionEnd — this is bookkeeping only.
"""

import json
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.state import archive_session, load_state, save_state


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    cwd = input_data.get("cwd")
    state = load_state(cwd)
    if state["session"].get("files_modified") or state["session"].get("todos_total"):
        archive_session(state)
    state["session"]["end_reason"] = input_data.get("reason", "")
    save_state(state, cwd)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
