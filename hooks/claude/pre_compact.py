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
from datetime import datetime, timezone
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.state import load_state, save_state


def main() -> None:
    sys.stdin.read()  # payload unused; consume to avoid broken pipe

    state = load_state()
    state["session"]["last_compacted"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(json.dumps({}))


if __name__ == "__main__":
    main()
