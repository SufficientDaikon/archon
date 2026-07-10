"""Per-project session state read/write — single source of truth for hooks.

Every hook imports this module. State lives at
``<ARCHON_HOME>/projects/<slug>/state.json`` where the slug is derived from
the project path — two concurrent Claude Code sessions in different repos get
independent state (gcloud named-configurations style), so one project's
failing tests can never trip another project's completion gate.

Handles first-run (no file), corrupt state, and version migration.
Atomic writes via temp+rename.
"""

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_FILE = "state.json"
STATE_VERSION = "1.0.0"

_SLUG_CHARS = re.compile(r"[^a-z0-9-]+")


def _get_archon_home() -> Path:
    """Resolve ~/.archon/ — standalone, no package imports needed."""
    env = os.environ.get("ARCHON_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".archon"


def project_slug(cwd: str | None = None) -> str:
    """Deterministic, human-readable project identifier.

    sanitized-basename[:40] + "-" + sha1(resolved path)[:8]. Pure function of
    the path; both hooks and tests must resolve() so symlinked tempdirs
    (macOS /tmp) hash identically.
    """
    path = Path(cwd) if cwd else Path.cwd()
    resolved = path.resolve()
    base = _SLUG_CHARS.sub("-", resolved.name.lower()).strip("-") or "project"
    digest = hashlib.sha1(str(resolved).encode("utf-8")).hexdigest()[:8]
    return f"{base[:40]}-{digest}"


def get_state_path(cwd: str | None = None) -> Path:
    return _get_archon_home() / "projects" / project_slug(cwd) / STATE_FILE


def load_state(cwd: str | None = None) -> dict[str, Any]:
    """Load the project's state; return empty scaffold if missing or corrupt."""
    path = get_state_path(cwd)
    if not path.exists():
        return _empty_state()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != STATE_VERSION:
            data = _migrate_state(data)
        return data
    except (json.JSONDecodeError, OSError):
        return _empty_state()


def save_state(state: dict[str, Any], cwd: str | None = None) -> Path:
    """Persist the project's state atomically (temp file + rename)."""
    path = get_state_path(cwd)
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
            "todos_pending_titles": [],
            "subagent_runs": [],
            "gate_blocks": 0,
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


def update_session_field(key: str, value: Any, cwd: str | None = None) -> None:
    """Load, update one session field, save."""
    state = load_state(cwd)
    state["session"][key] = value
    save_state(state, cwd)


def append_modified_file(filepath: str, cwd: str | None = None) -> None:
    """Track a modified file without duplicates."""
    state = load_state(cwd)
    files = state["session"]["files_modified"]
    if filepath not in files:
        files.append(filepath)
    save_state(state, cwd)


def new_session_id() -> str:
    """Generate a short session identifier."""
    return uuid.uuid4().hex[:12]


def archive_session(state: dict) -> None:
    """Move the current session summary into history. Keep last 3.

    Idempotent — callers (session_boot, completion_gate, session_end) may all
    attempt archival; the dedup check ensures one history entry per session.
    """
    session = state.get("session", {})
    if not session.get("id"):
        return

    summary = {
        "id": session.get("id", ""),
        "started": session.get("started", ""),
        "files_modified_count": len(session.get("files_modified", [])),
        "tests_passed": session.get("tests_passed"),
        "build_passed": session.get("build_passed"),
        "complexity_tier": session.get("complexity_tier", ""),
        "todos_completed": session.get("todos_completed", 0),
        "todos_total": session.get("todos_total", 0),
    }

    history = state.setdefault("history", {"last_sessions": [], "unfinished_work": []})
    existing_ids = [s.get("id") for s in history.get("last_sessions", [])]
    if summary["id"] in existing_ids:
        return
    history["last_sessions"].insert(0, summary)
    history["last_sessions"] = history["last_sessions"][:3]

    # Track unfinished work so the next session boot can surface it
    if summary["todos_total"] > 0 and summary["todos_completed"] < summary["todos_total"]:
        pending = session.get("todos_pending_titles", [])
        detail = f" ({'; '.join(pending[:3])})" if pending else ""
        unfinished = (
            f"Session {summary['id']}: "
            f"{summary['todos_total'] - summary['todos_completed']} incomplete tasks{detail}"
        )
        history.setdefault("unfinished_work", []).insert(0, unfinished)
        history["unfinished_work"] = history["unfinished_work"][:5]


# Self-test: create scaffold if run directly
if __name__ == "__main__":
    state = load_state()
    path = save_state(state)
    print(json.dumps({"status": "ok", "state_path": str(path)}, indent=2))
