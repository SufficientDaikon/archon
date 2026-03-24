"""
Archon v2.0 Test Suite — Integration Tests

End-to-end tests that verify the full pipeline flow:
1. Load pipeline from YAML
2. Execute with hooks
3. Validate artifacts
4. Check state persistence
5. Verify accumulated state
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestEndToEndPipelineFlow:
    """Test complete pipeline execution flow."""

    def test_load_execute_persist(self):
        """Full flow: load → execute → verify state persisted."""
        from archon.core.pipeline_engine import (
            PipelineExecutor, StepResult, StepStatus,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            pipeline = executor.load_pipeline("sdd-pipeline")

            def mock_handler(step_config, context):
                name = step_config.get("name", "unknown")
                output = step_config.get("output", "")
                if output:
                    Path(context["project_dir"], output).write_text(
                        f"# {name} output\n\nGenerated content for {name}."
                    )
                return StepResult(
                    step_name=name,
                    status=StepStatus.COMPLETED,
                    artifacts=[output] if output else [],
                )

            result = executor.execute(
                pipeline, project_dir=tmpdir, step_handler=mock_handler
            )

            assert result["status"] == "completed"
            assert len(result["steps"]) == len(pipeline.steps)

            # Verify state was persisted
            state_files = list(Path(tmpdir).glob("*.json"))
            assert len(state_files) >= 1

    def test_pipeline_state_survives_reload(self):
        """State can be loaded after pipeline execution."""
        from archon.core.pipeline_engine import PipelineExecutor
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            pipeline = executor.load_pipeline("sdd-pipeline")
            result = executor.execute(pipeline, project_dir=tmpdir)

            state_id = result["state_id"]
            loaded = PipelineState.load(state_id, Path(tmpdir))

            assert loaded is not None
            assert loaded.pipeline_name == "sdd-pipeline"
            assert loaded.status in ("completed", "failed")

    def test_accumulated_state_persists(self):
        """Decisions added during execution are persisted."""
        from archon.core.pipeline_engine import (
            PipelineExecutor, StepResult, StepStatus,
        )
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            executor = PipelineExecutor(
                hooks_dir=ARCHON_ROOT / "hooks",
                state_dir=Path(tmpdir),
            )
            pipeline = executor.load_pipeline("sdd-pipeline")

            decisions_made = []

            def handler_with_decisions(step_config, context):
                name = step_config.get("name", "unknown")
                decision = f"Decision from {name}"
                decisions_made.append(decision)
                # Load state, add decision, save it back
                state_id = context["state"]["state_id"]
                state = PipelineState.load(state_id, Path(tmpdir))
                if state:
                    state.add_decision(decision)
                    state.add_tech_stack("Python")
                    state.save(Path(tmpdir))
                return StepResult(
                    step_name=name,
                    status=StepStatus.COMPLETED,
                )

            result = executor.execute(
                pipeline, project_dir=tmpdir, step_handler=handler_with_decisions
            )

            # Reload and check
            state = PipelineState.load(result["state_id"], Path(tmpdir))
            assert state is not None
            assert len(decisions_made) > 0
            assert len(state.accumulated["decisions"]) > 0
            assert "Python" in state.accumulated["tech_stack"]


class TestHookIntegration:
    """Test that hooks integrate properly with pipeline execution."""

    def test_session_start_fires(self):
        """Session-start hook fires during pipeline execution."""
        from hooks.session_start import execute
        result = execute()
        assert result["status"] == "success"
        assert result["discipline"]["anti_rationalization"] is True

    def test_pre_post_step_chain(self):
        """Pre-step and post-step hooks work in sequence."""
        from hooks.pre_step import execute as pre_execute
        from hooks.post_step import execute as post_execute

        # Pre-step for first step (no prerequisites)
        pre_result = pre_execute({
            "pipeline": "test",
            "step": "step-1",
            "step_index": 0,
            "state": {"project_dir": "."},
            "step_config": {},
        })
        assert pre_result["status"] == "pass"

        # Post-step with no validation requirements
        post_result = post_execute({
            "pipeline": "test",
            "step": "step-1",
            "step_index": 0,
            "state": {"project_dir": "."},
            "step_config": {},
        })
        assert post_result["status"] == "pass"


class TestSDKIntegration:
    """Test SDK pipeline methods."""

    def test_sdk_health_check_includes_synapses(self):
        sdk_path = ARCHON_ROOT / "sdk"
        sys.path.insert(0, str(sdk_path.parent))
        from sdk.archon import Archon

        os_sdk = Archon(root_path=ARCHON_ROOT)
        health = os_sdk.health_check()
        assert "synapses_count" in health
        assert health["synapses_count"] >= 3

    def test_sdk_list_synapses(self):
        from sdk.archon import Archon

        os_sdk = Archon(root_path=ARCHON_ROOT)
        synapses = os_sdk.list_synapses()
        assert len(synapses) >= 3
        names = [s["name"] for s in synapses]
        assert "anti-rationalization" in names
        assert "sequential-thinking" in names
        assert "metacognition" in names

    def test_sdk_get_core_synapses(self):
        from sdk.archon import Archon

        os_sdk = Archon(root_path=ARCHON_ROOT)
        core = os_sdk.get_core_synapses()
        assert len(core) >= 3

    def test_sdk_version(self):
        from sdk.archon import Archon

        os_sdk = Archon(root_path=ARCHON_ROOT)
        health = os_sdk.health_check()
        assert health["archon_version"] == "1.0.0"


class TestManifestConsistency:
    """Test that archon.yaml is consistent with filesystem."""

    def test_version_is_1_0_0(self):
        import yaml
        with open(ARCHON_ROOT / "archon.yaml") as f:
            manifest = yaml.safe_load(f)
        assert manifest["version"] == "1.0.0"

    def test_all_synapse_paths_exist(self):
        import yaml
        with open(ARCHON_ROOT / "archon.yaml") as f:
            manifest = yaml.safe_load(f)
        for synapse in manifest.get("synapses", []):
            path = ARCHON_ROOT / synapse["path"]
            assert path.exists(), f"Synapse path missing: {path}"

    def test_all_pipeline_paths_exist(self):
        import yaml
        with open(ARCHON_ROOT / "archon.yaml") as f:
            manifest = yaml.safe_load(f)
        for pipeline in manifest.get("pipelines", []):
            path = ARCHON_ROOT / pipeline["path"]
            assert path.exists(), f"Pipeline path missing: {path}"

    def test_hooks_directory_exists(self):
        assert (ARCHON_ROOT / "hooks").exists()
        assert (ARCHON_ROOT / "hooks" / "hooks.yaml").exists()

    def test_new_schemas_exist(self):
        schemas = [
            "guardrails.schema.yaml",
            "deviation-log.schema.yaml",
            "thinking-trace.schema.yaml",
        ]
        for schema in schemas:
            path = ARCHON_ROOT / "schemas" / schema
            assert path.exists(), f"Schema missing: {path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
