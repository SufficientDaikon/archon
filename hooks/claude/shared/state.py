"""archon-state.json read/write — single source of truth for Claude Code hooks.

Every hook imports this module. Handles first-run (no file),
corrupt state, and version migration. Atomic writes via temp+rename.
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_FILE = "archon-state.json"
STATE_VERSION = "1.0.0"


def _get_archon_home() -> Path:
    """Resolve ~/.archon/ — standalone, no package imports needed."""
    env = os.environ.get("ARCHON_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".archon"


def get_state_path() -> Path:
    return _get_archon_home() / STATE_FILE


def load_state() -> dict[str, Any]:
    """Load state; return empty scaffold if missing or corrupt."""
    path = get_state_path()
    if not path.exists():
        return _empty_state()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != STATE_VERSION:
            data = _migrate_state(data)
        return data
    except (json.JSONDecodeError, OSError):
        return _empty_state()


def save_state(state: dict[str, Any]) -> Path:
    """Persist state atomically (temp file + rename)."""
    path = get_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    tmp.replace(path)
    return path


def _empty_state() -> dict[str, Any]:
    """Scaffold for first-run. Every field present so hooks never KeyError."""
    return {
        "version": STATE_VERSION,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "project": {
            "path": "",
            "type": "",
            "name": "",
            "framework": "",
        },
        "session": {
            "id": "",
            "started": "",
            "files_modified": [],
            "tests_passed": None,
            "build_passed": None,
            "complexity_tier": "",
            "active_skills": [],
            "todos_completed": 0,
            "todos_total": 0,
        },
        "history": {
            "last_sessions": [],
            "unfinished_work": [],
        },
        "git": {
            "branch": "",
            "uncommitted_changes": 0,
            "last_commit": "",
            "unpushed_commits": 0,
        },
    }


def _migrate_state(data: dict) -> dict:
    """Upgrade old state versions. Fill missing keys from scaffold."""
    scaffold = _empty_state()
    for section_key, section_val in scaffold.items():
        if section_key not in data:
            data[section_key] = section_val
        elif isinstance(section_val, dict):
            for k, v in section_val.items():
                if k not in data[section_key]:
                    data[section_key][k] = v
    data["version"] = STATE_VERSION
    return data


def update_session_field(key: str, value: Any) -> None:
    """Load, update one session field, save."""
    state = load_state()
    state["session"][key] = value
    save_state(state)


def append_modified_file(filepath: str) -> None:
    """Track a modified file without duplicates."""
    state = load_state()
    files = state["session"]["files_modified"]
    if filepath not in files:
        files.append(filepath)
    save_state(state)


def new_session_id() -> str:
    """Generate a short session identifier."""
    return uuid.uuid4().hex[:12]


# Self-test: create scaffold if run directly
if __name__ == "__main__":
    state = load_state()
    path = save_state(state)
    print(json.dumps({"status": "ok", "state_path": str(path)}, indent=2))
