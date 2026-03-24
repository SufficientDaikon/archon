"""
Archon v2.0 Test Suite — CLI Pipeline Commands

Tests the typer-based pipeline CLI module using CliRunner and mocking
to verify subcommand structure and command behaviour without executing pipelines.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))

from typer.testing import CliRunner

from archon.commands.pipeline import (
    pipeline_app,
    _create_executor,
    STATE_DIR,
    PIPELINES_DIR,
)

runner = CliRunner()


# ── Subcommand Structure ──────────────────────────────────────────────────


class TestPipelineAppStructure:
    """Verify the pipeline typer app registers all expected subcommands."""

    def test_pipeline_app_is_not_none(self):
        assert pipeline_app is not None

    def test_all_five_subcommands_registered(self):
        names = {cmd.name for cmd in pipeline_app.registered_commands}
        expected = {"run", "status", "resume", "list", "cancel"}
        assert expected.issubset(names), f"Missing: {expected - names}"

    def test_no_args_shows_help(self):
        result = runner.invoke(pipeline_app, [])
        # typer with no_args_is_help=True exits with code 0 or 2
        assert result.exit_code in (0, 2)
        assert "Usage" in result.output or "pipeline" in result.output.lower()


# ── Run Subcommand ─────────────────────────────────────────────────────────


class TestPipelineRun:
    """Test the 'run' subcommand with mocked PipelineExecutor."""

    @patch("archon.commands.pipeline._create_executor")
    def test_run_creates_executor_and_executes(self, mock_create):
        mock_executor = MagicMock()
        mock_pipeline = MagicMock()
        mock_pipeline.name = "sdd-pipeline"
        mock_pipeline.steps = [{"name": "s1"}, {"name": "s2"}]
        mock_pipeline.resumable = True
        mock_executor.load_pipeline.return_value = mock_pipeline
        mock_executor.execute.return_value = {
            "state_id": "sdd-pipeline-001",
            "status": "completed",
            "health_score": 100,
        }
        mock_executor._default_step_handler.return_value = MagicMock(
            status=MagicMock(value="completed"),
        )
        mock_create.return_value = mock_executor

        result = runner.invoke(pipeline_app, ["run", "sdd-pipeline"])
        mock_executor.load_pipeline.assert_called_once_with("sdd-pipeline")
        mock_executor.execute.assert_called_once()

    @patch("archon.commands.pipeline._create_executor")
    def test_run_invalid_pipeline_exits_nonzero(self, mock_create):
        mock_executor = MagicMock()
        mock_executor.load_pipeline.side_effect = FileNotFoundError("not found")
        mock_create.return_value = mock_executor

        result = runner.invoke(pipeline_app, ["run", "nonexistent"])
        assert result.exit_code != 0


# ── List Subcommand ────────────────────────────────────────────────────────


class TestPipelineList:
    """Test the 'list' subcommand scanning the state directory."""

    def test_list_empty_state_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("archon.commands.pipeline.STATE_DIR", Path(tmpdir)):
                result = runner.invoke(pipeline_app, ["list"])
                assert result.exit_code == 0

    @patch("archon.commands.pipeline.PipelineState")
    def test_list_returns_entries_from_state_files(self, mock_state_cls):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "pipe-001.json").write_text("{}")
            (tmp / "pipe-002.json").write_text("{}")

            mock_state = MagicMock()
            mock_state.state_id = "pipe-001"
            mock_state.pipeline_name = "test"
            mock_state.status = "completed"
            mock_state.project_dir = "."
            mock_state.steps = []
            mock_state.completed_step_names.return_value = []
            mock_state.get_health_score.return_value = 100
            mock_state.to_dict.return_value = {}
            mock_state_cls.load.return_value = mock_state

            with patch("archon.commands.pipeline.STATE_DIR", tmp):
                result = runner.invoke(pipeline_app, ["list"])
                assert mock_state_cls.load.call_count >= 1


# ── Cancel Subcommand ──────────────────────────────────────────────────────


class TestPipelineCancel:
    """Test the 'cancel' subcommand."""

    @patch("archon.commands.pipeline.PipelineState")
    def test_cancel_nonexistent_state_returns_error(self, mock_state_cls):
        mock_state_cls.load.return_value = None
        result = runner.invoke(pipeline_app, ["cancel", "ghost-id"])
        assert result.exit_code != 0

    @patch("archon.commands.pipeline.PipelineState")
    def test_cancel_active_pipeline_updates_status(self, mock_state_cls):
        mock_state = MagicMock()
        mock_state.state_id = "pipe-001"
        mock_state.pipeline_name = "test"
        mock_state.status = "running"
        mock_state.to_dict.return_value = {}
        mock_state_cls.load.return_value = mock_state

        runner.invoke(pipeline_app, ["cancel", "pipe-001"])
        mock_state.update_status.assert_called_once()
        mock_state.save.assert_called_once()

    @patch("archon.commands.pipeline.PipelineState")
    def test_cancel_already_completed_exits_zero(self, mock_state_cls):
        mock_state = MagicMock()
        mock_state.status = "completed"
        mock_state_cls.load.return_value = mock_state

        result = runner.invoke(pipeline_app, ["cancel", "pipe-done"])
        assert result.exit_code == 0


# ── Helper / Constants ─────────────────────────────────────────────────────


class TestHelpers:
    """Test module-level helpers and constants."""

    @patch("archon.commands.pipeline.PipelineExecutor")
    def test_create_executor_returns_instance(self, mock_cls):
        mock_cls.return_value = MagicMock()
        executor = _create_executor()
        mock_cls.assert_called_once()
        assert executor is not None

    def test_pipelines_dir_points_to_pipelines(self):
        assert PIPELINES_DIR.name == "pipelines"

    def test_state_dir_ends_with_pipeline_states(self):
        assert STATE_DIR.parts[-1] == "pipeline-states"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
