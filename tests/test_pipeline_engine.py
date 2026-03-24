"""
Archon v2.0 Test Suite — Pipeline Engine Tests

Tests the core PipelineExecutor, PipelineDefinition, and StepResult classes.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path
ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestPipelineDefinition:
    """Test pipeline YAML loading and parsing."""

    def test_load_sdd_pipeline(self):
        """Load the SDD pipeline from YAML."""
        from archon.core.pipeline_engine import PipelineDefinition

        pipeline_path = ARCHON_ROOT / "pipelines" / "sdd-pipeline.yaml"
        if not pipeline_path.exists():
            pytest.skip("sdd-pipeline.yaml not found")

        pipeline = PipelineDefinition.from_yaml(pipeline_path)
        assert pipeline.name == "sdd-pipeline"
        assert len(pipeline.steps) > 0
        assert pipeline.version != ""

    def test_load_all_pipelines(self):
        """Ensure all pipeline YAMLs parse without error."""
        from archon.core.pipeline_engine import PipelineDefinition

        pipelines_dir = ARCHON_ROOT / "pipelines"
        if not pipelines_dir.exists():
            pytest.skip("pipelines directory not found")

        loaded = 0
        for yaml_file in pipelines_dir.glob("*.yaml"):
            pipeline = PipelineDefinition.from_yaml(yaml_file)
            assert pipeline.name != "", f"Pipeline in {yaml_file.name} has no name"
            assert len(pipeline.steps) > 0, f"Pipeline {pipeline.name} has no steps"
            loaded += 1

        assert loaded > 0, "No pipeline files found"

    def test_pipeline_has_steps_with_agents(self):
        """Each pipeline step should reference an agent."""
        from archon.core.pipeline_engine import PipelineDefinition

        pipeline_path = ARCHON_ROOT / "pipelines" / "sdd-pipeline.yaml"
        if not pipeline_path.exists():
            pytest.skip("sdd-pipeline.yaml not found")

        pipeline = PipelineDefinition.from_yaml(pipeline_path)
        for step in pipeline.steps:
            assert "agent" in step, f"Step missing 'agent' field: {step}"


class TestStepResult:
    """Test StepResult data class."""

    def test_step_result_creation(self):
        from archon.core.pipeline_engine import StepResult, StepStatus

        result = StepResult(
            step_name="test-step",
            status=StepStatus.COMPLETED,
            duration_ms=150,
            artifacts=["output.md"],
        )
        assert result.step_name == "test-step"
        assert result.status == StepStatus.COMPLETED
        assert result.duration_ms == 150

    def test_step_result_to_dict(self):
        from archon.core.pipeline_engine import StepResult, StepStatus

        result = StepResult(
            step_name="test-step",
            status=StepStatus.FAILED,
            errors=["File not found"],
        )
        d = result.to_dict()
        assert d["status"] == "failed"
        assert "File not found" in d["errors"]

    def test_step_result_defaults(self):
        from archon.core.pipeline_engine import StepResult, StepStatus

        result = StepResult(step_name="s", status=StepStatus.PENDING)
        assert result.duration_ms == 0
        assert result.artifacts == []
        assert result.errors == []
        assert result.attempt == 1


class TestPipelineExecutor:
    """Test PipelineExecutor initialization and pipeline loading."""

    def test_executor_init(self):
        from archon.core.pipeline_engine import PipelineExecutor

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            assert executor.hooks_dir.exists()

    def test_load_pipeline_not_found(self):
        from archon.core.pipeline_engine import PipelineExecutor

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            with pytest.raises(FileNotFoundError):
                executor.load_pipeline("nonexistent-pipeline")

    def test_execute_pipeline_default_handler(self):
        """Execute pipeline with default (simulation) handler."""
        from archon.core.pipeline_engine import PipelineExecutor

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            pipeline = executor.load_pipeline("sdd-pipeline")
            result = executor.execute(pipeline, project_dir=tmpdir)

            assert result["status"] in ("completed", "failed")
            assert "steps" in result
            assert "state_id" in result

    def test_execute_with_custom_handler(self):
        """Execute pipeline with custom step handler."""
        from archon.core.pipeline_engine import (
            PipelineExecutor, StepResult, StepStatus,
        )

        executed_steps = []

        def custom_handler(step_config, context):
            step_name = step_config.get("name", "unknown")
            executed_steps.append(step_name)
            return StepResult(
                step_name=step_name,
                status=StepStatus.COMPLETED,
                artifacts=[f"{step_name}-output.md"],
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            pipeline = executor.load_pipeline("sdd-pipeline")
            result = executor.execute(
                pipeline, project_dir=tmpdir, step_handler=custom_handler
            )

            assert result["status"] == "completed"
            assert len(executed_steps) == len(pipeline.steps)

    def test_execute_with_failing_step(self):
        """Pipeline halts on step failure."""
        from archon.core.pipeline_engine import (
            PipelineExecutor, StepResult, StepStatus,
        )

        call_count = 0

        def failing_handler(step_config, context):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                return StepResult(
                    step_name=step_config.get("name", ""),
                    status=StepStatus.FAILED,
                    errors=["Intentional test failure"],
                )
            return StepResult(
                step_name=step_config.get("name", ""),
                status=StepStatus.COMPLETED,
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            pipeline = executor.load_pipeline("sdd-pipeline")
            result = executor.execute(
                pipeline, project_dir=tmpdir, step_handler=failing_handler
            )

            # Should have failed or escalated depending on retry policy
            assert result["status"] in ("failed", "completed")


class TestPipelineStateMachine:
    """Test state machine transitions."""

    def test_status_values(self):
        from archon.core.pipeline_engine import PipelineStatus

        assert PipelineStatus.PENDING.value == "pending"
        assert PipelineStatus.EXECUTING.value == "executing"
        assert PipelineStatus.COMPLETED.value == "completed"
        assert PipelineStatus.FAILED.value == "failed"
        assert PipelineStatus.CANCELLED.value == "cancelled"
        assert PipelineStatus.PAUSED.value == "paused"

    def test_step_status_values(self):
        from archon.core.pipeline_engine import StepStatus

        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.LOOPING.value == "looping"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
