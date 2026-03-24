"""
Archon Pipeline State Manager — Persistent state tracking for pipeline execution.

Implements the accumulated state pattern:
- State grows, never shrinks
- Decisions, constraints, and tech stack persist across phases
- JSON persistence for human readability and git-friendliness
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PipelineState:
    """
    Manages persistent state for a pipeline execution.

    State is accumulated (grows, never shrinks) and persisted as JSON
    at ~/.copilot/.archon/pipeline-states/
    """

    def __init__(
        self,
        state_id: str,
        pipeline_name: str,
        project_dir: str,
        status: str = "pending",
        steps: list[dict[str, Any]] | None = None,
        accumulated: dict[str, Any] | None = None,
        deviations: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        state_dir: Path | None = None,
    ):
        self.state_id = state_id
        self.pipeline_name = pipeline_name
        self.project_dir = project_dir
        self.status = status
        self.steps: list[dict[str, Any]] = steps or []
        self.accumulated: dict[str, Any] = accumulated or {
            "decisions": [],
            "constraints": [],
            "tech_stack": [],
            "context_briefs": [],
        }
        self.deviations: list[dict[str, Any]] = deviations or []
        self.metadata: dict[str, Any] = metadata or {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_duration_ms": 0,
        }
        self._state_dir = state_dir

    @classmethod
    def create(cls, pipeline_name: str, project_dir: str) -> PipelineState:
        """Create a new pipeline state."""
        state_id = f"{pipeline_name}-{uuid.uuid4().hex[:8]}"
        state = cls(
            state_id=state_id,
            pipeline_name=pipeline_name,
            project_dir=project_dir,
        )
        state.save()
        return state

    @classmethod
    def load(cls, state_id: str, state_dir: Path | None = None) -> PipelineState | None:
        """Load pipeline state from disk."""
        state_dir = state_dir or Path.home() / ".copilot" / ".archon" / "pipeline-states"
        state_file = state_dir / f"{state_id}.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return cls(
                state_id=data.get("state_id", state_id),
                pipeline_name=data.get("pipeline_name", ""),
                project_dir=data.get("project_dir", "."),
                status=data.get("status", "pending"),
                steps=data.get("steps", []),
                accumulated=data.get("accumulated", {}),
                deviations=data.get("deviations", []),
                metadata=data.get("metadata", {}),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def save(self, state_dir: Path | None = None) -> Path:
        """Persist state to disk as JSON."""
        state_dir = state_dir or self._state_dir or Path.home() / ".copilot" / ".archon" / "pipeline-states"
        self._state_dir = state_dir
        state_dir.mkdir(parents=True, exist_ok=True)

        self.metadata["updated_at"] = datetime.now(timezone.utc).isoformat()

        state_file = state_dir / f"{self.state_id}.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        return state_file

    def update_status(self, new_status: str) -> None:
        """Update pipeline status and persist."""
        self.status = new_status
        self.save()

    def record_step(
        self,
        step_name: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record a step execution result."""
        step_record = {
            "name": step_name,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if details:
            step_record.update(details)

        # Update existing step record or append new one
        existing_idx = None
        for i, s in enumerate(self.steps):
            if s.get("name") == step_name:
                existing_idx = i
                break

        if existing_idx is not None:
            self.steps[existing_idx] = step_record
        else:
            self.steps.append(step_record)

        self.save()

    def record_deviation(
        self,
        description: str,
        severity: str = "major",
        step: str = "",
        agent: str = "",
    ) -> str:
        """Record a deviation from the spec/plan."""
        deviation_id = f"DEV-{len(self.deviations) + 1:03d}"
        deviation = {
            "id": deviation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "agent": agent,
            "description": description,
            "severity": severity,
            "status": "requested",
        }
        self.deviations.append(deviation)
        self.save()
        return deviation_id

    def add_decision(self, decision: str) -> None:
        """Add a decision to accumulated state (grows, never shrinks)."""
        if decision not in self.accumulated["decisions"]:
            self.accumulated["decisions"].append(decision)
            self.save()

    def add_constraint(self, constraint: str) -> None:
        """Add a constraint to accumulated state."""
        if constraint not in self.accumulated["constraints"]:
            self.accumulated["constraints"].append(constraint)
            self.save()

    def add_tech_stack(self, tech: str) -> None:
        """Add a technology to the accumulated tech stack."""
        if tech not in self.accumulated["tech_stack"]:
            self.accumulated["tech_stack"].append(tech)
            self.save()

    def add_context_brief(self, brief: str) -> None:
        """Add a context brief from curation step."""
        self.accumulated["context_briefs"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "brief": brief,
        })
        self.save()

    def completed_step_names(self) -> list[str]:
        """Get list of completed step names."""
        return [
            s["name"] for s in self.steps
            if s.get("status") == "completed"
        ]

    def current_step(self) -> str | None:
        """Get the name of the currently running step."""
        for s in self.steps:
            if s.get("status") == "running":
                return s["name"]
        return None

    def get_health_score(self) -> int:
        """
        Calculate pipeline health score (0-100).

        Formula: 100 - CRITICAL×20 - HIGH×10 - MEDIUM×5 - LOW×1
        """
        score = 100
        for deviation in self.deviations:
            severity = deviation.get("severity", "minor")
            if severity == "critical":
                score -= 20
            elif severity == "major":
                score -= 10
            elif severity == "minor":
                score -= 5

        for step in self.steps:
            if step.get("status") == "failed":
                score -= 10

        return max(0, min(100, score))

    def to_dict(self) -> dict[str, Any]:
        """Serialize state to dict."""
        return {
            "state_id": self.state_id,
            "pipeline_name": self.pipeline_name,
            "project_dir": self.project_dir,
            "status": self.status,
            "steps": self.steps,
            "accumulated": self.accumulated,
            "deviations": self.deviations,
            "metadata": self.metadata,
            "health_score": self.get_health_score(),
        }

    def __repr__(self) -> str:
        completed = len(self.completed_step_names())
        total = len(self.steps)
        return (
            f"PipelineState('{self.state_id}', status={self.status}, "
            f"steps={completed}/{total}, health={self.get_health_score()})"
        )
