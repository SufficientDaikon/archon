"""
Archon v3 E2 Tests — Runtime and Session Orchestration.

Tests:
- E2-S1: State machine transitions, invalid transition rejection, recovery
- E2-S2: Session lifecycle (create, resume, send, abort, archive)
- E2-S3: Correlation ID linking between session and pipeline
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.archon.core.session_manager import (
    InvalidTransitionError,
    Session,
    SessionStatus,
)


# ---------------------------------------------------------------------------
# E2-S1: Client lifecycle state machine
# ---------------------------------------------------------------------------

class TestSessionStateMachine:
    """State machine must enforce valid transitions and reject invalid ones."""

    def test_create_starts_in_created(self):
        s = Session.create("test objective", "test-pipeline")
        assert s.status == SessionStatus.CREATED

    def test_created_to_active(self):
        s = Session.create("test", "pipe")
        s.activate()
        assert s.status == SessionStatus.ACTIVE

    def test_active_to_waiting_tool(self):
        s = _active_session()
        s.wait_for_tool("Read")
        assert s.status == SessionStatus.WAITING_TOOL

    def test_active_to_waiting_permission(self):
        s = _active_session()
        s.wait_for_permission("perm-file-write")
        assert s.status == SessionStatus.WAITING_PERMISSION

    def test_active_to_idle(self):
        s = _active_session()
        s.idle()
        assert s.status == SessionStatus.IDLE

    def test_active_to_error(self):
        s = _active_session()
        s.fail("something broke")
        assert s.status == SessionStatus.ERROR

    def test_active_to_archived(self):
        s = _active_session()
        s.complete()
        assert s.status == SessionStatus.ARCHIVED

    def test_waiting_tool_to_active(self):
        s = _active_session()
        s.wait_for_tool("Bash")
        s.resume()
        assert s.status == SessionStatus.ACTIVE

    def test_waiting_permission_to_active(self):
        s = _active_session()
        s.wait_for_permission("perm-x")
        s.resume()
        assert s.status == SessionStatus.ACTIVE

    def test_idle_to_active(self):
        s = _active_session()
        s.idle()
        s.resume()
        assert s.status == SessionStatus.ACTIVE

    def test_idle_to_archived(self):
        s = _active_session()
        s.idle()
        s.abort()
        assert s.status == SessionStatus.ARCHIVED

    def test_error_to_recovering(self):
        s = _active_session()
        s.fail("crash")
        result = s.recover()
        assert result is True
        assert s.status == SessionStatus.RECOVERING

    def test_recovering_to_active(self):
        s = _active_session()
        s.fail("crash")
        s.recover()
        s.resume()
        assert s.status == SessionStatus.ACTIVE

    def test_recovering_to_archived(self):
        s = _active_session()
        s.fail("crash")
        s.recover()
        s.abort()
        assert s.status == SessionStatus.ARCHIVED

    def test_archived_is_terminal(self):
        s = _active_session()
        s.complete()
        with pytest.raises(InvalidTransitionError):
            s.activate()

    def test_created_cannot_skip_to_error(self):
        s = Session.create("test", "pipe")
        with pytest.raises(InvalidTransitionError):
            s.fail("nope")

    def test_created_cannot_go_to_idle(self):
        s = Session.create("test", "pipe")
        with pytest.raises(InvalidTransitionError):
            s.idle()

    def test_error_cannot_go_to_active_directly(self):
        s = _active_session()
        s.fail("crash")
        with pytest.raises(InvalidTransitionError):
            s.resume()  # must go through RECOVERING first


# ---------------------------------------------------------------------------
# E2-S1: Recovery policies
# ---------------------------------------------------------------------------

class TestRecoveryPolicy:
    """Recovery must respect max_retries and stop when exhausted."""

    def test_recovery_respects_max_retries(self):
        s = Session.create("test", "pipe", recovery_policy={"max_retries": 2})
        s.activate()

        # First crash + recovery
        s.fail("err1")
        assert s.recover() is True
        s.resume()

        # Second crash + recovery
        s.fail("err2")
        assert s.recover() is True
        s.resume()

        # Third crash — recovery exhausted
        s.fail("err3")
        assert s.recover() is False
        assert s.status == SessionStatus.ERROR  # stays in ERROR

    def test_recovery_counter_increments(self):
        s = _active_session()
        s.fail("err")
        s.recover()
        assert s.recovery_attempts == 1
        s.resume()
        s.fail("err2")
        s.recover()
        assert s.recovery_attempts == 2

    def test_default_recovery_allows_3_retries(self):
        s = _active_session()
        for i in range(3):
            s.fail(f"err{i}")
            assert s.recover() is True
            s.resume()
        s.fail("final")
        assert s.recover() is False


# ---------------------------------------------------------------------------
# E2-S2: Session lifecycle service
# ---------------------------------------------------------------------------

class TestSessionLifecycle:
    """Session lifecycle: create, resume, send, abort, archive."""

    def test_create_generates_valid_ids(self):
        s = Session.create("test", "pipe")
        assert s.session_id.startswith("sess-")
        assert s.correlation_id.startswith("corr-")
        assert len(s.session_id) > 10
        assert len(s.correlation_id) > 10

    def test_send_records_step(self):
        s = _active_session()
        s.send("step-1", {"status": "completed", "artifacts": ["output.md"]})
        assert len(s.steps) == 1
        assert s.steps[0]["name"] == "step-1"
        assert s.steps[0]["correlation_id"] == s.correlation_id

    def test_send_rejects_when_not_active(self):
        s = Session.create("test", "pipe")
        with pytest.raises(InvalidTransitionError):
            s.send("step-1", {"status": "completed"})

    def test_abort_from_error(self):
        s = _active_session()
        s.fail("crash")
        s.abort()
        assert s.status == SessionStatus.ARCHIVED

    def test_objective_survives_lifecycle(self):
        s = Session.create("build auth system", "sdd")
        s.activate()
        s.idle()
        s.resume()
        s.complete()
        assert s.objective == "build auth system"

    def test_constraints_survive_lifecycle(self):
        constraints = [{"constraint": "no raw SQL", "enforcement": "hard"}]
        s = Session.create("test", "pipe", constraints=constraints)
        s.activate()
        s.idle()
        s.resume()
        s.complete()
        assert s.constraints == constraints


class TestSessionPersistence:
    """Session must persist and reload correctly."""

    def test_save_and_load(self, tmp_path: Path):
        s = Session.create("persist test", "sdd")
        s.activate()
        s.send("step-1", {"status": "completed"})
        s.add_decision("Use PostgreSQL")

        path = s.save(tmp_path)
        assert path.exists()

        loaded = Session.load(s.session_id, tmp_path)
        assert loaded is not None
        assert loaded.session_id == s.session_id
        assert loaded.status == SessionStatus.ACTIVE
        assert loaded.objective == "persist test"
        assert loaded.accumulated_state["decisions"] == ["Use PostgreSQL"]
        assert len(loaded.steps) == 1

    def test_load_nonexistent_returns_none(self, tmp_path: Path):
        loaded = Session.load("sess-doesnotexist", tmp_path)
        assert loaded is None

    def test_resume_from_disk_preserves_constraints(self, tmp_path: Path):
        s = Session.create("test", "pipe", constraints=[
            {"constraint": "v2 compat", "enforcement": "hard"}
        ])
        s.activate()
        s.idle()
        s.save(tmp_path)

        loaded = Session.load(s.session_id, tmp_path)
        assert loaded is not None
        loaded.resume()
        assert loaded.status == SessionStatus.ACTIVE
        assert loaded.constraints[0]["constraint"] == "v2 compat"


class TestAccumulatedState:
    """Accumulated state must grow, never shrink."""

    def test_add_decision(self):
        s = _active_session()
        s.add_decision("Use REST over GraphQL")
        assert "Use REST over GraphQL" in s.accumulated_state["decisions"]

    def test_no_duplicate_decisions(self):
        s = _active_session()
        s.add_decision("Use REST")
        s.add_decision("Use REST")
        assert s.accumulated_state["decisions"].count("Use REST") == 1

    def test_add_constraint(self):
        s = _active_session()
        s.add_constraint("No raw SQL")
        assert "No raw SQL" in s.accumulated_state["constraints"]


# ---------------------------------------------------------------------------
# E2-S3: Correlation ID linking
# ---------------------------------------------------------------------------

class TestCorrelationLinking:
    """Session must link to pipeline traces via correlation ID."""

    def test_link_returns_correlation_id(self):
        s = _active_session()
        corr = s.link_pipeline_trace("sdd-abc12345")
        assert corr == s.correlation_id
        assert corr.startswith("corr-")

    def test_link_emits_event(self):
        s = _active_session()
        s.link_pipeline_trace("sdd-xyz")
        events = [e for e in s.event_log if e["event_type"] == "pipeline_linked"]
        assert len(events) == 1
        assert events[0]["payload"]["pipeline_state_id"] == "sdd-xyz"

    def test_all_events_carry_correlation_id(self):
        s = Session.create("test", "pipe")
        s.activate()
        s.wait_for_tool("Read")
        s.resume()
        for event in s.event_log:
            assert event["correlation_id"] == s.correlation_id

    def test_context_checksum_is_deterministic(self):
        s = Session.create("test", "pipe")
        c1 = s.context_checksum()
        c2 = s.context_checksum()
        assert c1 == c2
        assert len(c1) == 64  # SHA-256

    def test_steps_carry_correlation_id(self):
        s = _active_session()
        s.send("step-1", {"status": "completed"})
        assert s.steps[0]["correlation_id"] == s.correlation_id


class TestEventLog:
    """Session event log must capture full lifecycle."""

    def test_create_emits_event(self):
        s = Session.create("test", "pipe")
        assert len(s.event_log) == 1
        assert s.event_log[0]["event_type"] == "session_created"

    def test_full_lifecycle_events(self):
        s = Session.create("test", "pipe")
        s.activate()
        s.wait_for_tool("Read")
        s.resume()
        s.complete()

        types = [e["event_type"] for e in s.event_log]
        assert types == [
            "session_created",
            "session_activated",
            "waiting_tool",
            "session_resumed",
            "session_completed",
        ]

    def test_events_have_required_fields(self):
        s = Session.create("test", "pipe")
        s.activate()
        for event in s.event_log:
            assert "event_id" in event
            assert event["event_id"].startswith("evt-")
            assert "timestamp" in event
            assert "session_id" in event
            assert "correlation_id" in event


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _active_session() -> Session:
    """Create a session already in ACTIVE state."""
    s = Session.create("test objective", "test-pipeline")
    s.activate()
    return s
