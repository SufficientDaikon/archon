"""
Archon v2.0 Test Suite — Pipeline State Manager Tests

Tests PipelineState creation, persistence, accumulated state, and health scoring.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestPipelineStateCreation:
    """Test state creation and initialization."""

    def test_create_state(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PipelineState.create("test-pipeline", tmpdir)
            assert state.pipeline_name == "test-pipeline"
            assert state.status == "pending"
            assert state.state_id.startswith("test-pipeline-")

    def test_state_has_accumulated(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PipelineState.create("test", tmpdir)
            assert "decisions" in state.accumulated
            assert "constraints" in state.accumulated
            assert "tech_stack" in state.accumulated

    def test_state_id_unique(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            s1 = PipelineState.create("test", tmpdir)
            s2 = PipelineState.create("test", tmpdir)
            assert s1.state_id != s2.state_id


class TestPipelineStatePersistence:
    """Test state save/load cycle."""

    def test_save_and_load(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PipelineState.create("test-pipeline", ".")
            state.save(Path(tmpdir))

            loaded = PipelineState.load(state.state_id, Path(tmpdir))
            assert loaded is not None
            assert loaded.state_id == state.state_id
            assert loaded.pipeline_name == "test-pipeline"
            assert loaded.status == "pending"

    def test_load_nonexistent(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            loaded = PipelineState.load("nonexistent-id", Path(tmpdir))
            assert loaded is None

    def test_state_persists_on_update(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PipelineState.create("test", ".")
            state_dir = Path(tmpdir)
            state.save(state_dir)

            state.update_status("executing")
            state.save(state_dir)

            loaded = PipelineState.load(state.state_id, state_dir)
            assert loaded.status == "executing"

    def test_state_file_is_valid_json(self):
        from archon.core.pipeline_state import PipelineState

        with tempfile.TemporaryDirectory() as tmpdir:
            state = PipelineState.create("test", ".")
            state_file = state.save(Path(tmpdir))

            with open(state_file, "r") as f:
                data = json.load(f)

            assert "state_id" in data
            assert "pipeline_name" in data
            assert "status" in data
            assert "accumulated" in data


class TestAccumulatedState:
    """Test that state accumulates (grows, never shrinks)."""

    def test_add_decision(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.add_decision("Use PostgreSQL for database")
        assert "Use PostgreSQL for database" in state.accumulated["decisions"]

    def test_no_duplicate_decisions(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.add_decision("Use PostgreSQL")
        state.add_decision("Use PostgreSQL")
        assert state.accumulated["decisions"].count("Use PostgreSQL") == 1

    def test_add_constraint(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.add_constraint("Must support Python 3.9+")
        assert "Must support Python 3.9+" in state.accumulated["constraints"]

    def test_add_tech_stack(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.add_tech_stack("Python")
        state.add_tech_stack("FastAPI")
        assert "Python" in state.accumulated["tech_stack"]
        assert "FastAPI" in state.accumulated["tech_stack"]

    def test_accumulated_state_grows(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")

        # Add various items
        state.add_decision("Decision 1")
        state.add_decision("Decision 2")
        state.add_constraint("Constraint 1")
        state.add_tech_stack("Tech 1")

        assert len(state.accumulated["decisions"]) == 2
        assert len(state.accumulated["constraints"]) == 1
        assert len(state.accumulated["tech_stack"]) == 1

    def test_add_context_brief(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.add_context_brief("Context from spec-writer step")
        assert len(state.accumulated["context_briefs"]) == 1
        assert state.accumulated["context_briefs"][0]["brief"] == "Context from spec-writer step"


class TestStepRecording:
    """Test step recording and tracking."""

    def test_record_step(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_step("specify", "completed", {"artifacts": ["spec.md"]})
        assert len(state.steps) == 1
        assert state.steps[0]["name"] == "specify"
        assert state.steps[0]["status"] == "completed"

    def test_record_step_updates_existing(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_step("specify", "running")
        state.record_step("specify", "completed")
        assert len(state.steps) == 1
        assert state.steps[0]["status"] == "completed"

    def test_completed_step_names(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_step("step-1", "completed")
        state.record_step("step-2", "running")
        state.record_step("step-3", "completed")

        completed = state.completed_step_names()
        assert "step-1" in completed
        assert "step-3" in completed
        assert "step-2" not in completed

    def test_current_step(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_step("step-1", "completed")
        state.record_step("step-2", "running")

        assert state.current_step() == "step-2"


class TestDeviations:
    """Test deviation recording."""

    def test_record_deviation(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        dev_id = state.record_deviation("Changed database", "major", "implement")
        assert dev_id == "DEV-001"
        assert len(state.deviations) == 1

    def test_multiple_deviations(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_deviation("Change 1", "minor")
        state.record_deviation("Change 2", "major")
        state.record_deviation("Change 3", "critical")
        assert len(state.deviations) == 3
        assert state.deviations[2]["id"] == "DEV-003"


class TestHealthScore:
    """Test health score calculation."""

    def test_perfect_health(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        assert state.get_health_score() == 100

    def test_health_decreases_with_deviations(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_deviation("Minor issue", "minor")
        assert state.get_health_score() == 95

        state.record_deviation("Major issue", "major")
        assert state.get_health_score() == 85

        state.record_deviation("Critical issue", "critical")
        assert state.get_health_score() == 65

    def test_health_decreases_with_failed_steps(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        state.record_step("step-1", "failed")
        assert state.get_health_score() == 90

    def test_health_minimum_zero(self):
        from archon.core.pipeline_state import PipelineState

        state = PipelineState("test-1", "test", ".")
        for i in range(20):
            state.record_deviation(f"Critical {i}", "critical")
        assert state.get_health_score() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
