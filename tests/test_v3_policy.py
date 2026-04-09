"""
Archon v3 E3 Tests — Policy-Routed Tool Hook Permission Flow.

Tests:
- E3-S1: Central policy engine routes all tool/hook decisions
- E3-S2: Schema validation before every tool invocation
- E3-S3: Policy decisions are machine-readable, auditable, and replayable
"""

from __future__ import annotations

import pytest

from archon.core.policy_engine import (
    PermissionRule,
    PolicyDecision,
    PolicyEngine,
)


# ---------------------------------------------------------------------------
# E3-S1: Central policy engine
# ---------------------------------------------------------------------------

class TestPolicyEngineBasics:
    """Policy engine must produce a decision for every evaluation."""

    def test_default_deny_when_no_rules(self):
        engine = PolicyEngine()
        decision = engine.evaluate("Read", "sess-abc", "corr-xyz")
        assert decision.action == "deny"
        assert decision.policy_id == "default-deny"

    def test_allow_rule_matches(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-read-allow",
            scope="tool",
            trust_tier="community",
            action="allow",
        ))
        decision = engine.evaluate("Read", "sess-abc", "corr-xyz", trust_tier="community")
        assert decision.is_allowed

    def test_deny_rule_matches(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-bash-deny",
            scope="tool",
            trust_tier="untrusted",
            action="deny",
        ))
        decision = engine.evaluate("Bash", "sess-abc", "corr-xyz", trust_tier="untrusted")
        assert decision.action == "deny"

    def test_escalate_rule(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-write-escalate",
            scope="tool",
            trust_tier="community",
            action="escalate",
        ))
        decision = engine.evaluate("Write", "sess-abc", "corr-xyz")
        assert decision.action == "escalate"

    def test_prompt_action_becomes_escalate(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-prompt",
            scope="tool",
            trust_tier="community",
            action="prompt",
        ))
        decision = engine.evaluate("Edit", "sess-abc", "corr-xyz")
        assert decision.action == "escalate"

    def test_first_matching_rule_wins(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="deny-first", scope="tool", trust_tier="community", action="deny",
        ))
        engine.add_rule(PermissionRule(
            id="allow-second", scope="tool", trust_tier="community", action="allow",
        ))
        decision = engine.evaluate("Tool", "sess-abc", "corr-xyz")
        assert decision.action == "deny"
        assert decision.policy_id == "deny-first"


class TestTrustTierPrecedence:
    """Higher trust tiers must satisfy lower tier requirements."""

    def test_builtin_satisfies_community(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-comm", scope="tool", trust_tier="community", action="allow",
        ))
        decision = engine.evaluate("Tool", "sess-a", "corr-a", trust_tier="builtin")
        assert decision.is_allowed

    def test_untrusted_rejected_for_verified_rule(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-verified", scope="tool", trust_tier="verified", action="allow",
        ))
        decision = engine.evaluate("Tool", "sess-a", "corr-a", trust_tier="untrusted")
        assert decision.action == "deny"  # falls through to default deny

    def test_verified_satisfies_community(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-comm", scope="tool", trust_tier="community", action="allow",
        ))
        decision = engine.evaluate("Tool", "sess-a", "corr-a", trust_tier="verified")
        assert decision.is_allowed


class TestConditionEvaluation:
    """Conditions must all match (AND logic)."""

    def test_condition_eq_matches(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-cond",
            scope="tool",
            trust_tier="community",
            action="allow",
            conditions=[{"field": "mode", "operator": "eq", "value": "read"}],
        ))
        decision = engine.evaluate(
            "Tool", "sess-a", "corr-a",
            arguments={"mode": "read"},
        )
        assert decision.is_allowed

    def test_condition_eq_fails(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-cond",
            scope="tool",
            trust_tier="community",
            action="allow",
            conditions=[{"field": "mode", "operator": "eq", "value": "read"}],
        ))
        decision = engine.evaluate(
            "Tool", "sess-a", "corr-a",
            arguments={"mode": "write"},
        )
        assert decision.action == "deny"

    def test_condition_neq(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-neq",
            scope="tool",
            trust_tier="community",
            action="allow",
            conditions=[{"field": "env", "operator": "neq", "value": "production"}],
        ))
        decision = engine.evaluate(
            "Tool", "sess-a", "corr-a",
            arguments={"env": "staging"},
        )
        assert decision.is_allowed

    def test_multiple_conditions_and_logic(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-multi",
            scope="tool",
            trust_tier="community",
            action="allow",
            conditions=[
                {"field": "scope", "operator": "eq", "value": "read"},
                {"field": "target", "operator": "neq", "value": "/etc/passwd"},
            ],
        ))
        # Both conditions match
        d = engine.evaluate("Tool", "s", "c", arguments={"scope": "read", "target": "/tmp"})
        assert d.is_allowed

        # Second condition fails
        d = engine.evaluate("Tool", "s", "c", arguments={"scope": "read", "target": "/etc/passwd"})
        assert d.action == "deny"


# ---------------------------------------------------------------------------
# E3-S2: Schema validation before tool invocation
# ---------------------------------------------------------------------------

