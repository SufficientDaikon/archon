"""
Archon v2.0 Stress Tests — Pipeline Edge Cases

Tests extreme conditions:
- Large pipelines (20+ steps)
- Cascading failures
- State corruption recovery
- Empty/malformed artifacts
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

ARCHON_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestLargePipeline:
    """Test pipeline with many steps."""

    def test_20_step_pipeline(self):
        """Execute a synthetic 20-step pipeline."""
        from archon.core.pipeline_engine import (
            PipelineExecutor, PipelineDefinition, StepResult, StepStatus,
        )

        steps = [
            {"name": f"step-{i}", "agent": "test-agent", "output": f"output-{i}.md"}
            for i in range(20)
        ]
        pipeline = PipelineDefinition(
            name="stress-test-large",
            version="1.0.0",
            description="Stress test with 20 steps",
            trigger="stress test",
            tags=["stress"],
            synapse_mode="standard",
            steps=steps,
        )

        executed = []

        def handler(step_config, context):
            name = step_config.get("name", "")
            executed.append(name)
            return StepResult(step_name=name, status=StepStatus.COMPLETED)

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            result = executor.execute(pipeline, project_dir=tmpdir, step_handler=handler)

            assert result["status"] == "completed"
            assert len(executed) == 20


class TestCascadingFailures:
    """Test failure handling across multiple steps."""

    def test_failure_at_step_5_halts(self):
        """Pipeline halts at step 5 when using halt policy."""
        from archon.core.pipeline_engine import (
            PipelineExecutor, PipelineDefinition, StepResult, StepStatus,
        )

        steps = [
            {"name": f"step-{i}", "agent": "test", "on-failure": "halt"}
            for i in range(10)
        ]
        pipeline = PipelineDefinition(
            name="cascade-test",
            version="1.0.0",
            description="Cascade failure test",
            trigger="test",
            tags=[],
            synapse_mode="standard",
            steps=steps,
        )

        call_count = 0

        def failing_at_5(step_config, context):
            nonlocal call_count
            call_count += 1
            name = step_config.get("name", "")
            if call_count == 5:
                return StepResult(
                    step_name=name,
                    status=StepStatus.FAILED,
                    errors=["Intentional failure at step 5"],
                )
            return StepResult(step_name=name, status=StepStatus.COMPLETED)

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            result = executor.execute(
                pipeline, project_dir=tmpdir, step_handler=failing_at_5
            )

            assert result["status"] == "failed"
            # Should have stopped — not all 10 executed
            assert call_count <= 6  # At most step 5 + one more


class TestStateCorruption:
    """Test recovery from corrupted state files."""

    def test_corrupted_json_returns_none(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "corrupted-state.json"
            state_file.write_text("NOT VALID JSON {{{")

            loaded = PipelineState.load("corrupted-state", Path(tmpdir))
            assert loaded is None

    def test_empty_json_returns_none(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "empty-state.json"
            state_file.write_text("")

            loaded = PipelineState.load("empty-state", Path(tmpdir))
            assert loaded is None

    def test_partial_json_returns_none(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "partial-state.json"
            state_file.write_text('{"state_id": "partial-state"')

            loaded = PipelineState.load("partial-state", Path(tmpdir))
            assert loaded is None


class TestArtifactEdgeCases:
    """Test artifact validation with edge cases."""

    def test_empty_file(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "empty.md").write_text("")
            result = validator.validate_min_content(str(Path(tmpdir, "empty.md")), 1)
            assert result.passed is False

    def test_very_large_file(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "word " * 100_000  # 100k words
            Path(tmpdir, "large.md").write_text(content)
            result = validator.validate_min_content(str(Path(tmpdir, "large.md")), 50_000)
            assert result.passed is True

    def test_binary_file(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "binary.bin").write_bytes(b"\x00\x01\x02\x03" * 100)
            result = validator.validate_exists("binary.bin", tmpdir)
            assert result.passed is True

    def test_nested_glob_pattern(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir, "sub", "dir")
            nested.mkdir(parents=True)
            (nested / "deep.md").write_text("deep content")
            result = validator.validate_exists("sub/dir/deep.md", tmpdir)
            assert result.passed is True

    def test_unicode_content(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "# 日本語テスト\n\nこれはテストです。" + " word" * 50
            filepath = str(Path(tmpdir, "unicode.md"))
            Path(filepath).write_text(content, encoding="utf-8")
            result = validator.validate_sections(filepath, ["日本語テスト"])
            assert result.passed is True


class TestHealthScoreEdgeCases:
    """Test health score calculation edge cases."""

    def test_many_critical_deviations(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test", "test", ".")
        for i in range(10):
            state.record_deviation(f"Critical {i}", "critical")
        assert state.get_health_score() == 0  # Capped at 0

    def test_mixed_severity_deviations(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test", "test", ".")
        state.record_deviation("Critical", "critical")   # -20
        state.record_deviation("Major", "major")           # -10
        state.record_deviation("Minor", "minor")           # -5
        assert state.get_health_score() == 65

    def test_failed_steps_reduce_health(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test", "test", ".")
        for i in range(5):
            state.record_step(f"step-{i}", "failed")
        assert state.get_health_score() == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
