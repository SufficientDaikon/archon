#!/usr/bin/env python3
"""PreCompact hook — guarantees state freshness before compaction.

Fires before Claude Code compacts the conversation. Session state (files
modified, test status, todos) is already maintained incrementally by the
other hooks; this hook re-persists it with a compaction marker so the
SessionStart(source="compact") re-injection in session_boot.py is accurate.
PreCompact output is not consumed — the re-injection happens at SessionStart.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.hooklog import write_record
from shared.state import load_state, save_state


def main() -> None:
    t0 = time.perf_counter()
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    cwd = input_data.get("cwd")
    state = load_state(cwd)
    state["session"]["last_compacted"] = datetime.now(timezone.utc).isoformat()
    save_state(state, cwd)

    write_record("pre_compact", "PreCompact", cwd, t0)
    print(json.dumps({}))


if __name__ == "__main__":
    main()
