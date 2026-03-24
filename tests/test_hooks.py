"""
Archon v2.0 Test Suite — Hook System Tests

Tests session-start, pre-step, post-step, on-failure, and on-deviation hooks.
"""

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))
sys.path.insert(0, str(ARCHON_ROOT))


class TestHookConfiguration:
    """Test hooks.yaml configuration."""

    def test_hooks_yaml_exists(self):
        assert (ARCHON_ROOT / "hooks" / "hooks.yaml").exists()

    def test_hooks_yaml_parses(self):
        with open(ARCHON_ROOT / "hooks" / "hooks.yaml") as f:
            config = yaml.safe_load(f)
        assert "hooks" in config
        assert "settings" in config

    def test_all_hook_types_defined(self):
        with open(ARCHON_ROOT / "hooks" / "hooks.yaml") as f:
            config = yaml.safe_load(f)
        hooks = config["hooks"]
        assert "session-start" in hooks
        assert "pre-step" in hooks
        assert "post-step" in hooks
        assert "on-failure" in hooks
        assert "on-deviation" in hooks

    def test_all_hooks_enabled(self):
        with open(ARCHON_ROOT / "hooks" / "hooks.yaml") as f:
            config = yaml.safe_load(f)
        for name, hook in config["hooks"].items():
            assert hook.get("enabled", False), f"Hook '{name}' should be enabled"


class TestSessionStartHook:
    """Test session-start hook execution."""

    def test_hook_file_exists(self):
        assert (ARCHON_ROOT / "hooks" / "session_start.py").exists()

    def test_hook_executes(self):
        from hooks.session_start import execute
        result = execute()
        assert result["status"] == "success"
        assert "discipline" in result

    def test_hook_injects_discipline(self):
        from hooks.session_start import execute
        result = execute()
        discipline = result["discipline"]
        assert discipline["anti_rationalization"] is True
        assert discipline["sequential_thinking"] is True
        assert discipline["stuck_loop_threshold"] == 3

    def test_hook_loads_core_synapses(self):
        from hooks.session_start import execute
        result = execute()
        assert len(result["injected"]) > 0


class TestPreStepHook:
    """Test pre-step hook execution."""

    def test_hook_file_exists(self):
        assert (ARCHON_ROOT / "hooks" / "pre_step.py").exists()

    def test_hook_passes_for_first_step(self):
        from hooks.pre_step import execute
        result = execute({
            "pipeline": "test",
            "step": "first",
            "step_index": 0,
            "state": {},
            "step_config": {},
        })
        assert result["status"] == "pass"

    def test_hook_returns_errors_and_warnings(self):
        from hooks.pre_step import execute
        result = execute({
            "pipeline": "test",
            "step": "second",
            "step_index": 1,
            "state": {"project_dir": "/nonexistent"},
            "step_config": {
                "validation": {
                    "expected-artifacts": [
                        {"path-pattern": "nonexistent-file.md"}
                    ]
                }
            },
        })
        assert result["status"] == "fail"
        assert len(result["errors"]) > 0


class TestPostStepHook:
    """Test post-step hook execution."""

    def test_hook_file_exists(self):
        assert (ARCHON_ROOT / "hooks" / "post_step.py").exists()

    def test_hook_passes_with_no_validation(self):
        from hooks.post_step import execute
        result = execute({
            "pipeline": "test",
            "step": "step-1",
            "step_index": 0,
            "state": {"project_dir": "."},
            "step_config": {},
        })
        assert result["status"] == "pass"

    def test_hook_fails_on_missing_artifact(self):
        from hooks.post_step import execute
        result = execute({
            "pipeline": "test",
            "step": "step-1",
            "step_index": 0,
            "state": {"project_dir": "/nonexistent"},
            "step_config": {
                "validation": {
                    "expected-artifacts": [
                        {"path-pattern": "required-output.md"}
                    ]
                }
            },
        })
        assert result["status"] == "fail"

    def test_hook_checks_word_count(self):
        from hooks.post_step import execute

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "short.md").write_text("Just a few words")
            result = execute({
                "pipeline": "test",
                "step": "step-1",
                "step_index": 0,
                "state": {"project_dir": tmpdir},
                "step_config": {
                    "validation": {
                        "expected-artifacts": [{"path-pattern": "short.md"}],
                        "min-word-count": 1000,
                    }
                },
            })
            assert result["status"] == "fail"
            assert any("too short" in e for e in result["errors"])


class TestOnFailureHook:
    """Test on-failure hook execution."""

    def test_hook_file_exists(self):
        assert (ARCHON_ROOT / "hooks" / "on_failure.py").exists()

    def test_retry_policy(self):
        from hooks.on_failure import execute
        result = execute({
            "step": "implement",
            "error": "Test error",
            "attempt": 1,
            "max_retries": 3,
            "step_config": {"on-failure": "retry"},
        })
        assert result["action"] == "retry"

    def test_halt_policy(self):
        from hooks.on_failure import execute
        result = execute({
            "step": "implement",
            "error": "Test error",
            "attempt": 1,
            "max_retries": 3,
            "step_config": {"on-failure": "halt"},
        })
        assert result["action"] == "halt"

    def test_escape_hatch_at_3_attempts(self):
        """3-fix escape hatch should trigger at 3+ attempts."""
        from hooks.on_failure import execute
        result = execute({
            "step": "implement",
            "error": "Persistent failure",
            "attempt": 3,
            "max_retries": 5,
            "step_config": {"on-failure": "retry"},
        })
        assert result["action"] == "escalate"
        assert "3-FIX ESCAPE HATCH" in result["reason"]

    def test_skip_policy(self):
        from hooks.on_failure import execute
        result = execute({
            "step": "optional-step",
            "error": "Non-critical error",
            "attempt": 1,
            "step_config": {"on-failure": "skip"},
        })
        assert result["action"] == "skip"


class TestOnDeviationHook:
    """Test on-deviation hook execution."""

    def test_hook_file_exists(self):
        assert (ARCHON_ROOT / "hooks" / "on_deviation.py").exists()

    def test_deviation_logged(self):
        from hooks.on_deviation import execute
        result = execute({
            "pipeline": "test",
            "step": "implement",
            "agent": "implementer",
            "what": "Test deviation",
            "why": "Testing",
            "severity": "minor",
        })
        assert result["status"] == "logged"
        assert result["deviation_id"].startswith("DEV-")

    def test_critical_deviation_escalated(self):
        from hooks.on_deviation import execute
        result = execute({
            "pipeline": "test",
            "step": "implement",
            "what": "Critical deviation",
            "severity": "critical",
        })
        assert result["status"] == "escalated"
        assert "HALT" in result["action"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
