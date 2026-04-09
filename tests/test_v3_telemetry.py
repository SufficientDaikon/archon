"""
Archon v3 E5 Tests — Observability, Replay, Stress.

Tests:
- E5-S1: Telemetry envelope normalization
- E5-S2: Replay harness determinism and snapshot lifecycle
- E5-S3: Stress suites for concurrency and failure injection
"""

from __future__ import annotations

from pathlib import Path

import pytest

from archon.core.session_manager import Session, SessionStatus
from archon.core.policy_engine import PolicyEngine, PermissionRule
from archon.core.telemetry import (
    ReplayHarness,
    ReplaySnapshot,
    TelemetryCollector,
    TelemetryEnvelope,
)


# ---------------------------------------------------------------------------
# E5-S1: Telemetry envelope normalization
# ---------------------------------------------------------------------------

class TestTelemetryEnvelope:
    """All events must be normalized to versioned envelope."""

    def test_envelope_has_required_fields(self):
        e = TelemetryEnvelope("test_event", "test_component")
        d = e.to_dict()
        assert d["envelope_id"].startswith("tel-")
        assert d["schema_version"] == "3.0.0"
        assert d["event_type"] == "test_event"
        assert d["timestamp"]
        assert d["source"]["component"] == "test_component"

    def test_envelope_checksum_deterministic(self):
        e = TelemetryEnvelope("evt", "comp", payload={"x": 1})
        c1 = e.checksum()
        c2 = e.checksum()
        assert c1 == c2
        assert len(c1) == 64

    def test_envelope_carries_correlation_id(self):
        e = TelemetryEnvelope("evt", "comp", correlation_id="corr-abc123")
        assert e.to_dict()["correlation_id"] == "corr-abc123"

    def test_retention_class_default(self):
        e = TelemetryEnvelope("evt", "comp")
        assert e.retention_class == "standard"

    def test_audit_retention_for_policy_events(self):
        e = TelemetryEnvelope("policy_decision", "policy_engine", retention_class="audit")
        assert e.retention_class == "audit"


class TestTelemetryCollector:
    """Collector must index envelopes for query."""

    def test_emit_returns_id(self):
        c = TelemetryCollector()
        eid = c.emit(TelemetryEnvelope("evt", "comp"))
        assert eid.startswith("tel-")
        assert len(c.envelopes) == 1

    def test_filter_by_session(self):
        c = TelemetryCollector()
        c.emit(TelemetryEnvelope("e1", "c", session_id="sess-1"))
        c.emit(TelemetryEnvelope("e2", "c", session_id="sess-2"))
        c.emit(TelemetryEnvelope("e3", "c", session_id="sess-1"))
        result = c.get_by_session("sess-1")
        assert len(result) == 2

    def test_filter_by_correlation(self):
        c = TelemetryCollector()
        c.emit(TelemetryEnvelope("e1", "c", correlation_id="corr-a"))
        c.emit(TelemetryEnvelope("e2", "c", correlation_id="corr-b"))
        result = c.get_by_correlation("corr-a")
        assert len(result) == 1

    def test_filter_by_type(self):
        c = TelemetryCollector()
        c.emit(TelemetryEnvelope("session_start", "sm"))
        c.emit(TelemetryEnvelope("policy_decision", "pe"))
        c.emit(TelemetryEnvelope("session_start", "sm"))
        result = c.get_by_type("session_start")
        assert len(result) == 2

    def test_emit_from_session_event(self):
        c = TelemetryCollector()
        event = {
            "event_type": "session_activated",
            "session_id": "sess-abc",
            "correlation_id": "corr-xyz",
            "payload": {"k": "v"},
        }
        eid = c.emit_from_session_event(event)
        assert eid.startswith("tel-")
        assert c.envelopes[0].event_type == "session_activated"

    def test_emit_from_policy_decision(self):
        c = TelemetryCollector()
        decision = {
            "action": "deny",
            "tool_name": "Bash",
            "session_id": "sess-1",
            "correlation_id": "corr-1",
        }
        c.emit_from_policy_decision(decision)
        e = c.envelopes[0]
        assert e.event_type == "policy_decision"
        assert e.retention_class == "audit"
        assert e.tags["action"] == "deny"


