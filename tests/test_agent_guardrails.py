"""
Archon v2.0 Test Suite — Agent Guardrails Tests

Tests that all agents (excluding _template) enforce structured guardrails
with proper schema, severity levels, and violation handling.
"""

import sys
from pathlib import Path

import pytest
import yaml

ARCHON_ROOT = Path(__file__).parent.parent

VALID_SEVERITIES = {"critical", "major", "minor"}
VALID_VIOLATIONS = {"halt", "warn", "log"}
VALID_ENFORCEMENT = {"strict", "standard"}

AGENT_DIRS = sorted([
    d for d in (ARCHON_ROOT / "agents").iterdir()
    if d.is_dir() and d.name != "_template"
])
AGENT_NAMES = [d.name for d in AGENT_DIRS]


def _load_manifest(agent_dir: Path) -> dict:
    """Load and return agent-manifest.yaml for a given agent directory."""
    with open(agent_dir / "agent-manifest.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Discovery ──────────────────────────────────────────────────────────────


class TestAgentDiscovery:
    """Verify agents are discoverable and have valid manifests."""

    def test_agents_directory_exists(self):
        assert (ARCHON_ROOT / "agents").is_dir()

    def test_at_least_nine_agents_found(self):
        assert len(AGENT_DIRS) >= 9, f"Expected ≥9 agents, found {len(AGENT_DIRS)}"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_manifest_file_exists(self, agent_dir):
        assert (agent_dir / "agent-manifest.yaml").exists(), \
            f"{agent_dir.name} missing agent-manifest.yaml"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_manifest_parses_as_dict(self, agent_dir):
        manifest = _load_manifest(agent_dir)
        assert isinstance(manifest, dict), f"{agent_dir.name} manifest is not a dict"


# ── Guardrail Enforcement Key ──────────────────────────────────────────────


class TestGuardrailEnforcement:
    """Test guardrail-enforcement key exists and has a valid value."""

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_has_guardrail_enforcement_key(self, agent_dir):
        manifest = _load_manifest(agent_dir)
        assert "guardrail-enforcement" in manifest, \
            f"{agent_dir.name} missing 'guardrail-enforcement'"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_enforcement_is_strict_or_standard(self, agent_dir):
        manifest = _load_manifest(agent_dir)
        value = manifest["guardrail-enforcement"]
        assert value in VALID_ENFORCEMENT, \
            f"{agent_dir.name} guardrail-enforcement={value!r}, expected {VALID_ENFORCEMENT}"


# ── Guardrails Structure ──────────────────────────────────────────────────


class TestGuardrailsStructure:
    """Test guardrails key contains must-not and must-do sub-keys."""

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_has_guardrails_key(self, agent_dir):
        manifest = _load_manifest(agent_dir)
        assert "guardrails" in manifest, f"{agent_dir.name} missing 'guardrails'"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_has_must_not_subkey(self, agent_dir):
        guardrails = _load_manifest(agent_dir)["guardrails"]
        assert "must-not" in guardrails, f"{agent_dir.name} missing guardrails.must-not"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_has_must_do_subkey(self, agent_dir):
        guardrails = _load_manifest(agent_dir)["guardrails"]
        assert "must-do" in guardrails, f"{agent_dir.name} missing guardrails.must-do"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_must_not_is_nonempty_list(self, agent_dir):
        must_not = _load_manifest(agent_dir)["guardrails"]["must-not"]
        assert isinstance(must_not, list) and len(must_not) > 0, \
            f"{agent_dir.name} must-not should be a non-empty list"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_must_do_is_nonempty_list(self, agent_dir):
        must_do = _load_manifest(agent_dir)["guardrails"]["must-do"]
        assert isinstance(must_do, list) and len(must_do) > 0, \
            f"{agent_dir.name} must-do should be a non-empty list"


# ── Rule Schema ────────────────────────────────────────────────────────────


class TestGuardrailRuleSchema:
    """Test that each guardrail rule has rule, severity, and on-violation."""

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_must_not_rules_schema(self, agent_dir):
        rules = _load_manifest(agent_dir)["guardrails"]["must-not"]
        for i, rule in enumerate(rules):
            assert "rule" in rule and isinstance(rule["rule"], str), \
                f"{agent_dir.name} must-not[{i}] missing or non-string 'rule'"
            assert rule.get("severity") in VALID_SEVERITIES, \
                f"{agent_dir.name} must-not[{i}] severity={rule.get('severity')!r}"
            assert rule.get("on-violation") in VALID_VIOLATIONS, \
                f"{agent_dir.name} must-not[{i}] on-violation={rule.get('on-violation')!r}"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_must_do_rules_schema(self, agent_dir):
        rules = _load_manifest(agent_dir)["guardrails"]["must-do"]
        for i, rule in enumerate(rules):
            assert "rule" in rule and isinstance(rule["rule"], str), \
                f"{agent_dir.name} must-do[{i}] missing or non-string 'rule'"
            assert rule.get("severity") in VALID_SEVERITIES, \
                f"{agent_dir.name} must-do[{i}] severity={rule.get('severity')!r}"
            assert rule.get("on-violation") in VALID_VIOLATIONS, \
                f"{agent_dir.name} must-do[{i}] on-violation={rule.get('on-violation')!r}"


# ── Critical Rules Policy ─────────────────────────────────────────────────


class TestCriticalRulesPolicy:
    """Every agent must have ≥1 critical rule, and critical → halt."""

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_at_least_one_critical_rule(self, agent_dir):
        guardrails = _load_manifest(agent_dir)["guardrails"]
        all_rules = guardrails["must-not"] + guardrails["must-do"]
        critical = [r for r in all_rules if r["severity"] == "critical"]
        assert len(critical) >= 1, f"{agent_dir.name} has zero critical rules"

    @pytest.mark.parametrize("agent_dir", AGENT_DIRS, ids=AGENT_NAMES)
    def test_critical_rules_enforce_halt(self, agent_dir):
        guardrails = _load_manifest(agent_dir)["guardrails"]
        all_rules = guardrails["must-not"] + guardrails["must-do"]
        for rule in all_rules:
            if rule["severity"] == "critical":
                assert rule["on-violation"] == "halt", (
                    f"{agent_dir.name} critical rule {rule['rule']!r} "
                    f"has on-violation={rule['on-violation']!r}, expected 'halt'"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
