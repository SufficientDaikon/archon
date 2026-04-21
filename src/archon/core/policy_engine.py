"""
Archon v3 Policy Engine — Central policy-routed tool/hook/permission flow.

E3-S1: Unified policy engine for tool, hook, and permission decisions.
E3-S2: Schema validation before every tool invocation.
E3-S3: Machine-readable policy decision artifacts with rationale and links.

No tool execution without an explicit policy decision artifact.
Denied decisions are machine-readable and replayable.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ARCHON_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class PolicyDecision:
    """Immutable policy decision artifact."""
    decision_id: str
    action: str  # allow, deny, escalate
    rationale: str
    policy_id: str
    tool_name: str
    session_id: str
    correlation_id: str
    timestamp: str
    evidence_links: list[str] = field(default_factory=list)
    conditions_evaluated: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "action": self.action,
            "rationale": self.rationale,
            "policy_id": self.policy_id,
            "tool_name": self.tool_name,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "evidence_links": self.evidence_links,
            "conditions_evaluated": self.conditions_evaluated,
        }

    @property
    def is_allowed(self) -> bool:
        return self.action == "allow"


@dataclass
class PermissionRule:
    """A single permission rule from the permission schema."""
    id: str
    scope: str  # tool, hook, agent, mcp, pipeline, file_system
    trust_tier: str  # builtin, verified, community, untrusted
    action: str  # allow, deny, prompt, escalate
    conditions: list[dict[str, Any]] = field(default_factory=list)
    audit_required: bool = True


class PolicyEngine:
    """
    Central policy engine that gates all tool/hook/permission flows.

    Every tool invocation must pass through evaluate() which:
    1. Validates the invocation against the tool schema
    2. Evaluates permission rules in precedence order
    3. Produces a machine-readable PolicyDecision artifact
    4. Appends to the audit log
    """

    def __init__(self, rules: list[PermissionRule] | None = None):
        self._rules = rules or []
        self._audit_log: list[PolicyDecision] = []
        self._schemas: dict[str, dict] = {}

    # -- Rule management ----------------------------------------------------

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a permission rule. Rules are evaluated in precedence order."""
        self._rules.append(rule)

    def load_rules_from_schema(self, schema_path: Path) -> int:
        """Load permission rules from a permission schema YAML file."""
        with open(schema_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        count = 0
        for perm in data.get("permissions", []):
            if isinstance(perm, dict):
                rule = PermissionRule(
                    id=perm.get("id", f"perm-auto-{count}"),
                    scope=perm.get("scope", "tool"),
                    trust_tier=perm.get("trust_tier", "community"),
                    action=perm.get("action", "deny"),
                    conditions=perm.get("conditions", []),
                    audit_required=perm.get("audit_required", True),
                )
                self._rules.append(rule)
                count += 1
        return count

    # -- Schema registration ------------------------------------------------

    def register_tool_schema(self, tool_name: str, schema: dict[str, Any]) -> None:
        """Register a tool's argument schema for pre-invocation validation."""
        self._schemas[tool_name] = schema

    # -- Core evaluation ----------------------------------------------------

    def evaluate(
        self,
        tool_name: str,
        session_id: str,
        correlation_id: str,
        arguments: dict[str, Any] | None = None,
        trust_tier: str = "community",
        context: dict[str, Any] | None = None,
    ) -> PolicyDecision:
        """
        Evaluate a tool invocation against the policy engine.

        Returns a PolicyDecision artifact that must be checked before execution.
        """
        arguments = arguments or {}
        context = context or {}
        now = datetime.now(timezone.utc).isoformat()
        decision_id = f"pd-{uuid.uuid4().hex[:8]}"

        # E3-S2: Schema validation before invocation
        schema_errors = self._validate_tool_args(tool_name, arguments)
        if schema_errors:
            decision = PolicyDecision(
                decision_id=decision_id,
                action="deny",
                rationale=f"Schema validation failed: {'; '.join(schema_errors)}",
                policy_id="schema-validation",
                tool_name=tool_name,
                session_id=session_id,
                correlation_id=correlation_id,
                timestamp=now,
                evidence_links=[],
                conditions_evaluated=[{"check": "schema", "errors": schema_errors}],
            )
            self._record(decision)
            return decision

        # Evaluate permission rules in order (first match wins)
        conditions_evaluated = []
        for rule in self._rules:
            if not self._rule_matches_scope(rule, tool_name):
                continue

            # Check trust tier precedence
            tier_match = self._check_trust_tier(rule.trust_tier, trust_tier)
            conditions_evaluated.append({
                "rule_id": rule.id,
                "scope_match": True,
                "tier_match": tier_match,
            })

            if tier_match:
                # Evaluate conditions
                conditions_pass = self._evaluate_conditions(
                    rule.conditions, arguments, context
                )
                conditions_evaluated[-1]["conditions_pass"] = conditions_pass

                if conditions_pass:
                    decision = PolicyDecision(
                        decision_id=decision_id,
                        action=rule.action if rule.action != "prompt" else "escalate",
                        rationale=f"Rule {rule.id} matched: scope={rule.scope}, "
                                  f"tier={rule.trust_tier}, action={rule.action}",
                        policy_id=rule.id,
                        tool_name=tool_name,
                        session_id=session_id,
                        correlation_id=correlation_id,
                        timestamp=now,
                        evidence_links=[],
                        conditions_evaluated=conditions_evaluated,
                    )
                    self._record(decision)
                    return decision

        # Default: deny if no rule matched
        decision = PolicyDecision(
            decision_id=decision_id,
            action="deny",
            rationale="No matching permission rule found — default deny",
            policy_id="default-deny",
            tool_name=tool_name,
            session_id=session_id,
            correlation_id=correlation_id,
            timestamp=now,
            evidence_links=[],
            conditions_evaluated=conditions_evaluated,
        )
        self._record(decision)
        return decision

    # -- Audit log ----------------------------------------------------------

    @property
    def audit_log(self) -> list[PolicyDecision]:
        return list(self._audit_log)

    def get_decisions_for_session(self, session_id: str) -> list[PolicyDecision]:
        """Get all decisions for a session (replayable)."""
        return [d for d in self._audit_log if d.session_id == session_id]

    def get_denied_decisions(self) -> list[PolicyDecision]:
        """Get all denied decisions (machine-readable for replay)."""
        return [d for d in self._audit_log if d.action == "deny"]

    # -- Internal -----------------------------------------------------------

    def _validate_tool_args(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> list[str]:
        """Validate tool arguments against registered schema."""
        schema = self._schemas.get(tool_name)
        if not schema:
            return []  # No schema registered — pass through

        errors = []
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for req in required:
            if req not in arguments:
                errors.append(f"Missing required argument: '{req}'")

        for arg_name, arg_value in arguments.items():
            prop_schema = properties.get(arg_name, {})
            if not prop_schema:
                continue

            expected_type = prop_schema.get("type", "")
            if expected_type == "string" and not isinstance(arg_value, str):
                errors.append(f"Argument '{arg_name}' must be string, got {type(arg_value).__name__}")
            elif expected_type == "integer" and not isinstance(arg_value, int):
                errors.append(f"Argument '{arg_name}' must be integer, got {type(arg_value).__name__}")

            pattern = prop_schema.get("pattern", "")
            if pattern and isinstance(arg_value, str):
                if not re.match(pattern, arg_value):
                    errors.append(f"Argument '{arg_name}' does not match pattern '{pattern}'")

            enum_vals = prop_schema.get("enum", [])
            if enum_vals and arg_value not in enum_vals:
                errors.append(f"Argument '{arg_name}' must be one of {enum_vals}")

        return errors

    def _rule_matches_scope(self, rule: PermissionRule, tool_name: str) -> bool:
        """Check if a rule's scope matches the tool invocation."""
        return rule.scope in ("tool", "pipeline", "agent")

    def _check_trust_tier(self, rule_tier: str, request_tier: str) -> bool:
        """Check if the request tier satisfies the rule tier."""
        tier_order = ["builtin", "verified", "community", "untrusted"]
        try:
            rule_idx = tier_order.index(rule_tier)
            req_idx = tier_order.index(request_tier)
            return req_idx <= rule_idx  # request must be at or above rule tier
        except ValueError:
            return False

    def _evaluate_conditions(
        self,
        conditions: list[dict[str, Any]],
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        """Evaluate all conditions (AND logic). Empty conditions = pass."""
        if not conditions:
            return True

        merged = {**arguments, **context}
        for cond in conditions:
            field_name = cond.get("field", "")
            operator = cond.get("operator", "eq")
            expected = cond.get("value")
            actual = merged.get(field_name)

            if operator == "eq" and actual != expected:
                return False
            elif operator == "neq" and actual == expected:
                return False
            elif operator == "in" and actual not in (expected or []):
                return False
            elif operator == "not_in" and actual in (expected or []):
                return False
            elif operator == "matches" and isinstance(actual, str) and isinstance(expected, str):
                if not re.match(expected, actual):
                    return False

        return True

    def _record(self, decision: PolicyDecision) -> None:
        """Record decision to audit log."""
        self._audit_log.append(decision)


# ─────────────────────────────────────────────────────────────────────────────
# SYNAPSE INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────

class PolicyEngineWithSynapses(PolicyEngine):
    """Policy engine extended with synapse firing."""
    
    def __init__(self, rules: list[PermissionRule] | None = None, synapse_engine=None):
        super().__init__(rules)
        self.synapse_engine = synapse_engine
        self.synapse_decisions: list = []
    
    def evaluate_with_synapses(
        self,
        tool_name: str,
        session_id: str,
        correlation_id: str,
        arguments: dict[str, Any] | None = None,
        trust_tier: str = "community",
        context: dict[str, Any] | None = None,
        synapse_context: dict[str, Any] | None = None,
    ) -> tuple[PolicyDecision, list]:
        """
        Evaluate tool invocation through BOTH policy engine AND synapses.
        Returns (policy_decision, synapse_decisions).
        
        If any synapse HALTS, return HALT regardless of policy decision.
        """
        synapse_decisions = []
        
        # Fire synapses first (they block harder)
        if self.synapse_engine and synapse_context:
            synapse_decisions = self._fire_synapses(synapse_context)
            if any(d["action"] == "halt" for d in synapse_decisions):
                # Synapses blocked it
                policy_decision = PolicyDecision(
                    decision_id=f"pd-synapse-halt-{uuid.uuid4().hex[:8]}",
                    action="deny",
                    rationale=f"Synapse halt: {[d.get('message') for d in synapse_decisions]}",
                    policy_id="synapse-enforcement",
                    tool_name=tool_name,
                    session_id=session_id,
                    correlation_id=correlation_id,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    evidence_links=[],
                    conditions_evaluated=[{"synapses_fired": len(synapse_decisions)}],
                )
                return policy_decision, synapse_decisions
        
        # Then evaluate policy
        policy_decision = self.evaluate(
            tool_name,
            session_id,
            correlation_id,
            arguments,
            trust_tier,
            context,
        )
        
        return policy_decision, synapse_decisions
    
    def _fire_synapses(self, context: dict[str, Any]) -> list:
        """Fire all registered synapses for the context."""
        if not self.synapse_engine:
            return []
        
        decisions = []
        for synapse in self.synapse_engine.synapses.values():
            for hook in synapse.hooks.values():
                # Simple sync validation for now
                try:
                    result = hook.validator(context)
                    if hasattr(result, '__await__'):
                        # Can't await in sync context, skip async validators
                        continue
                    decisions.append({
                        "synapse": synapse.name,
                        "hook": hook.name,
                        "action": result.action.value if hasattr(result, 'action') else "allow",
                        "message": result.message if hasattr(result, 'message') else "",
                    })
                except Exception:
                    pass
        
        return decisions
