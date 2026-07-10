"""Contract tests for the Claude Code hooks in hooks/claude/.

Each hook is executed as a real subprocess with a synthetic stdin payload and
an isolated ARCHON_HOME, asserting on exit code, stdout JSON, and state-file
mutations — the same contract Claude Code holds them to.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ARCHON_ROOT = Path(__file__).parent.parent
HOOKS_DIR = ARCHON_ROOT / "hooks" / "claude"


def run_hook(
    name: str, payload: dict, archon_home: Path, extra_env: dict | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOKS_DIR / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "ARCHON_HOME": str(archon_home), **(extra_env or {})},
    )


def read_state(archon_home: Path) -> dict:
    return json.loads((archon_home / "archon-state.json").read_text(encoding="utf-8"))


def write_state(archon_home: Path, mutate) -> None:
    """Seed a state file: run session_boot to scaffold, then apply mutate(state)."""
    state = read_state(archon_home)
    mutate(state)
    (archon_home / "archon-state.json").write_text(json.dumps(state), encoding="utf-8")


@pytest.fixture
def home(tmp_path):
    """Isolated ARCHON_HOME with a booted session."""
    boot = run_hook("session_boot.py", {"cwd": str(ARCHON_ROOT)}, tmp_path)
    assert boot.returncode == 0
    return tmp_path


class TestSessionBoot:
    def test_startup_creates_session(self, tmp_path):
        result = run_hook("session_boot.py", {"cwd": str(ARCHON_ROOT)}, tmp_path)
        assert result.returncode == 0
        out = json.loads(result.stdout)
        assert "<archon-boot>" in out["hookSpecificOutput"]["additionalContext"]
        assert read_state(tmp_path)["session"]["id"]

    def test_startup_resets_session(self, home):
        write_state(
            home, lambda s: s["session"].update(files_modified=["a.py"], tests_passed=False)
        )
        run_hook("session_boot.py", {"cwd": str(ARCHON_ROOT), "source": "startup"}, home)
        session = read_state(home)["session"]
        assert session["files_modified"] == []
        assert session["tests_passed"] is None

    def test_compact_preserves_session(self, home):
        """Regression: compaction must NOT wipe gate state mid-session."""
        write_state(
            home,
            lambda s: s["session"].update(
                files_modified=["a.py", "b.py"],
                tests_passed=False,
                complexity_tier="COMPLEX",
                todos_total=3,
                todos_completed=1,
                todos_pending_titles=["finish x"],
            ),
        )
        result = run_hook("session_boot.py", {"cwd": str(ARCHON_ROOT), "source": "compact"}, home)
        session = read_state(home)["session"]
        assert session["files_modified"] == ["a.py", "b.py"]
        assert session["tests_passed"] is False

        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert "<archon-resume" in context
        assert "a.py" in context
        assert "finish x" in context
        assert 'tests="FAIL"' in context

    def test_resume_preserves_session(self, home):
        write_state(home, lambda s: s["session"].update(files_modified=["a.py"]))
        run_hook("session_boot.py", {"cwd": str(ARCHON_ROOT), "source": "resume"}, home)
        assert read_state(home)["session"]["files_modified"] == ["a.py"]


class TestPromptRouter:
    def test_trivial_prompt_no_synapse_noise(self, home):
        result = run_hook("prompt_router.py", {"prompt": "hi"}, home)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert 'tier="TRIVIAL"' in context
        assert "metacognition>" not in context

    def test_moderate_injects_discipline(self, home):
        prompt = (
            "refactor the payment reconciliation module so retries are idempotent, "
            "update the ledger writer accordingly, and make sure error paths roll "
            "back partial writes cleanly across both services involved here today"
        )
        result = run_hook("prompt_router.py", {"prompt": prompt}, home)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert "NO UNVERIFIED CLAIMS" in context
        assert "PLAN before executing" in context

    def test_log_stuffed_prompt_not_expert(self, home):
        logs = "\n".join(f"2026-01-01T00:00:{i:02d} ERROR x{i}" for i in range(200))
        result = run_hook("prompt_router.py", {"prompt": f"fix this\n```\n{logs}\n```"}, home)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert 'tier="EXPERT"' not in context

    def test_updates_state_tier(self, home):
        run_hook("prompt_router.py", {"prompt": "hello there friend"}, home)
        assert read_state(home)["session"]["complexity_tier"] == "TRIVIAL"

    def test_empty_prompt_passthrough(self, home):
        result = run_hook("prompt_router.py", {"prompt": ""}, home)
        assert json.loads(result.stdout) == {}


class TestGuardBash:
    def deny_reason(self, result):
        out = json.loads(result.stdout)
        hso = out.get("hookSpecificOutput", {})
        return hso.get("permissionDecision"), hso.get("permissionDecisionReason", "")

    def test_blocks_rm_root(self, home):
        result = run_hook("guard_bash.py", {"tool_input": {"command": "rm -rf " + "/"}}, home)
        decision, _ = self.deny_reason(result)
        assert decision == "deny"

    def test_blocks_force_push_flag_after_branch(self, home):
        cmd = "git push origin main --force"
        result = run_hook("guard_bash.py", {"tool_input": {"command": cmd}}, home)
        decision, reason = self.deny_reason(result)
        assert decision == "deny"
        assert "force push" in reason

    def test_allows_reset_hard_feature_branch(self, home):
        cmd = "git reset --hard origin/feature-x"
        result = run_hook("guard_bash.py", {"tool_input": {"command": cmd}}, home)
        assert json.loads(result.stdout) == {}

    def test_allows_force_with_lease(self, home):
        cmd = "git push --force-with-lease origin main"
        result = run_hook("guard_bash.py", {"tool_input": {"command": cmd}}, home)
        assert json.loads(result.stdout) == {}

    def test_allows_normal_command(self, home):
        result = run_hook("guard_bash.py", {"tool_input": {"command": "ls -la"}}, home)
        assert json.loads(result.stdout) == {}


class TestGuardWrite:
    def test_blocks_secret_in_source(self, home):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/app/config.py",
                "content": 'api_key = "sk-ant-abc123def456ghi789jkl"',
            },
        }
        result = run_hook("guard_write.py", payload, home)
        out = json.loads(result.stdout)
        assert out["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_allows_fixture_file(self, home):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/app/tests/__tests__/fixture.js",
                "content": 'const key = "sk-ant-abc123def456ghi789jkl"',
            },
        }
        result = run_hook("guard_write.py", payload, home)
        assert json.loads(result.stdout) == {}

    def test_scans_multiedit_payload(self, home):
        payload = {
            "tool_name": "MultiEdit",
            "tool_input": {
                "file_path": "/app/config.py",
                "edits": [
                    {"old_string": "x", "new_string": "y"},
                    {"old_string": "a", "new_string": 'token = "ghp_' + "A" * 36 + '"'},
                ],
            },
        }
        result = run_hook("guard_write.py", payload, home)
        out = json.loads(result.stdout)
        assert out["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_scans_notebook_payload(self, home):
        payload = {
            "tool_name": "NotebookEdit",
            "tool_input": {
                "notebook_path": "/app/analysis.ipynb",
                "new_source": 'password = "hunter2hunter2"',
            },
        }
        result = run_hook("guard_write.py", payload, home)
        out = json.loads(result.stdout)
        assert out["hookSpecificOutput"]["permissionDecision"] == "deny"


class TestQualityBash:
    def test_exit_code_zero_marks_pass(self, home):
        payload = {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"exit_code": 0},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["tests_passed"] is True

    def test_exit_code_nonzero_marks_fail(self, home):
        payload = {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"exitCode": 1},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["tests_passed"] is False

    def test_zero_errors_output_is_not_failure(self, home):
        """Regression: 'error' appearing in passing output must not mark failure."""
        payload = {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"stdout": "collected 10 items\n0 errors, improved error handling"},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["tests_passed"] is None

    def test_pytest_summary_failed_count(self, home):
        payload = {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"stdout": "3 failed, 42 passed in 1.2s"},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["tests_passed"] is False

    def test_pytest_summary_all_passed(self, home):
        payload = {
            "tool_input": {"command": "pytest tests/"},
            "tool_response": {"stdout": "546 passed in 4.08s"},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["tests_passed"] is True

    def test_cargo_summary(self, home):
        payload = {
            "tool_input": {"command": "cargo test"},
            "tool_response": {"stdout": "test result: FAILED. 1 passed; 2 failed"},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["tests_passed"] is False

    def test_build_command_tracked(self, home):
        payload = {
            "tool_input": {"command": "npm run build"},
            "tool_response": {"exit_code": 0},
        }
        run_hook("quality_bash.py", payload, home)
        assert read_state(home)["session"]["build_passed"] is True


class TestCompletionGate:
    def test_no_files_passes_silently(self, home):
        result = run_hook("completion_gate.py", {}, home)
        assert result.returncode == 0
        assert json.loads(result.stdout) == {}

    def test_failed_tests_blocks_with_exit_2(self, home):
        write_state(
            home, lambda s: s["session"].update(files_modified=["app.py"], tests_passed=False)
        )
        result = run_hook("completion_gate.py", {}, home)
        assert result.returncode == 2
        assert "quality checks failed" in result.stderr
        assert read_state(home)["session"]["gate_blocks"] == 1

    def test_stop_hook_active_never_reblocks(self, home):
        write_state(
            home, lambda s: s["session"].update(files_modified=["app.py"], tests_passed=False)
        )
        result = run_hook("completion_gate.py", {"stop_hook_active": True}, home)
        assert result.returncode == 0

    def test_block_cap_downgrades_to_warning(self, home):
        write_state(
            home,
            lambda s: s["session"].update(
                files_modified=["app.py"], tests_passed=False, gate_blocks=2
            ),
        )
        result = run_hook("completion_gate.py", {}, home)
        assert result.returncode == 0
        assert "allowing stop" in result.stderr

    def test_passing_tests_no_dead_injection(self, home):
        write_state(
            home, lambda s: s["session"].update(files_modified=["app.py"], tests_passed=True)
        )
        result = run_hook("completion_gate.py", {}, home)
        assert result.returncode == 0
        # Stop hooks can't inject context — the pass path must be a bare {}
        assert json.loads(result.stdout) == {}

    def test_tests_never_ran_does_not_block(self, home):
        write_state(
            home,
            lambda s: s["session"].update(
                files_modified=["a.py", "b.py", "c.py"], tests_passed=None
            ),
        )
        result = run_hook("completion_gate.py", {}, home)
        assert result.returncode == 0


class TestConfigProperties:
    """Config-driven hook behavior (env > project > user > default)."""

    def test_gate_disabled_by_env_never_blocks(self, home):
        write_state(
            home, lambda s: s["session"].update(files_modified=["app.py"], tests_passed=False)
        )
        result = run_hook(
            "completion_gate.py", {}, home, extra_env={"ARCHON_GATE_ENABLED": "false"}
        )
        assert result.returncode == 0
        assert "disabled by gate/enabled" in result.stderr
        # disabling the gate must not lose data: session was still archived
        state = read_state(home)
        assert state["history"]["last_sessions"]

    def test_gate_max_blocks_env_caps_at_one(self, home):
        write_state(
            home,
            lambda s: s["session"].update(
                files_modified=["app.py"], tests_passed=False, gate_blocks=1
            ),
        )
        result = run_hook("completion_gate.py", {}, home, extra_env={"ARCHON_GATE_MAX_BLOCKS": "1"})
        assert result.returncode == 0
        assert "allowing stop" in result.stderr

    def test_classifier_threshold_env_shifts_tier(self, home):
        # 3-word prompt: default TRIVIAL; with trivial ceiling 1 it lands SIMPLE
        result = run_hook(
            "prompt_router.py",
            {"prompt": "hello there friend"},
            home,
            extra_env={"ARCHON_CLASSIFIER_TRIVIAL_MAX_WORDS": "1"},
        )
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert 'tier="SIMPLE"' in context

    def test_injection_master_switch_suppresses_instructions(self, home):
        prompt = (
            "refactor the payment reconciliation module so retries are idempotent, "
            "update the ledger writer accordingly, and make sure error paths roll "
            "back partial writes cleanly across both services involved here today"
        )
        result = run_hook(
            "prompt_router.py",
            {"prompt": prompt},
            home,
            extra_env={"ARCHON_INJECTION_ENABLED": "false"},
        )
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        # Route tag still emitted, instruction block suppressed
        assert "<archon-route" in context
        assert "NO UNVERIFIED CLAIMS" not in context

    def test_injection_single_synapse_toggle(self, home):
        prompt = (
            "refactor the payment reconciliation module so retries are idempotent, "
            "update the ledger writer accordingly, and make sure error paths roll "
            "back partial writes cleanly across both services involved here today"
        )
        result = run_hook(
            "prompt_router.py",
            {"prompt": prompt},
            home,
            extra_env={"ARCHON_INJECTION_ANTI_RATIONALIZATION": "false"},
        )
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert "NO UNVERIFIED CLAIMS" not in context
        assert "PLAN before executing" in context

    def test_project_config_beats_user_config(self, home, tmp_path):
        # user file says gate max_blocks 5; project file says 1 -> project wins
        (home / "config").write_text("[gate]\nmax_blocks = 5\n", encoding="utf-8")
        project_dir = tmp_path / "proj"
        (project_dir / ".archon").mkdir(parents=True)
        (project_dir / ".archon" / "config").write_text(
            "[gate]\nmax_blocks = 1\n", encoding="utf-8"
        )
        write_state(
            home,
            lambda s: s["session"].update(
                files_modified=["app.py"], tests_passed=False, gate_blocks=1
            ),
        )
        result = run_hook("completion_gate.py", {"cwd": str(project_dir)}, home)
        assert result.returncode == 0  # cap of 1 already reached
        assert "allowing stop" in result.stderr

    def test_scanner_extra_allowlist(self, home):
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/app/golden/sample.py",
                "content": 'api_key = "sk-ant-abc123def456ghi789jkl"',
            },
        }
        # Denied by default
        result = run_hook("guard_write.py", payload, home)
        assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
        # Allowed when the path matches the extra allowlist
        result = run_hook(
            "guard_write.py",
            payload,
            home,
            extra_env={"ARCHON_SCANNER_EXTRA_ALLOWLIST": r"/golden/"},
        )
        assert json.loads(result.stdout) == {}


class TestTodoTrack:
    def test_counts_and_pending_titles(self, home):
        payload = {
            "tool_input": {
                "todos": [
                    {"content": "write parser", "status": "completed"},
                    {"content": "add tests", "status": "in_progress"},
                    {"content": "update docs", "status": "pending"},
                ]
            }
        }
        run_hook("todo_track.py", payload, home)
        session = read_state(home)["session"]
        assert session["todos_total"] == 3
        assert session["todos_completed"] == 1
        assert session["todos_pending_titles"] == ["add tests", "update docs"]

    def test_malformed_payload_is_noop(self, home):
        result = run_hook("todo_track.py", {"tool_input": {"todos": "garbage"}}, home)
        assert result.returncode == 0
        assert json.loads(result.stdout) == {}


class TestAgentContext:
    def test_subagent_type_field_honored(self, home):
        result = run_hook(
            "agent_context.py",
            {"hook_event_name": "SubagentStart", "subagent_type": "Explore"},
            home,
        )
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert 'role="explore"' in context

    def test_unknown_type_defaults_to_code(self, home):
        result = run_hook(
            "agent_context.py",
            {"hook_event_name": "SubagentStart", "subagent_type": "custom-agent"},
            home,
        )
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert 'role="code"' in context

    def test_subagent_stop_records_run(self, home):
        run_hook(
            "agent_context.py",
            {"hook_event_name": "SubagentStop", "subagent_type": "Explore"},
            home,
        )
        runs = read_state(home)["session"]["subagent_runs"]
        assert runs and runs[-1]["type"] == "Explore"


class TestSessionEnd:
    def test_archives_active_session(self, home):
        write_state(
            home,
            lambda s: s["session"].update(
                files_modified=["app.py"],
                todos_total=2,
                todos_completed=1,
                todos_pending_titles=["finish y"],
            ),
        )
        session_id = read_state(home)["session"]["id"]
        result = run_hook("session_end.py", {"reason": "exit"}, home)
        assert result.returncode == 0
        state = read_state(home)
        archived_ids = [s["id"] for s in state["history"]["last_sessions"]]
        assert session_id in archived_ids
        assert any("finish y" in item for item in state["history"]["unfinished_work"])


class TestPreCompact:
    def test_stamps_compaction_marker(self, home):
        result = run_hook("pre_compact.py", {}, home)
        assert result.returncode == 0
        assert read_state(home)["session"]["last_compacted"]