# ---------------------------------------------------------------------------
# E5-S2: Replay harness determinism and snapshot lifecycle
# ---------------------------------------------------------------------------

class TestReplaySnapshot:
    """Snapshots must be saveable, loadable, and have deterministic checksums."""

    def test_snapshot_checksum_deterministic(self):
        s = _make_snapshot()
        c1 = s.checksum()
        c2 = s.checksum()
        assert c1 == c2

    def test_identical_runs_same_checksum(self):
        s1 = _make_snapshot(status="completed", steps=[{"name": "s1", "status": "completed"}])
        s2 = _make_snapshot(status="completed", steps=[{"name": "s1", "status": "completed"}])
        assert s1.checksum() == s2.checksum()

    def test_different_status_different_checksum(self):
        s1 = _make_snapshot(status="completed")
        s2 = _make_snapshot(status="failed")
        assert s1.checksum() != s2.checksum()

    def test_save_and_load(self, tmp_path: Path):
        s = _make_snapshot()
        path = s.save(tmp_path)
        assert path.exists()

        loaded = ReplaySnapshot.load(path)
        assert loaded is not None
        assert loaded.snapshot_id == s.snapshot_id
        assert loaded.checksum() == s.checksum()

    def test_load_nonexistent_returns_none(self, tmp_path: Path):
        loaded = ReplaySnapshot.load(tmp_path / "nope.json")
        assert loaded is None


class TestReplayHarness:
    """Replay harness must detect determinism and report diffs."""

    def test_identical_snapshots_are_deterministic(self):
        harness = ReplayHarness()
        s1 = _make_snapshot(status="completed", steps=[{"name": "s1", "status": "completed"}])
        s2 = _make_snapshot(status="completed", steps=[{"name": "s1", "status": "completed"}])
        result = harness.compare(s1, s2)
        assert result["deterministic"] is True

    def test_different_status_not_deterministic(self):
        harness = ReplayHarness()
        s1 = _make_snapshot(status="completed")
        s2 = _make_snapshot(status="failed")
        result = harness.compare(s1, s2)
        assert result["deterministic"] is False
        assert "diffs" in result
        assert any("status" in d for d in result["diffs"])

    def test_different_step_count_detected(self):
        harness = ReplayHarness()
        s1 = _make_snapshot(steps=[{"name": "s1", "status": "completed"}])
        s2 = _make_snapshot(steps=[
            {"name": "s1", "status": "completed"},
            {"name": "s2", "status": "completed"},
        ])
        result = harness.compare(s1, s2)
        assert result["deterministic"] is False

    def test_capture_from_live_session(self):
        # Full integration: session → telemetry → replay snapshot
        session = Session.create("replay test", "sdd")
        session.activate()
        session.send("step-1", {"status": "completed"})
        session.complete()

        collector = TelemetryCollector()
        for event in session.event_log:
            collector.emit_from_session_event(event)

        harness = ReplayHarness()
        snap = harness.capture(session.to_dict(), collector, [])
        assert snap.snapshot_id.startswith("snap-")
        assert snap.checksum()


# ---------------------------------------------------------------------------
# E5-S3: Stress suites for concurrency and failure injection
# ---------------------------------------------------------------------------

class TestStressSessionLifecycle:
    """Stress: rapid state transitions must not corrupt state."""

    def test_rapid_transitions_100_cycles(self):
        s = Session.create("stress", "pipe")
        s.activate()
        for i in range(100):
            s.wait_for_tool(f"tool-{i}")
            s.resume()
        assert s.status == SessionStatus.ACTIVE
        assert len(s.event_log) > 200

    def test_rapid_recovery_cycles(self):
        s = Session.create("stress", "pipe", recovery_policy={"max_retries": 50})
        s.activate()
        for i in range(50):
            s.fail(f"err-{i}")
            assert s.recover() is True
            s.resume()
        assert s.recovery_attempts == 50

    def test_large_accumulated_state(self):
        s = Session.create("stress", "pipe")
        s.activate()
        for i in range(500):
            s.add_decision(f"decision-{i}")
            s.add_constraint(f"constraint-{i}")
        assert len(s.accumulated_state["decisions"]) == 500
        assert len(s.accumulated_state["constraints"]) == 500


