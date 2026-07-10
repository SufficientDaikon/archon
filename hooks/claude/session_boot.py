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

from shared.state import archive_session, load_state, new_session_id, save_state

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
    source = input_data.get("source", "startup")
    state = load_state()

    if source in ("resume", "compact"):
        # Mid-session continuation: the session's files_modified / tests_passed /
        # todos are live gate state — wiping them here would silently disarm the
        # completion gate. Preserve everything and re-inject a resume snapshot.
        state["git"] = get_git_summary(cwd)
        save_state(state)
        context = build_resume_context(state, source)
    else:
        # Fresh session (startup or /clear): archive the previous one and reset.
        archive_session(state)
        state["project"] = detect_project(cwd)
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
            "todos_pending_titles": [],
            "subagent_runs": [],
            "gate_blocks": 0,
        }
        state["git"] = get_git_summary(cwd)
        save_state(state)
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
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3,
        )
        if branch.returncode == 0:
            result["branch"] = branch.stdout.strip()

        # Uncommitted changes count
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd, capture_output=True, text=True, timeout=3
        )
        if status.returncode == 0:
            lines = [ln for ln in status.stdout.strip().splitlines() if ln.strip()]
            result["uncommitted_changes"] = len(lines)

        # Last commit SHA
        log = subprocess.run(
            ["git", "log", "-1", "--format=%h"], cwd=cwd, capture_output=True, text=True, timeout=3
        )
        if log.returncode == 0:
            result["last_commit"] = log.stdout.strip()

        # Unpushed commits
        unpushed = subprocess.run(
            ["git", "rev-list", "--count", "@{upstream}..HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3,
        )
        if unpushed.returncode == 0:
            result["unpushed_commits"] = int(unpushed.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    return result


def build_resume_context(state: dict, source: str) -> str:
    """Build the mid-session re-injection block for resume/compact.

    After compaction the model loses its working memory of what it touched;
    this snapshot restores the load-bearing facts from disk state.
    """
    session = state.get("session", {})
    git = state.get("git", {})

    def fmt(value):
        return {True: "pass", False: "FAIL", None: "unknown"}.get(value, str(value))

    lines = [f'<archon-resume source="{source}">']
    lines.append(
        f'  <session tier="{session.get("complexity_tier", "")}" '
        f'tests="{fmt(session.get("tests_passed"))}" '
        f'build="{fmt(session.get("build_passed"))}" '
        f'todos="{session.get("todos_completed", 0)}/{session.get("todos_total", 0)}" />'
    )

    files = session.get("files_modified", [])
    if files:
        lines.append(f'  <files-modified count="{len(files)}">')
        for f in files[-10:]:
            lines.append(f"    <file>{f}</file>")
        lines.append("  </files-modified>")

    pending = session.get("todos_pending_titles", [])
    if pending:
        lines.append("  <pending-todos>")
        for title in pending[:5]:
            lines.append(f"    <todo>{title}</todo>")
        lines.append("  </pending-todos>")

    lines.append(
        f'  <git branch="{git.get("branch", "")}" uncommitted="{git.get("uncommitted_changes", 0)}" />'
    )
    lines.append("</archon-resume>")
    return "\n".join(lines)


def build_boot_context(state: dict) -> str:
    """Build compressed XML context for additionalContext."""
    project = state["project"]
    git = state["git"]
    history = state.get("history", {})
    last_sessions = history.get("last_sessions", [])
    unfinished = history.get("unfinished_work", [])

    lines = ["<archon-boot>"]

    # Project
    lines.append(
        f'  <project type="{project["type"]}" name="{project["name"]}" framework="{project["framework"]}" />'
    )

    # Git
    lines.append(
        f'  <git branch="{git["branch"]}" uncommitted="{git["uncommitted_changes"]}" unpushed="{git["unpushed_commits"]}" last-commit="{git["last_commit"]}" />'
    )

    # Previous sessions
    if last_sessions:
        prev = last_sessions[0]
        lines.append(
            f'  <previous-session files="{prev["files_modified_count"]}" tests="{prev["tests_passed"]}" tier="{prev["complexity_tier"]}" />'
        )

    # Unfinished work
    if unfinished:
        lines.append(f'  <unfinished count="{len(unfinished)}">')
        for item in unfinished[:3]:
            lines.append(f"    <task>{item}</task>")
        lines.append("  </unfinished>")

    lines.append("</archon-boot>")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
