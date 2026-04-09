"""
Archon v3 Telemetry and Replay — Observability, replay, and stress harness.

E5-S1: Normalize all runtime events to versioned telemetry envelope.
E5-S2: Replay-first E2E harness and snapshot lifecycle.
E5-S3: Stress suites for concurrency and failure injection.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TelemetryEnvelope:
    """
    Versioned telemetry envelope for all runtime events.

    Every event (session, tool, policy, hook) is normalized to this
    format for replay, observability, and audit.
    """

    SCHEMA_VERSION = "3.0.0"

    def __init__(
        self,
        event_type: str,
        source_component: str,
        payload: dict[str, Any] | None = None,
        correlation_id: str = "",
        session_id: str = "",
        pipeline_name: str = "",
        step_name: str = "",
        metrics: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
        retention_class: str = "standard",
        parent_id: str = "",
    ):
        self.envelope_id = f"tel-{uuid.uuid4().hex[:12]}"
        self.schema_version = self.SCHEMA_VERSION
        self.event_type = event_type
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.source = {
            "component": source_component,
            "session_id": session_id,
            "pipeline_name": pipeline_name,
            "step_name": step_name,
        }
        self.correlation_id = correlation_id
        self.parent_id = parent_id
        self.payload = payload or {}
        self.metrics = metrics or {}
        self.tags = tags or {}
        self.retention_class = retention_class

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "schema_version": self.schema_version,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "parent_id": self.parent_id,
            "payload": self.payload,
            "metrics": self.metrics,
            "tags": self.tags,
            "retention_class": self.retention_class,
        }

    def checksum(self) -> str:
        blob = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()


class TelemetryCollector:
    """Collects and indexes telemetry envelopes for replay."""

    def __init__(self):
        self._envelopes: list[TelemetryEnvelope] = []

    def emit(self, envelope: TelemetryEnvelope) -> str:
        """Record an envelope. Returns envelope_id."""
        self._envelopes.append(envelope)
        return envelope.envelope_id

    def emit_from_session_event(self, event: dict[str, Any]) -> str:
        """Convert a session event log entry to telemetry envelope."""
        envelope = TelemetryEnvelope(
            event_type=event.get("event_type", "unknown"),
            source_component="session_manager",
            payload=event.get("payload", {}),
            correlation_id=event.get("correlation_id", ""),
            session_id=event.get("session_id", ""),
        )
        return self.emit(envelope)

    def emit_from_policy_decision(self, decision_dict: dict[str, Any]) -> str:
        """Convert a policy decision to telemetry envelope."""
        envelope = TelemetryEnvelope(
            event_type="policy_decision",
            source_component="policy_engine",
            payload=decision_dict,
            correlation_id=decision_dict.get("correlation_id", ""),
            session_id=decision_dict.get("session_id", ""),
            tags={"action": decision_dict.get("action", ""), "tool": decision_dict.get("tool_name", "")},
            retention_class="audit",
        )
        return self.emit(envelope)

    @property
    def envelopes(self) -> list[TelemetryEnvelope]:
        return list(self._envelopes)

    def get_by_session(self, session_id: str) -> list[TelemetryEnvelope]:
        return [e for e in self._envelopes if e.source.get("session_id") == session_id]

    def get_by_correlation(self, correlation_id: str) -> list[TelemetryEnvelope]:
        return [e for e in self._envelopes if e.correlation_id == correlation_id]

    def get_by_type(self, event_type: str) -> list[TelemetryEnvelope]:
        return [e for e in self._envelopes if e.event_type == event_type]


class ReplaySnapshot:
    """
    Captures a deterministic snapshot of a session for replay.

    Replay baselines must be deterministic across environments.
    """

    def __init__(
        self,
        snapshot_id: str,
        session_dict: dict[str, Any],
        telemetry: list[dict[str, Any]],
        policy_decisions: list[dict[str, Any]],
    ):
        self.snapshot_id = snapshot_id
        self.session_dict = session_dict
        self.telemetry = telemetry
        self.policy_decisions = policy_decisions
        self.captured_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at": self.captured_at,
            "session": self.session_dict,
            "telemetry_count": len(self.telemetry),
            "policy_decision_count": len(self.policy_decisions),
            "telemetry": self.telemetry,
            "policy_decisions": self.policy_decisions,
        }

    def checksum(self) -> str:
        """Deterministic checksum for replay comparison."""
        # Exclude timestamps for determinism — only structure matters
        normalized = {
            "session_status": self.session_dict.get("status"),
            "session_objective": self.session_dict.get("objective"),
            "session_steps": [
                {"name": s.get("name"), "status": s.get("status")}
                for s in self.session_dict.get("steps", [])
            ],
            "policy_actions": [d.get("action") for d in self.policy_decisions],
            "telemetry_types": [t.get("event_type") for t in self.telemetry],
        }
        blob = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def save(self, snapshots_dir: Path) -> Path:
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        path = snapshots_dir / f"{self.snapshot_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path

    @classmethod
    def load(cls, path: Path) -> ReplaySnapshot | None:
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(
                snapshot_id=data["snapshot_id"],
                session_dict=data["session"],
                telemetry=data["telemetry"],
                policy_decisions=data["policy_decisions"],
            )
        except (json.JSONDecodeError, KeyError):
            return None


class ReplayHarness:
    """
    Replay-first E2E harness.

    Captures a session run as a snapshot, then replays it and
    verifies the outcome matches the baseline deterministically.
    """

    def __init__(self, snapshots_dir: Path | None = None):
        from archon.utils.paths import get_archon_home
        self.snapshots_dir = snapshots_dir or get_archon_home() / "snapshots"

    def capture(
        self,
        session_dict: dict[str, Any],
        collector: TelemetryCollector,
        policy_decisions: list[dict[str, Any]],
    ) -> ReplaySnapshot:
        """Capture current state as a replay snapshot."""
        session_id = session_dict.get("session_id", "unknown")
        snapshot = ReplaySnapshot(
            snapshot_id=f"snap-{session_id}-{uuid.uuid4().hex[:6]}",
            session_dict=session_dict,
            telemetry=[e.to_dict() for e in collector.envelopes],
            policy_decisions=policy_decisions,
        )
        return snapshot

    def compare(self, baseline: ReplaySnapshot, current: ReplaySnapshot) -> dict[str, Any]:
        """Compare two snapshots for replay determinism."""
        b_check = baseline.checksum()
        c_check = current.checksum()
        match = b_check == c_check

        result = {
            "deterministic": match,
            "baseline_checksum": b_check,
            "current_checksum": c_check,
        }

        if not match:
            result["diffs"] = self._diff_snapshots(baseline, current)

        return result

    def _diff_snapshots(
        self, baseline: ReplaySnapshot, current: ReplaySnapshot
    ) -> list[str]:
        diffs = []
        if baseline.session_dict.get("status") != current.session_dict.get("status"):
            diffs.append(
                f"status: {baseline.session_dict.get('status')} → {current.session_dict.get('status')}"
            )
        b_steps = len(baseline.session_dict.get("steps", []))
        c_steps = len(current.session_dict.get("steps", []))
        if b_steps != c_steps:
            diffs.append(f"step count: {b_steps} → {c_steps}")

        b_pols = len(baseline.policy_decisions)
        c_pols = len(current.policy_decisions)
        if b_pols != c_pols:
            diffs.append(f"policy decision count: {b_pols} → {c_pols}")

        return diffs
