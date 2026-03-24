"""
Archon v3 E4 Tests — Agent/Skill/MCP Expansion.

Tests:
- E4-S1: Agent capability profiles and mode-aware execution
- E4-S2: Skill manifest checks and deterministic precedence
- E4-S3: MCP connector routing with trust tiers and health policy
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.archon.core.agent_mcp import (
    AgentCapabilityProfile,
    MCPConnector,
    MCPConnectorManager,
    SkillManifestCheck,
    SkillManifestChecker,
)

ARCHON_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# E4-S1: Agent capability profiles
# ---------------------------------------------------------------------------

class TestAgentCapabilityProfile:
    """Agent profiles must enforce mode constraints."""

    def test_profile_creation(self):
        p = AgentCapabilityProfile(
            agent_name="implementer",
            modes=["plan", "implement"],
            skills=["backend-development", "django-expert"],
        )
        assert p.agent_name == "implementer"
        assert p.can_execute_in_mode("implement")
        assert not p.can_execute_in_mode("review")

    def test_from_manifest(self, tmp_path: Path):
        agent_dir = tmp_path / "test-agent"
        agent_dir.mkdir()
        manifest = agent_dir / "manifest.yaml"
        manifest.write_text(
            "name: test-agent\nmodes: [plan, review]\nskills: [backend]\n"
            "guardrails:\n  enforcement: strict\ntrust_tier: verified\n"
        )
        p = AgentCapabilityProfile.from_manifest(manifest)
        assert p.agent_name == "test-agent"
        assert p.can_execute_in_mode("plan")
        assert p.trust_tier == "verified"

    def test_serializes(self):
        p = AgentCapabilityProfile("test", ["implement"], ["skill-a"])
        d = p.to_dict()
        assert d["agent_name"] == "test"
        assert "modes" in d
        assert "skills" in d

    def test_loads_real_agents(self):
        """At least 9 agents should exist with manifests."""
        agents_dir = ARCHON_ROOT / "agents"
        if not agents_dir.exists():
            pytest.skip("agents directory not found")
        manifests = list(agents_dir.rglob("agent-manifest.yaml"))
        assert len(manifests) >= 9


# ---------------------------------------------------------------------------
# E4-S2: Skill manifest checks and precedence
# ---------------------------------------------------------------------------

class TestSkillManifestChecker:
    """Manifest checker must validate and compute precedence."""

    def test_valid_manifest(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "manifest.yaml").write_text(
            "name: my-skill\nversion: '1.0'\ndescription: A skill\ntags: [test]\ntier: verified\n"
        )
        checker = SkillManifestChecker()
        result = checker.check(skill_dir / "manifest.yaml")
        assert result.valid
        assert result.precedence_score == 75
        assert len(result.content_hash) == 64

    def test_missing_required_fields(self, tmp_path: Path):
        skill_dir = tmp_path / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "manifest.yaml").write_text("name: bad\n")
        checker = SkillManifestChecker()
        result = checker.check(skill_dir / "manifest.yaml")
        assert not result.valid
        assert any("version" in e for e in result.errors)

    def test_precedence_tiers(self, tmp_path: Path):
        checker = SkillManifestChecker()
        for tier, expected in [("core", 100), ("verified", 75), ("community", 50), ("user", 25)]:
            skill_dir = tmp_path / f"skill-{tier}"
            skill_dir.mkdir()
            (skill_dir / "manifest.yaml").write_text(
                f"name: skill-{tier}\nversion: '1.0'\ndescription: test\ntags: [t]\ntier: {tier}\n"
            )
            result = checker.check(skill_dir / "manifest.yaml")
            assert result.precedence_score == expected

    def test_conflict_resolution_deterministic(self):
        checker = SkillManifestChecker()
        checks = [
            SkillManifestCheck("zz-skill", True, [], "", 50),
            SkillManifestCheck("aa-skill", True, [], "", 75),
            SkillManifestCheck("mm-skill", True, [], "", 75),
            SkillManifestCheck("bb-skill", True, [], "", 100),
        ]
        resolved = checker.resolve_conflicts(checks)
        assert resolved[0].skill_name == "bb-skill"   # highest precedence
        assert resolved[1].skill_name == "aa-skill"    # same tier, alphabetical
        assert resolved[2].skill_name == "mm-skill"
        assert resolved[3].skill_name == "zz-skill"

    def test_check_all_real_skills(self):
        """All real skills must have manifests (spot check)."""
        skills_dir = ARCHON_ROOT / "skills"
        if not skills_dir.exists():
            pytest.skip("skills directory not found")
        checker = SkillManifestChecker()
        results = checker.check_all(skills_dir)
        assert len(results) >= 10  # at least 10 skills


# ---------------------------------------------------------------------------
# E4-S3: MCP Connector Manager
# ---------------------------------------------------------------------------

class TestMCPConnectorManager:
    """MCP routing must be deterministic and respect trust tiers."""

    def test_register_and_get(self):
        mgr = MCPConnectorManager()
        conn = MCPConnector("github", "mcp://github", "verified", "healthy", ["search", "pr"])
        mgr.register(conn)
        assert mgr.get("github") is not None
        assert mgr.get("nonexistent") is None

    def test_unregister(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("test", "mcp://test", "community"))
        assert mgr.unregister("test") is True
        assert mgr.unregister("test") is False

    def test_route_by_capability(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("gh", "mcp://gh", "verified", "healthy", ["search", "pr"]))
        mgr.register(MCPConnector("jira", "mcp://jira", "verified", "healthy", ["issues"]))

        result = mgr.route("search")
        assert result is not None
        assert result.name == "gh"

        result = mgr.route("issues")
        assert result is not None
        assert result.name == "jira"

    def test_route_respects_trust_tier(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("untrusted-srv", "mcp://x", "untrusted", "healthy", ["search"]))
        # Require verified — untrusted should not match
        result = mgr.route("search", min_tier="verified")
        assert result is None

    def test_route_prefers_higher_trust(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("comm", "mcp://c", "community", "healthy", ["search"]))
        mgr.register(MCPConnector("builtin", "mcp://b", "builtin", "healthy", ["search"]))
        result = mgr.route("search")
        assert result.name == "builtin"  # higher trust wins

    def test_route_skips_unhealthy(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("bad", "mcp://bad", "builtin", "unhealthy", ["search"]))
        mgr.register(MCPConnector("good", "mcp://good", "verified", "healthy", ["search"]))
        result = mgr.route("search")
        assert result.name == "good"

    def test_route_returns_none_when_no_match(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("srv", "mcp://srv", "verified", "healthy", ["pr"]))
        assert mgr.route("nonexistent-cap") is None

    def test_health_update(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("srv", "mcp://srv", "verified"))
        assert mgr.update_health("srv", "healthy") is True
        assert mgr.get("srv").health_status == "healthy"
        assert mgr.update_health("srv", "invalid") is False
        assert mgr.update_health("none", "healthy") is False

    def test_get_unhealthy(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("a", "mcp://a", "verified", "healthy", []))
        mgr.register(MCPConnector("b", "mcp://b", "verified", "unhealthy", []))
        mgr.register(MCPConnector("c", "mcp://c", "verified", "unhealthy", []))
        assert len(mgr.get_unhealthy()) == 2

    def test_get_by_tier(self):
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("a", "mcp://a", "builtin"))
        mgr.register(MCPConnector("b", "mcp://b", "verified"))
        mgr.register(MCPConnector("c", "mcp://c", "builtin"))
        assert len(mgr.get_by_tier("builtin")) == 2

    def test_routing_is_deterministic(self):
        """Same inputs must always produce same routing decision."""
        mgr = MCPConnectorManager()
        mgr.register(MCPConnector("a", "mcp://a", "verified", "healthy", ["x"]))
        mgr.register(MCPConnector("b", "mcp://b", "verified", "healthy", ["x"]))
        r1 = mgr.route("x")
        r2 = mgr.route("x")
        assert r1.name == r2.name  # deterministic
