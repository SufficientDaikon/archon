"""
Archon v3 Session Manager — Lifecycle orchestration with enforced state machine.

E2-S1: Client lifecycle state machine with restart and recovery policies.
E2-S2: Session lifecycle service (create, resume, send, abort, archive).
E2-S3: Link session and pipeline traces with correlation IDs.

Extends v2 PipelineState without breaking existing behavior.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

ARCHON_ROOT = Path(__file__).parent.parent.parent.parent


class SessionStatus(Enum):
    CREATED = "created"
    ACTIVE = "active"
    WAITING_TOOL = "waiting_tool"
    WAITING_PERMISSION = "waiting_permission"
    IDLE = "idle"
    RECOVERING = "recovering"
    ARCHIVED = "archived"
    ERROR = "error"


# Transition table from session.schema.yaml
_VALID_TRANSITIONS: dict[SessionStatus, set[SessionStatus]] = {
    SessionStatus.CREATED: {SessionStatus.ACTIVE},
    SessionStatus.ACTIVE: {
        SessionStatus.WAITING_TOOL,
        SessionStatus.WAITING_PERMISSION,
        SessionStatus.IDLE,
        SessionStatus.RECOVERING,
        SessionStatus.ERROR,
        SessionStatus.ARCHIVED,
    },
    SessionStatus.WAITING_TOOL: {SessionStatus.ACTIVE, SessionStatus.ERROR},
    SessionStatus.WAITING_PERMISSION: {SessionStatus.ACTIVE, SessionStatus.ERROR},
    SessionStatus.IDLE: {SessionStatus.ACTIVE, SessionStatus.ARCHIVED},
    SessionStatus.RECOVERING: {
        SessionStatus.ACTIVE,
        SessionStatus.ERROR,
        SessionStatus.ARCHIVED,
    },
    SessionStatus.ERROR: {SessionStatus.RECOVERING, SessionStatus.ARCHIVED},
    SessionStatus.ARCHIVED: set(),
}


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""


class Session:
    """
    v3 Session lifecycle with enforced state machine.

    Wraps v2 PipelineState for backward compatibility while adding:
    - Strict state transition enforcement
    - Correlation IDs for cross-trace linking
    - Recovery policies with configurable retry/backoff
    - Context handoff integrity
    - Accumulated state that grows, never shrinks
    """

    def __init__(
        self,
        session_id: str,
        status: SessionStatus,
        objective: str,
        pipeline_name: str,
        correlation_id: str,
        constraints: list[dict[str, Any]],
        created_at: str,
        updated_at: str,
        accumulated_state: dict[str, Any] | None = None,
        recovery_policy: dict[str, Any] | None = None,
        steps: list[dict[str, Any]] | None = None,
        deviations: list[dict[str, Any]] | None = None,
        event_log: list[dict[str, Any]] | None = None,
        recovery_attempts: int = 0,
    ):
        self.session_id = session_id
        self._status = status
        self.objective = objective
        self.pipeline_name = pipeline_name
        self.correlation_id = correlation_id
        self.constraints = constraints
        self.created_at = created_at
        self.updated_at = updated_at
        self.accumulated_state = accumulated_state or {
            "decisions": [],
            "constraints": [],
            "tech_stack": [],
            "context_briefs": [],
        }
        self.recovery_policy = recovery_policy or {
            "max_retries": 3,
            "backoff_strategy": "exponential",
            "preserve_on_crash": True,
        }
        self.steps = steps or []
        self.deviations = deviations or []
        self.event_log = event_log or []
        self.recovery_attempts = recovery_attempts

    @property
    def status(self) -> SessionStatus:
        return self._status

    # -- Lifecycle commands --------------------------------------------------

    @classmethod
    def create(
        cls,
        objective: str,
        pipeline_name: str,
        constraints: list[dict[str, Any]] | None = None,
        recovery_policy: dict[str, Any] | None = None,
    ) -> Session:
        """Create a new session in CREATED state."""
        now = datetime.now(timezone.utc).isoformat()
        session = cls(
            session_id=f"sess-{uuid.uuid4().hex[:12]}",
            status=SessionStatus.CREATED,
            objective=objective,
            pipeline_name=pipeline_name,
            correlation_id=f"corr-{uuid.uuid4().hex[:12]}",
            constraints=constraints or [],
            created_at=now,
            updated_at=now,
            recovery_policy=recovery_policy,
        )
        session._emit_event("session_created")
        return session

    def activate(self) -> None:
        """Transition to ACTIVE state."""
        self._transition(SessionStatus.ACTIVE)
        self._emit_event("session_activated")

    def wait_for_tool(self, tool_name: str) -> None:
        """Transition to WAITING_TOOL state."""
        self._transition(SessionStatus.WAITING_TOOL)
        self._emit_event("waiting_tool", {"tool": tool_name})

    def wait_for_permission(self, permission_id: str) -> None:
        """Transition to WAITING_PERMISSION."""
        self._transition(SessionStatus.WAITING_PERMISSION)
        self._emit_event("waiting_permission", {"permission_id": permission_id})

    def idle(self) -> None:
        """Transition to IDLE state."""
        self._transition(SessionStatus.IDLE)
        self._emit_event("session_idle")

    def complete(self) -> None:
        """Transition to ARCHIVED (completed) state."""
        self._transition(SessionStatus.ARCHIVED)
        self._emit_event("session_completed")

    def fail(self, error: str) -> None:
        """Transition to ERROR state."""
        self._transition(SessionStatus.ERROR)
        self._emit_event("session_error", {"error": error})

    def abort(self) -> None:
        """Force-archive from any error or idle state."""
        self._transition(SessionStatus.ARCHIVED)
        self._emit_event("session_aborted")

    def recover(self) -> bool:
        """
        Attempt recovery. Returns True if recovery initiated.

        Respects max_retries from recovery policy.
        """
        max_retries = self.recovery_policy.get("max_retries", 3)
        if self.recovery_attempts >= max_retries:
            self._emit_event("recovery_exhausted", {
                "attempts": self.recovery_attempts,
                "max": max_retries,
            })
            return False

        self._transition(SessionStatus.RECOVERING)
        self.recovery_attempts += 1
        self._emit_event("recovery_attempt", {
            "attempt": self.recovery_attempts,
            "max": max_retries,
        })
        return True

    def resume(self) -> None:
        """Resume from RECOVERING or IDLE → ACTIVE."""
        self._transition(SessionStatus.ACTIVE)
        self._emit_event("session_resumed")

    def send(self, step_name: str, result: dict[str, Any]) -> None:
        """Record a step result while ACTIVE."""
        if self._status != SessionStatus.ACTIVE:
            raise InvalidTransitionError(
                f"Cannot send in state {self._status.value} (must be active)"
            )
        self.steps.append({
            "name": step_name,
            "status": result.get("status", "completed"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": self.correlation_id,
            **result,
        })
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self._emit_event("step_recorded", {"step": step_name})

    # -- State accumulation (grows, never shrinks) ---------------------------

    def add_decision(self, decision: str) -> None:
        if decision not in self.accumulated_state["decisions"]:
            self.accumulated_state["decisions"].append(decision)

    def add_constraint(self, constraint: str) -> None:
        if constraint not in self.accumulated_state["constraints"]:
            self.accumulated_state["constraints"].append(constraint)

    # -- Correlation and tracing (E2-S3) ------------------------------------

    def link_pipeline_trace(self, pipeline_state_id: str) -> str:
        """Link this session to a v2 PipelineState via correlation ID."""
        self._emit_event("pipeline_linked", {
            "pipeline_state_id": pipeline_state_id,
            "correlation_id": self.correlation_id,
        })
        return self.correlation_id

    # -- Persistence --------------------------------------------------------

    def save(self, state_dir: Path | None = None) -> Path:
        """Persist session to disk."""
        state_dir = state_dir or Path.home() / ".copilot" / ".archon" / "sessions"
        state_dir.mkdir(parents=True, exist_ok=True)

        self.updated_at = datetime.now(timezone.utc).isoformat()

        path = state_dir / f"{self.session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return path

    @classmethod
    def load(cls, session_id: str, state_dir: Path | None = None) -> Session | None:
        """Load session from disk."""
        state_dir = state_dir or Path.home() / ".copilot" / ".archon" / "sessions"
        path = state_dir / f"{session_id}.json"

        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(
                session_id=data["session_id"],
                status=SessionStatus(data["status"]),
                objective=data["objective"],
                pipeline_name=data["pipeline_name"],
                correlation_id=data["correlation_id"],
                constraints=data.get("constraints", []),
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                accumulated_state=data.get("accumulated_state"),
                recovery_policy=data.get("recovery_policy"),
                steps=data.get("steps", []),
                deviations=data.get("deviations", []),
                event_log=data.get("event_log", []),
                recovery_attempts=data.get("recovery_attempts", 0),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    # -- Serialization ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "status": self._status.value,
            "objective": self.objective,
            "pipeline_name": self.pipeline_name,
            "correlation_id": self.correlation_id,
            "constraints": self.constraints,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "accumulated_state": self.accumulated_state,
            "recovery_policy": self.recovery_policy,
            "steps": self.steps,
            "deviations": self.deviations,
            "event_log": self.event_log,
            "recovery_attempts": self.recovery_attempts,
        }

    def context_checksum(self) -> str:
        """SHA-256 of serialized session for integrity verification."""
        blob = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    # -- Internal -----------------------------------------------------------

    def _transition(self, target: SessionStatus) -> None:
        """Enforce valid state transition."""
        allowed = _VALID_TRANSITIONS.get(self._status, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f"Invalid transition: {self._status.value} → {target.value} "
                f"(allowed: {[s.value for s in allowed]})"
            )
        self._status = target
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def _emit_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        """Append event to session log."""
        self.event_log.append({
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "status": self._status.value,
            "payload": payload or {},
        })
