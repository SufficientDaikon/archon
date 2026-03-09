"""Registry loader — parses omniskill.yaml and component manifests.

The registry is the single source of truth for every skill, agent, bundle,
and pipeline in the framework (FR-062, FR-063).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from omniskill.utils.paths import get_omniskill_root


# ── Data classes ────────────────────────────────────────────────

@dataclass
class Skill:
    name: str
    path: str
    version: str = "0.0.0"
    description: str = ""
    author: str = ""
    tags: list[str] = field(default_factory=list)
    priority: str = "P2"
    platforms: list[str] = field(default_factory=list)
    triggers: dict = field(default_factory=dict)
    # loaded from manifest.yaml on demand
    _manifest: dict | None = field(default=None, repr=False)


@dataclass
class Agent:
    name: str
    path: str
    version: str = "0.0.0"
    role: str = ""
    description: str = ""
    _manifest: dict | None = field(default=None, repr=False)


@dataclass
class Bundle:
    name: str
    path: str
    skills: list[str] = field(default_factory=list)
    version: str = "0.0.0"
    description: str = ""
    _manifest: dict | None = field(default=None, repr=False)


@dataclass
class Pipeline:
    name: str
    path: str
    trigger: str = ""
    version: str = "0.0.0"
    description: str = ""
    steps: list[dict] = field(default_factory=list)
    _manifest: dict | None = field(default=None, repr=False)


# ── Registry class ──────────────────────────────────────────────

class Registry:
    """Loads and caches the OMNISKILL root manifest and component manifests."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or get_omniskill_root()
        self._raw: dict[str, Any] = {}
        self.skills: list[Skill] = []
        self.agents: list[Agent] = []
        self.bundles: list[Bundle] = []
        self.pipelines: list[Pipeline] = []
        self.platforms_config: list[dict] = []
        self.name: str = ""
        self.version: str = ""
        self._loaded = False

    # ── loading ─────────────────────────────────────────────────

    def load(self) -> None:
        """Parse ``omniskill.yaml`` and populate component lists."""
        registry_path = self.root / "omniskill.yaml"
        if not registry_path.exists():
            raise FileNotFoundError(
                f"Registry not found at {registry_path}.\n"
                "Set OMNISKILL_ROOT to the directory containing omniskill.yaml "
                "or run from inside the omniskill repository."
            )

        with open(registry_path, "r", encoding="utf-8") as fh:
            self._raw = yaml.safe_load(fh) or {}

        self.name = self._raw.get("name", "omniskill")
        self.version = self._raw.get("version", "0.0.0")

        # Skills
        for entry in self._raw.get("skills", []):
            self.skills.append(Skill(
                name=entry["name"],
                path=entry.get("path", f"skills/{entry['name']}"),
                version=entry.get("version", "1.0.0"),
                tags=entry.get("tags", []),
                priority=entry.get("priority", "P2"),
            ))

        # Agents
        for entry in self._raw.get("agents", []):
            self.agents.append(Agent(
                name=entry["name"],
                path=entry.get("path", f"agents/{entry['name']}"),
            ))

        # Bundles
        for entry in self._raw.get("bundles", []):
            self.bundles.append(Bundle(
                name=entry["name"],
                path=entry.get("path", f"bundles/{entry['name']}"),
                skills=entry.get("skills", []),
            ))

        # Pipelines
        for entry in self._raw.get("pipelines", []):
            self.pipelines.append(Pipeline(
                name=entry["name"],
                path=entry.get("path", ""),
                trigger=entry.get("trigger", ""),
            ))

        # Platforms
        self.platforms_config = self._raw.get("platforms", [])
        self._loaded = True

    def ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    # ── lookups ─────────────────────────────────────────────────

    def find_skill(self, name: str) -> Skill | None:
        self.ensure_loaded()
        for s in self.skills:
            if s.name == name:
                return s
        return None

    def find_agent(self, name: str) -> Agent | None:
        self.ensure_loaded()
        for a in self.agents:
            if a.name == name:
                return a
        return None

    def find_bundle(self, name: str) -> Bundle | None:
        self.ensure_loaded()
        for b in self.bundles:
            if b.name == name:
                return b
        return None

    def find_pipeline(self, name: str) -> Pipeline | None:
        self.ensure_loaded()
        for p in self.pipelines:
            if p.name == name:
                return p
        return None

    def find_component(self, name: str) -> tuple[str, Any] | None:
        """Find any component by name. Returns (type, component) or None."""
        self.ensure_loaded()
        s = self.find_skill(name)
        if s:
            return ("skill", s)
        a = self.find_agent(name)
        if a:
            return ("agent", a)
        b = self.find_bundle(name)
        if b:
            return ("bundle", b)
        p = self.find_pipeline(name)
        if p:
            return ("pipeline", p)
        return None

    def similar_names(self, query: str, limit: int = 5) -> list[str]:
        """Return component names that are similar to *query* (fuzzy match)."""
        self.ensure_loaded()
        all_names = (
            [s.name for s in self.skills]
            + [a.name for a in self.agents]
            + [b.name for b in self.bundles]
            + [p.name for p in self.pipelines]
        )
        query_lower = query.lower()
        scored: list[tuple[float, str]] = []
        for n in all_names:
            n_lower = n.lower()
            # simple relevance: substring match gets high score, shared prefix, shared words
            score = 0.0
            if query_lower in n_lower:
                score += 10.0
            if n_lower in query_lower:
                score += 8.0
            # common prefix
            prefix_len = len(os.path.commonprefix([query_lower, n_lower]))
            score += prefix_len * 0.5
            # word overlap
            q_words = set(re.split(r"[-_ ]", query_lower))
            n_words = set(re.split(r"[-_ ]", n_lower))
            score += len(q_words & n_words) * 3.0
            if score > 0:
                scored.append((score, n))
        scored.sort(key=lambda x: -x[0])
        return [n for _, n in scored[:limit]]

    # ── manifest loading (detailed info) ────────────────────────

    def load_skill_manifest(self, skill: Skill) -> dict:
        """Load and cache the full manifest.yaml for a skill."""
        if skill._manifest is not None:
            return skill._manifest
        manifest_path = self.root / skill.path / "manifest.yaml"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as fh:
                    skill._manifest = yaml.safe_load(fh) or {}
            except Exception:
                skill._manifest = {}
        else:
            skill._manifest = {}
        # Back-fill fields
        skill.description = skill._manifest.get("description", skill.description)
        skill.author = skill._manifest.get("author", skill.author)
        skill.platforms = skill._manifest.get("platforms", skill.platforms)
        skill.tags = skill._manifest.get("tags", skill.tags) or skill.tags
        skill.priority = skill._manifest.get("priority", skill.priority)
        skill.triggers = skill._manifest.get("triggers", skill.triggers)
        return skill._manifest

    def load_agent_manifest(self, agent: Agent) -> dict:
        if agent._manifest is not None:
            return agent._manifest
        manifest_path = self.root / agent.path / "agent-manifest.yaml"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as fh:
                    agent._manifest = yaml.safe_load(fh) or {}
            except Exception:
                agent._manifest = {}
        else:
            agent._manifest = {}
        agent.version = agent._manifest.get("version", agent.version)
        agent.role = agent._manifest.get("role", agent.role)
        agent.description = agent._manifest.get("description", agent.description)
        return agent._manifest

    def load_bundle_manifest(self, bundle: Bundle) -> dict:
        if bundle._manifest is not None:
            return bundle._manifest
        manifest_path = self.root / bundle.path / "bundle.yaml"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as fh:
                    bundle._manifest = yaml.safe_load(fh) or {}
            except Exception:
                bundle._manifest = {}
        else:
            bundle._manifest = {}
        bundle.version = bundle._manifest.get("version", bundle.version)
        bundle.description = bundle._manifest.get("description", bundle.description)
        return bundle._manifest

    def load_pipeline_manifest(self, pipeline: Pipeline) -> dict:
        if pipeline._manifest is not None:
            return pipeline._manifest
        manifest_path = self.root / pipeline.path
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as fh:
                    pipeline._manifest = yaml.safe_load(fh) or {}
            except Exception:
                pipeline._manifest = {}
        else:
            pipeline._manifest = {}
        pipeline.version = pipeline._manifest.get("version", pipeline.version)
        pipeline.description = pipeline._manifest.get("description", pipeline.description)
        pipeline.steps = pipeline._manifest.get("steps", pipeline.steps)
        return pipeline._manifest


# Need os for commonprefix in similar_names
import os  # noqa: E402 — kept at end to avoid circular-import issues with paths.py