class TestStressPolicyEngine:
    """Stress: policy engine under high load."""

    def test_1000_evaluations(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="allow-all", scope="tool", trust_tier="community", action="allow",
        ))
        for i in range(1000):
            d = engine.evaluate(f"tool-{i}", f"sess-{i % 10}", "corr-x")
            assert d.is_allowed
        assert len(engine.audit_log) == 1000

    def test_mixed_allow_deny_pattern(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="verified-only", scope="tool", trust_tier="verified", action="allow",
        ))
        allowed = denied = 0
        for i in range(200):
            tier = "verified" if i % 2 == 0 else "untrusted"
            d = engine.evaluate("Tool", "sess-x", "corr-x", trust_tier=tier)
            if d.is_allowed:
                allowed += 1
            else:
                denied += 1
        assert allowed == 100
        assert denied == 100


class TestStressTelemetry:
    """Stress: telemetry collector under high volume."""

    def test_10000_envelopes(self):
        c = TelemetryCollector()
        for i in range(10000):
            c.emit(TelemetryEnvelope(
                f"event-{i % 5}", "stress",
                session_id=f"sess-{i % 10}",
                correlation_id=f"corr-{i % 20}",
            ))
        assert len(c.envelopes) == 10000
        # Filter must still work
        assert len(c.get_by_session("sess-0")) == 1000
        assert len(c.get_by_type("event-0")) == 2000

    def test_persistence_roundtrip(self, tmp_path: Path):
        """Snapshot save/load must preserve all data."""
        c = TelemetryCollector()
        for i in range(100):
            c.emit(TelemetryEnvelope(f"evt-{i}", "comp"))

        snap = ReplaySnapshot(
            snapshot_id="snap-stress",
            session_dict={"status": "completed", "objective": "test", "steps": []},
            telemetry=[e.to_dict() for e in c.envelopes],
            policy_decisions=[],
        )
        path = snap.save(tmp_path)
        loaded = ReplaySnapshot.load(path)
        assert loaded is not None
        assert len(loaded.telemetry) == 100
        assert loaded.checksum() == snap.checksum()


class TestStressFailureInjection:
    """Failure injection: silent failure paths must be caught."""

    def test_schema_validation_blocks_bad_batch(self):
        """Policy engine must block ALL bad invocations, not just some."""
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="allow-valid", scope="tool", trust_tier="community", action="allow",
        ))
        engine.register_tool_schema("StrictTool", {
            "required": ["id"],
            "properties": {"id": {"type": "string", "pattern": "^[a-z]+$"}},
        })

        # Every bad invocation must be denied
        bad_args = [
            {},                      # missing required
            {"id": 123},             # wrong type
            {"id": "ABC"},           # bad pattern
            {"id": "with spaces"},   # bad pattern
        ]
        for args in bad_args:
            d = engine.evaluate("StrictTool", "s", "c", arguments=args)
            assert d.action == "deny", f"Should deny args={args}, got {d.action}"

    def test_double_archive_rejected(self):
        """Cannot transition out of archived state."""
        from archon.core.session_manager import InvalidTransitionError
        s = Session.create("test", "pipe")
        s.activate()
        s.complete()
        with pytest.raises(InvalidTransitionError):
            s.activate()
        with pytest.raises(InvalidTransitionError):
            s.fail("nope")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_snapshot(
    status: str = "active",
    steps: list[dict] | None = None,
    policies: list[dict] | None = None,
    objective: str = "test",
) -> ReplaySnapshot:
    return ReplaySnapshot(
        snapshot_id=f"snap-test-{id(status) % 10000:04d}",
        session_dict={
            "status": status,
            "objective": objective,
            "steps": steps or [],
        },
        telemetry=[],
        policy_decisions=policies or [],
    )