class TestSchemaValidation:
    """Schema validation must block invocations with invalid arguments."""

    def test_missing_required_arg_denied(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-allow", scope="tool", trust_tier="community", action="allow",
        ))
        engine.register_tool_schema("Read", {
            "required": ["file_path"],
            "properties": {"file_path": {"type": "string"}},
        })
        decision = engine.evaluate("Read", "sess-a", "corr-a", arguments={})
        assert decision.action == "deny"
        assert "file_path" in decision.rationale

    def test_valid_args_allowed(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-allow", scope="tool", trust_tier="community", action="allow",
        ))
        engine.register_tool_schema("Read", {
            "required": ["file_path"],
            "properties": {"file_path": {"type": "string"}},
        })
        decision = engine.evaluate(
            "Read", "sess-a", "corr-a",
            arguments={"file_path": "/tmp/test.txt"},
        )
        assert decision.is_allowed

    def test_wrong_type_denied(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-allow", scope="tool", trust_tier="community", action="allow",
        ))
        engine.register_tool_schema("Read", {
            "required": ["file_path"],
            "properties": {"file_path": {"type": "string"}},
        })
        decision = engine.evaluate(
            "Read", "sess-a", "corr-a",
            arguments={"file_path": 123},
        )
        assert decision.action == "deny"
        assert "string" in decision.rationale.lower()

    def test_pattern_validation(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-allow", scope="tool", trust_tier="community", action="allow",
        ))
        engine.register_tool_schema("SessionLookup", {
            "required": ["session_id"],
            "properties": {"session_id": {"type": "string", "pattern": "^sess-[a-f0-9]{8,}$"}},
        })
        # Bad ID
        d = engine.evaluate("SessionLookup", "s", "c", arguments={"session_id": "bad-id"})
        assert d.action == "deny"

        # Good ID
        d = engine.evaluate("SessionLookup", "s", "c", arguments={"session_id": "sess-abcdef01"})
        assert d.is_allowed

    def test_enum_validation(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-allow", scope="tool", trust_tier="community", action="allow",
        ))
        engine.register_tool_schema("SetLevel", {
            "required": ["level"],
            "properties": {"level": {"type": "string", "enum": ["info", "warn", "error"]}},
        })
        d = engine.evaluate("SetLevel", "s", "c", arguments={"level": "debug"})
        assert d.action == "deny"

        d = engine.evaluate("SetLevel", "s", "c", arguments={"level": "info"})
        assert d.is_allowed

    def test_no_schema_passes_through(self):
        """Tools without registered schemas are not blocked by schema validation."""
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="perm-allow", scope="tool", trust_tier="community", action="allow",
        ))
        decision = engine.evaluate("UnknownTool", "sess-a", "corr-a", arguments={"anything": True})
        assert decision.is_allowed


# ---------------------------------------------------------------------------
# E3-S3: Policy decision artifacts and audit
# ---------------------------------------------------------------------------

class TestPolicyDecisionArtifacts:
    """Every evaluation must produce a machine-readable artifact."""

    def test_decision_has_required_fields(self):
        engine = PolicyEngine()
        decision = engine.evaluate("Read", "sess-a", "corr-a")
        d = decision.to_dict()
        assert "decision_id" in d
        assert "action" in d
        assert "rationale" in d
        assert "policy_id" in d
        assert "tool_name" in d
        assert "session_id" in d
        assert "correlation_id" in d
        assert "timestamp" in d

    def test_decision_id_format(self):
        engine = PolicyEngine()
        decision = engine.evaluate("Read", "sess-a", "corr-a")
        assert decision.decision_id.startswith("pd-")

    def test_audit_log_records_all_decisions(self):
        engine = PolicyEngine()
        engine.evaluate("Read", "sess-1", "corr-1")
        engine.evaluate("Write", "sess-1", "corr-1")
        engine.evaluate("Bash", "sess-2", "corr-2")
        assert len(engine.audit_log) == 3

    def test_filter_by_session(self):
        engine = PolicyEngine()
        engine.evaluate("Read", "sess-1", "corr-1")
        engine.evaluate("Write", "sess-1", "corr-1")
        engine.evaluate("Bash", "sess-2", "corr-2")
        sess1_decisions = engine.get_decisions_for_session("sess-1")
        assert len(sess1_decisions) == 2
        assert all(d.session_id == "sess-1" for d in sess1_decisions)

    def test_denied_decisions_queryable(self):
        engine = PolicyEngine()
        engine.evaluate("Read", "sess-1", "corr-1")  # deny (no rules)
        engine.add_rule(PermissionRule(
            id="allow-all", scope="tool", trust_tier="community", action="allow",
        ))
        engine.evaluate("Write", "sess-1", "corr-1")  # allow
        denied = engine.get_denied_decisions()
        assert len(denied) == 1
        assert denied[0].tool_name == "Read"

    def test_conditions_evaluated_recorded(self):
        engine = PolicyEngine()
        engine.add_rule(PermissionRule(
            id="rule-1", scope="tool", trust_tier="community", action="allow",
            conditions=[{"field": "x", "operator": "eq", "value": 1}],
        ))
        d = engine.evaluate("Tool", "s", "c", arguments={"x": 1})
        assert len(d.conditions_evaluated) > 0

    def test_decision_is_replayable(self):
        """Denied decisions serialized form contains all info needed for replay."""
        engine = PolicyEngine()
        decision = engine.evaluate("Bash", "sess-1", "corr-1", arguments={"cmd": "rm -rf /"})
        d = decision.to_dict()
        assert d["action"] == "deny"
        assert d["tool_name"] == "Bash"
        assert d["session_id"] == "sess-1"
        assert d["correlation_id"] == "corr-1"
        assert isinstance(d["conditions_evaluated"], list)
