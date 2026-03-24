"""
Archon v3 Agent/Skill/MCP Expansion — Deterministic routing and trust.

E4-S1: Agent capability profiles and mode-aware execution templates.
E4-S2: Signed skill manifest checks and deterministic precedence rules.
E4-S3: MCP connector manager with trust tiers and health policy.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ARCHON_ROOT = Path(__file__).parent.parent.parent.parent


# ---------------------------------------------------------------------------
# E4-S1: Agent Capability Profiles
# ---------------------------------------------------------------------------

@dataclass
class AgentCapabilityProfile:
    """Runtime profile for an agent's capabilities and mode constraints."""
    agent_name: str
    modes: list[str]  # e.g., ["plan", "implement", "review"]
    skills: list[str]  # skill IDs this agent can invoke
    guardrails: dict[str, Any] = field(default_factory=dict)
    max_concurrent_tools: int = 5
    trust_tier: str = "verified"

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> AgentCapabilityProfile:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(
            agent_name=data.get("name", manifest_path.parent.name),
            modes=data.get("modes", ["implement"]),
            skills=data.get("skills", []),
            guardrails=data.get("guardrails", {}),
            max_concurrent_tools=data.get("max_concurrent_tools", 5),
            trust_tier=data.get("trust_tier", "verified"),
        )

    def can_execute_in_mode(self, mode: str) -> bool:
        return mode in self.modes

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "modes": self.modes,
            "skills": self.skills,
            "guardrails": self.guardrails,
            "max_concurrent_tools": self.max_concurrent_tools,
            "trust_tier": self.trust_tier,
        }


# ---------------------------------------------------------------------------
# E4-S2: Skill Manifest Checker
# ---------------------------------------------------------------------------

@dataclass
class SkillManifestCheck:
    """Result of checking a skill manifest."""
    skill_name: str
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    content_hash: str = ""
    precedence_score: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "valid": self.valid,
            "errors": self.errors,
            "content_hash": self.content_hash,
            "precedence_score": self.precedence_score,
        }


class SkillManifestChecker:
    """
    Validates skill manifests and computes deterministic precedence.

    Precedence rules (highest to lowest):
    1. Core skills (bundled with Archon) — precedence 100
    2. Verified skills (signed, from registry) — precedence 75
    3. Community skills (reviewed) — precedence 50
    4. User skills (local, unverified) — precedence 25
    """

    REQUIRED_FIELDS = {"name", "version", "description", "tags"}
    PRECEDENCE_TIERS = {
        "core": 100,
        "verified": 75,
        "community": 50,
        "user": 25,
    }

    def check(self, manifest_path: Path) -> SkillManifestCheck:
        """Validate a single skill manifest."""
        result = SkillManifestCheck(skill_name=manifest_path.parent.name)

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                raw = f.read()
                data = yaml.safe_load(raw)
        except Exception as e:
            result.valid = False
            result.errors.append(f"Cannot parse: {e}")
            return result

        if not isinstance(data, dict):
            result.valid = False
            result.errors.append("Manifest root must be a mapping")
            return result

        # Required fields
        for req in self.REQUIRED_FIELDS:
            if req not in data:
                result.valid = False
                result.errors.append(f"Missing required field: '{req}'")

        # Content hash for integrity
        result.content_hash = hashlib.sha256(raw.encode()).hexdigest()

        # Precedence from tier
        tier = data.get("tier", "user")
        result.precedence_score = self.PRECEDENCE_TIERS.get(tier, 25)

        return result

    def check_all(self, skills_dir: Path) -> list[SkillManifestCheck]:
        """Check all skill manifests in directory."""
        results = []
        for manifest in sorted(skills_dir.rglob("manifest.yaml")):
            results.append(self.check(manifest))
        return results

    def resolve_conflicts(self, checks: list[SkillManifestCheck]) -> list[SkillManifestCheck]:
        """Sort by deterministic precedence (highest first, then alphabetical)."""
        return sorted(
            checks,
            key=lambda c: (-c.precedence_score, c.skill_name),
        )


# ---------------------------------------------------------------------------
# E4-S3: MCP Connector Manager
# ---------------------------------------------------------------------------

@dataclass
class MCPConnector:
    """A single MCP server connector."""
    name: str
    uri: str
    trust_tier: str  # builtin, verified, community, untrusted
    health_status: str = "unknown"  # healthy, degraded, unhealthy, unknown
    capabilities: list[str] = field(default_factory=list)
    last_health_check: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "uri": self.uri,
            "trust_tier": self.trust_tier,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "last_health_check": self.last_health_check,
        }


class MCPConnectorManager:
    """
    Manages MCP server connections with trust tiers and health policies.

    Health policy:
    - Healthy: all checks pass, routing allowed
    - Degraded: some checks fail, routing with warning
    - Unhealthy: critical checks fail, routing blocked
    """

    TIER_ORDER = ["builtin", "verified", "community", "untrusted"]

    def __init__(self):
        self._connectors: dict[str, MCPConnector] = {}

    def register(self, connector: MCPConnector) -> None:
        self._connectors[connector.name] = connector

    def unregister(self, name: str) -> bool:
        return self._connectors.pop(name, None) is not None

    def get(self, name: str) -> MCPConnector | None:
        return self._connectors.get(name)

    @property
    def connectors(self) -> list[MCPConnector]:
        return list(self._connectors.values())

    def route(self, capability: str, min_tier: str = "community") -> MCPConnector | None:
        """
        Route to the highest-trust healthy connector that has the capability.

        Returns None if no suitable connector found.
        """
        candidates = []
        for conn in self._connectors.values():
            if capability in conn.capabilities and self._tier_satisfies(conn.trust_tier, min_tier):
                if conn.health_status in ("healthy", "degraded"):
                    candidates.append(conn)

        if not candidates:
            return None

        # Sort by trust tier (highest first), then name for determinism
        candidates.sort(key=lambda c: (self.TIER_ORDER.index(c.trust_tier), c.name))
        return candidates[0]

    def update_health(self, name: str, status: str) -> bool:
        """Update a connector's health status."""
        conn = self._connectors.get(name)
        if conn is None:
            return False
        if status not in ("healthy", "degraded", "unhealthy", "unknown"):
            return False
        conn.health_status = status
        return True

    def get_unhealthy(self) -> list[MCPConnector]:
        return [c for c in self._connectors.values() if c.health_status == "unhealthy"]

    def get_by_tier(self, tier: str) -> list[MCPConnector]:
        return [c for c in self._connectors.values() if c.trust_tier == tier]

    def _tier_satisfies(self, connector_tier: str, required_tier: str) -> bool:
        try:
            conn_idx = self.TIER_ORDER.index(connector_tier)
            req_idx = self.TIER_ORDER.index(required_tier)
            return conn_idx <= req_idx
        except ValueError:
            return False
