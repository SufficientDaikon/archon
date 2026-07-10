"""Live hook diagnostics — gcloud's ``info --run-diagnostics`` for Archon.

Drives every hook in ``hooks/claude/`` as a real subprocess with synthetic
payloads against a throwaway ARCHON_HOME, and checks the load-bearing
behaviors (the same contracts tests/test_claude_hooks.py pins, condensed to
one PASS/FAIL line each). Used by ``archon doctor --hooks``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from archon.utils.paths import get_archon_root

Expect = Callable[[subprocess.CompletedProcess, Path, str], tuple[bool, str]]


@dataclass
class HookCheck:
    name: str
    script: str
    payload: dict[str, Any]
    expect: Expect
    seed_session: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


def _stdout_json(result: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        return {}


def _expect_context(needle: str, absent: str = "") -> Expect:
    def check(result, home, cwd):
        context = _stdout_json(result).get("hookSpecificOutput", {}).get("additionalContext", "")
        if needle not in context:
            return False, f"missing {needle!r} in injected context"
        if absent and absent in context:
            return False, f"unexpected {absent!r} in injected context"
        return True, ""

    return check


def _expect_decision(decision: str | None) -> Expect:
    def check(result, home, cwd):
        got = _stdout_json(result).get("hookSpecificOutput", {}).get("permissionDecision")
        if got != decision:
            return False, f"permissionDecision={got!r}, expected {decision!r}"
        return True, ""

    return check


def _expect_exit(code: int, stderr_contains: str = "") -> Expect:
    def check(result, home, cwd):
        if result.returncode != code:
            return False, f"exit={result.returncode}, expected {code}"
        if stderr_contains and stderr_contains not in result.stderr:
            return False, f"stderr missing {stderr_contains!r}"
        return True, ""

    return check


def _expect_state(probe: Callable[[dict], bool], describe: str) -> Expect:
    def check(result, home, cwd):
        from archon.core.hooks_bridge import load_shared

        state_mod = load_shared("state")
        path = home / "projects" / state_mod.project_slug(cwd) / "state.json"
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return False, f"state unreadable: {exc}"
        if not probe(state):
            return False, describe
        return True, ""

    return check


CHECKS: list[HookCheck] = [
    HookCheck(
        "session_boot: startup injects <archon-boot>",
        "session_boot.py",
        {"source": "startup"},
        _expect_context("<archon-boot>"),
    ),
    HookCheck(
        "session_boot: compact preserves session state",
        "session_boot.py",
        {"source": "compact"},
        _expect_state(
            lambda s: s["session"].get("files_modified") == ["x.py"],
            "compact wiped files_modified — gate disarmed",
        ),
        seed_session={"files_modified": ["x.py"]},
    ),
    HookCheck(
        "prompt_router: trivial prompt stays quiet",
        "prompt_router.py",
        {"prompt": "hi"},
        _expect_context('tier="TRIVIAL"', absent="metacognition>"),
    ),
    HookCheck(
        "prompt_router: complex prompt gets escape hatch",
        "prompt_router.py",
        {
            "prompt": (
                "refactor the authentication pipeline architecture end to end and migrate "
                "the distributed session store, then rewrite the authorization middleware "
                "for the production deployment with full test coverage across services"
            )
        },
        _expect_context("ESCAPE HATCH"),
    ),
    HookCheck(
        "guard_bash: denies force push to main",
        "guard_bash.py",
        {"tool_input": {"command": "git push origin main " + "--" + "force"}},
        _expect_decision("deny"),
    ),
    HookCheck(
        "guard_bash: allows feature-branch reset",
        "guard_bash.py",
        {"tool_input": {"command": "git reset " + "--hard origin/feature-x"}},
        _expect_decision(None),
    ),
    HookCheck(
        "guard_write: denies hardcoded secret",
        "guard_write.py",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/app/config.py",
                "content": 'key = "sk-' + 'ant-abc123def456ghi789jkl"',
            },
        },
        _expect_decision("deny"),
    ),
    HookCheck(
        "quality_bash: '0 errors' output stays unknown",
        "quality_bash.py",
        {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"stdout": "0 errors, improved error handling"},
        },
        _expect_state(
            lambda s: s["session"].get("tests_passed") is None,
            "tests_passed flipped on the word 'error' — false-positive regression",
        ),
    ),
    HookCheck(
        "quality_bash: exit_code 1 marks tests failed",
        "quality_bash.py",
        {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"exit_code": 1},
        },
        _expect_state(
            lambda s: s["session"].get("tests_passed") is False,
            "tests_passed not recorded from exit_code",
        ),
    ),
    HookCheck(
        "quality_write: tracks modified file",
        "quality_write.py",
        {"tool_input": {"file_path": "/app/thing.py"}},
        _expect_state(
            lambda s: "/app/thing.py" in s["session"].get("files_modified", []),
            "modified file not tracked",
        ),
    ),
    HookCheck(
        "completion_gate: blocks on failed tests (exit 2)",
        "completion_gate.py",
        {},
        _expect_exit(2, stderr_contains="quality checks failed"),
        seed_session={"files_modified": ["a.py"], "tests_passed": False},
    ),
    HookCheck(
        "completion_gate: respects stop_hook_active",
        "completion_gate.py",
        {"stop_hook_active": True},
        _expect_exit(0),
        seed_session={"files_modified": ["a.py"], "tests_passed": False},
    ),
    HookCheck(
        "completion_gate: silent pass when tests pass",
        "completion_gate.py",
        {},
        _expect_exit(0),
        seed_session={"files_modified": ["a.py"], "tests_passed": True},
    ),
    HookCheck(
        "todo_track: records todo counts",
        "todo_track.py",
        {
            "tool_input": {
                "todos": [
                    {"content": "a", "status": "completed"},
                    {"content": "b", "status": "pending"},
                ]
            }
        },
        _expect_state(
            lambda s: (
                s["session"].get("todos_total") == 2 and s["session"].get("todos_completed") == 1
            ),
            "todo counts not recorded",
        ),
    ),
    HookCheck(
        "agent_context: subagent_type payload honored",
        "agent_context.py",
        {"hook_event_name": "SubagentStart", "subagent_type": "Explore"},
        _expect_context('role="explore"'),
    ),
    HookCheck(
        "session_end: archives the session",
        "session_end.py",
        {"reason": "exit"},
        _expect_state(
            lambda s: bool(s.get("history", {}).get("last_sessions")),
            "session not archived to history",
        ),
        seed_session={"files_modified": ["a.py"]},
    ),
    HookCheck(
        "pre_compact: stamps compaction marker",
        "pre_compact.py",
        {},
        _expect_state(
            lambda s: bool(s["session"].get("last_compacted")),
            "last_compacted not stamped",
        ),
    ),
]


def run_diagnostics(hooks_dir: Path | None = None) -> list[CheckResult]:
    """Drive every check against a throwaway ARCHON_HOME. Returns results."""
    if hooks_dir is None:
        hooks_dir = Path(get_archon_root()) / "hooks" / "claude"
    if not hooks_dir.is_dir():
        return [CheckResult("hooks directory exists", False, f"not found: {hooks_dir}")]

    from archon.core.hooks_bridge import load_shared

    state_mod = load_shared("state")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        cwd_dir = Path(tmp) / "project"
        cwd_dir.mkdir(parents=True)
        cwd = str(cwd_dir)
        env = {**os.environ, "ARCHON_HOME": str(home)}

        def drive(script: str, payload: dict) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(hooks_dir / script)],
                input=json.dumps({"cwd": cwd, **payload}),
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )

        for check in CHECKS:
            # Fresh session per check so seeds don't leak between checks
            drive("session_boot.py", {"source": "startup"})
            if check.seed_session:
                state_path = home / "projects" / state_mod.project_slug(cwd) / "state.json"
                state = json.loads(state_path.read_text(encoding="utf-8"))
                state["session"].update(check.seed_session)
                state_path.write_text(json.dumps(state), encoding="utf-8")

            try:
                result = drive(check.script, check.payload)
                passed, detail = check.expect(result, home, cwd)
            except Exception as exc:  # a crashed check is a failed check
                passed, detail = False, f"exception: {exc}"
            results.append(CheckResult(check.name, passed, detail))

    return results
