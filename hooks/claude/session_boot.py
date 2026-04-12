#!/usr/bin/env python3
"""SessionStart hook — boots Archon runtime, injects project context.

Fires once per session. Detects project type, loads previous session state,
captures git status, and injects compressed context into Claude's window.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOOK_DIR = Path(__file__).parent
sys.path.insert(0, str(HOOK_DIR))

from shared.state import load_state, save_state, new_session_id

# Project detection markers -> (type, framework check)
PROJECT_MARKERS = {
    "pyproject.toml": ("python", None),
    "setup.py": ("python", None),
    "requirements.txt": ("python", None),
    "package.json": ("node", "_detect_node_framework"),
    "Cargo.toml": ("rust", None),
    "go.mod": ("go", None),
    "archon.yaml": ("archon", None),
    "project.godot": ("godot", None),
}

NODE_FRAMEWORKS = {
    "next": "nextjs",
    "astro": "astro",
    "react": "react",
    "vue": "vue",
    "svelte": "svelte",
    "express": "express",
    "fastify": "fastify",
    "nuxt": "nuxt",
}


def main() -> None:
    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    cwd = input_data.get("cwd", str(Path.cwd()))
    state = load_state()

    # Archive previous session if it exists
    archive_previous_session(state)

    # Detect project
    project = detect_project(cwd)
    state["project"] = project

    # New session
    state["session"] = {
        "id": new_session_id(),
        "started": datetime.now(timezone.utc).isoformat(),
        "files_modified": [],
        "tests_passed": None,
        "build_passed": None,
        "complexity_tier": "",
        "active_skills": [],
        "todos_completed": 0,
        "todos_total": 0,
    }

    # Git info
    state["git"] = get_git_summary(cwd)

    save_state(state)

    # Build context
    context = build_boot_context(state)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    print(json.dumps(output))


def detect_project(cwd: str) -> dict:
    """Detect project type from filesystem markers."""
    cwd_path = Path(cwd)
    result = {"path": cwd, "type": "", "name": cwd_path.name, "framework": ""}

    for marker, (ptype, framework_fn) in PROJECT_MARKERS.items():
        if (cwd_path / marker).exists():
            result["type"] = ptype
            if framework_fn and framework_fn == "_detect_node_framework":
                result["framework"] = _detect_node_framework(cwd_path)
            break

    return result


def _detect_node_framework(cwd_path: Path) -> str:
    """Check package.json deps for known frameworks."""
    try:
        pkg = json.loads((cwd_path / "package.json").read_text(encoding="utf-8"))
        all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        for dep_name, framework_name in NODE_FRAMEWORKS.items():
            if dep_name in all_deps:
                return framework_name
    except (json.JSONDecodeError, OSError):
        pass
    return "node"


def get_git_summary(cwd: str) -> dict:
    """Fast git status via subprocess."""
    result = {"branch": "", "uncommitted_changes": 0, "last_commit": "", "unpushed_commits": 0}

    try:
        # Branch name
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=3
        )
        if branch.returncode == 0:
            result["branch"] = branch.stdout.strip()

        # Uncommitted changes count
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd, capture_output=True, text=True, timeout=3
        )
        if status.returncode == 0:
            lines = [l for l in status.stdout.strip().splitlines() if l.strip()]
            result["uncommitted_changes"] = len(lines)

        # Last commit SHA
        log = subprocess.run(
            ["git", "log", "-1", "--format=%h"],
            cwd=cwd, capture_output=True, text=True, timeout=3
        )
        if log.returncode == 0:
            result["last_commit"] = log.stdout.strip()

        # Unpushed commits
        unpushed = subprocess.run(
            ["git", "rev-list", "--count", "@{upstream}..HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=3
        )
        if unpushed.returncode == 0:
            result["unpushed_commits"] = int(unpushed.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    return result


def archive_previous_session(state: dict) -> None:
    """Move current session to history. Keep last 3. Dedup prevents double-archiving."""
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
    # Dedup check — completion_gate may have already archived this session
    existing_ids = [s.get("id") for s in history.get("last_sessions", [])]
    if summary["id"] in existing_ids:
        return
    history["last_sessions"].insert(0, summary)
    history["last_sessions"] = history["last_sessions"][:3]

    # Track unfinished work
    if summary["todos_total"] > 0 and summary["todos_completed"] < summary["todos_total"]:
        unfinished = f"Session {summary['id']}: {summary['todos_total'] - summary['todos_completed']} incomplete tasks"
        history.setdefault("unfinished_work", []).insert(0, unfinished)
        history["unfinished_work"] = history["unfinished_work"][:5]


def build_boot_context(state: dict) -> str:
    """Build compressed XML context for additionalContext."""
    project = state["project"]
    git = state["git"]
    history = state.get("history", {})
    last_sessions = history.get("last_sessions", [])
    unfinished = history.get("unfinished_work", [])

    lines = ['<archon-boot>']

    # Project
    lines.append(f'  <project type="{project["type"]}" name="{project["name"]}" framework="{project["framework"]}" />')

    # Git
    lines.append(f'  <git branch="{git["branch"]}" uncommitted="{git["uncommitted_changes"]}" unpushed="{git["unpushed_commits"]}" last-commit="{git["last_commit"]}" />')

    # Previous sessions
    if last_sessions:
        prev = last_sessions[0]
        lines.append(f'  <previous-session files="{prev["files_modified_count"]}" tests="{prev["tests_passed"]}" tier="{prev["complexity_tier"]}" />')

    # Unfinished work
    if unfinished:
        lines.append(f'  <unfinished count="{len(unfinished)}">')
        for item in unfinished[:3]:
            lines.append(f'    <task>{item}</task>')
        lines.append('  </unfinished>')

    lines.append('</archon-boot>')
    return "\n".join(lines)


if __name__ == "__main__":
    main()
