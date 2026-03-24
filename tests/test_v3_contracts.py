"""
Archon v3 E1 Tests — Contract and Schema Foundation.

Tests:
- E1-S1: v3 schema structure, required fields, state transitions
- E1-S2: Schema lint catches missing fields and contradictory constraints
- E1-S3: v2-to-v3 compatibility diagnostics produce deterministic report
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ARCHON_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = ARCHON_ROOT / "schemas"


# ---------------------------------------------------------------------------
# E1-S1: v3 schema positive and negative fixture tests
# ---------------------------------------------------------------------------

V3_SCHEMAS = [
    "session.schema.yaml",
    "tool-invocation.schema.yaml",
    "permission.schema.yaml",
    "hook-event.schema.yaml",
    "telemetry-envelope.schema.yaml",
    "context-handoff.schema.yaml",
]

V2_SCHEMAS = [
    "agent-manifest.schema.yaml",
    "bundle-manifest.schema.yaml",
    "deviation-log.schema.yaml",
    "guardrails.schema.yaml",
    "mcp-catalog.schema.yaml",
    "pipeline.schema.yaml",
    "skill-manifest.schema.yaml",
    "synapse-manifest.schema.yaml",
    "thinking-trace.schema.yaml",
]


class TestV3SchemasExist:
    """All v3 schemas must exist alongside v2 schemas."""

    @pytest.mark.parametrize("schema_name", V3_SCHEMAS)
    def test_v3_schema_exists(self, schema_name: str):
        path = SCHEMAS_DIR / schema_name
        assert path.exists(), f"v3 schema missing: {schema_name}"

    @pytest.mark.parametrize("schema_name", V2_SCHEMAS)
    def test_v2_schema_preserved(self, schema_name: str):
        path = SCHEMAS_DIR / schema_name
        assert path.exists(), f"v2 schema removed (breaking): {schema_name}"


class TestV3SchemaStructure:
    """All v3 schemas must have required top-level fields and valid structure."""

    @pytest.mark.parametrize("schema_name", V3_SCHEMAS)
    def test_has_title(self, schema_name: str):
        data = _load_schema(schema_name)
        assert "title" in data, f"{schema_name} missing 'title'"

    @pytest.mark.parametrize("schema_name", V3_SCHEMAS)
    def test_has_version_3(self, schema_name: str):
        data = _load_schema(schema_name)
        assert data.get("version", "").startswith("3"), f"{schema_name} version not 3.x"

    @pytest.mark.parametrize("schema_name", V3_SCHEMAS)
    def test_has_type(self, schema_name: str):
        data = _load_schema(schema_name)
        assert "type" in data, f"{schema_name} missing 'type'"

    @pytest.mark.parametrize("schema_name", V3_SCHEMAS)
    def test_has_required_fields(self, schema_name: str):
        data = _load_schema(schema_name)
        assert "required" in data or (
            "properties" in data and isinstance(data["properties"], dict)
        ), f"{schema_name} has neither 'required' nor 'properties'"

    @pytest.mark.parametrize("schema_name", V3_SCHEMAS)
    def test_properties_are_typed(self, schema_name: str):
        data = _load_schema(schema_name)
        properties = data.get("properties", {})
        for prop_name, prop_def in properties.items():
            if isinstance(prop_def, dict):
                assert "type" in prop_def or "enum" in prop_def or "$ref" in prop_def, (
                    f"{schema_name}.{prop_name} has no type, enum, or $ref"
                )


class TestSessionSchemaTransitions:
    """Session schema must define a valid state machine."""

    def test_transitions_exist(self):
        data = _load_schema("session.schema.yaml")
        assert "state_transitions" in data, "Session schema missing state_transitions"

    def test_all_status_enum_states_have_transitions(self):
        data = _load_schema("session.schema.yaml")
        statuses = set(data["properties"]["status"]["enum"])
        transitions = set(data["state_transitions"].keys())
        assert statuses == transitions, (
            f"Mismatch: enum={statuses - transitions}, transitions={transitions - statuses}"
        )

    def test_no_unknown_target_states(self):
        data = _load_schema("session.schema.yaml")
        all_states = set(data["state_transitions"].keys())
        for source, targets in data["state_transitions"].items():
            for target in targets:
                assert target in all_states, (
                    f"Transition {source}->{target}: target not in state set"
                )

    def test_archived_is_terminal(self):
        data = _load_schema("session.schema.yaml")
        archived_targets = data["state_transitions"].get("archived", [])
        assert archived_targets == [], "archived must be terminal (no outgoing transitions)"


class TestToolInvocationSchema:
    """Tool invocation must enforce policy decision."""

    def test_policy_decision_required(self):
        data = _load_schema("tool-invocation.schema.yaml")
        assert "policy_decision" in data.get("required", [])

    def test_policy_action_enum(self):
        data = _load_schema("tool-invocation.schema.yaml")
        policy = data["properties"]["policy_decision"]["properties"]["action"]
        assert set(policy["enum"]) == {"allow", "deny", "escalate"}


class TestPermissionSchema:
    """Permission schema trust tier ordering."""

    def test_trust_tiers_defined(self):
        data = _load_schema("permission.schema.yaml")
        items = data["properties"]["permissions"]["items"]["properties"]
        tiers = items["trust_tier"]["enum"]
        assert tiers == ["builtin", "verified", "community", "untrusted"]


class TestContextHandoffSchema:
    """Context handoff must enforce evidence links and pinned constraints."""

    def test_evidence_links_required(self):
        data = _load_schema("context-handoff.schema.yaml")
        assert "evidence_links" in data.get("required", [])

    def test_pinned_constraints_required(self):
        data = _load_schema("context-handoff.schema.yaml")
        assert "pinned_constraints" in data.get("required", [])

    def test_evidence_types_enum(self):
        data = _load_schema("context-handoff.schema.yaml")
        items = data["properties"]["evidence_links"]["items"]["properties"]
        types = set(items["type"]["enum"])
        assert "test_output" in types
        assert "artifact" in types


# ---------------------------------------------------------------------------
# E1-S1 Negative fixtures — schemas must reject bad data shapes
# ---------------------------------------------------------------------------

class TestNegativeFixtures:
    """Schema patterns must reject invalid ID formats."""

    @pytest.mark.parametrize("bad_id", ["", "abc", "sess-ZZZ", "123"])
    def test_session_id_rejects_bad_format(self, bad_id: str):
        data = _load_schema("session.schema.yaml")
        pattern = data["properties"]["session_id"]["pattern"]
        assert not re.match(pattern, bad_id), f"Pattern should reject '{bad_id}'"

    @pytest.mark.parametrize("good_id", ["sess-abcdef01", "sess-0123456789abcdef"])
    def test_session_id_accepts_good_format(self, good_id: str):
        data = _load_schema("session.schema.yaml")
        pattern = data["properties"]["session_id"]["pattern"]
        assert re.match(pattern, good_id), f"Pattern should accept '{good_id}'"

    @pytest.mark.parametrize("bad_id", ["", "inv-ZZZ", "tool-call-1"])
    def test_invocation_id_rejects_bad_format(self, bad_id: str):
        data = _load_schema("tool-invocation.schema.yaml")
        pattern = data["properties"]["invocation_id"]["pattern"]
        assert not re.match(pattern, bad_id), f"Pattern should reject '{bad_id}'"

    @pytest.mark.parametrize("bad_id", ["", "evt-ZZZ", "event-1"])
    def test_event_id_rejects_bad_format(self, bad_id: str):
        data = _load_schema("hook-event.schema.yaml")
        pattern = data["properties"]["event_id"]["pattern"]
        assert not re.match(pattern, bad_id), f"Pattern should reject '{bad_id}'"


# ---------------------------------------------------------------------------
# E1-S2: Schema lint and contradiction checker
# ---------------------------------------------------------------------------

class TestSchemaLint:
    """SchemaValidator must catch errors and pass clean schemas."""

    def test_lint_all_v3_schemas_pass(self):
        from src.archon.core.schema_validator import SchemaValidator
        validator = SchemaValidator()
        results = validator.lint_all(SCHEMAS_DIR)
        v3_results = [r for r in results if r.schema_name in V3_SCHEMAS]
        assert len(v3_results) == len(V3_SCHEMAS), "Not all v3 schemas were linted"
        for r in v3_results:
            assert r.passed, f"{r.schema_name} lint failed: {r.errors}"

    def test_lint_catches_missing_title(self, tmp_path: Path):
        from src.archon.core.schema_validator import SchemaValidator
        bad_schema = tmp_path / "bad.schema.yaml"
        bad_schema.write_text("type: object\nversion: '1.0.0'\n", encoding="utf-8")
        validator = SchemaValidator()
        result = validator.lint_schema(bad_schema)
        assert not result.passed
        assert any("title" in e for e in result.errors)

    def test_lint_catches_invalid_version(self, tmp_path: Path):
        from src.archon.core.schema_validator import SchemaValidator
        bad_schema = tmp_path / "bad.schema.yaml"
        bad_schema.write_text(
            "title: test\ntype: object\nversion: 'abc'\n", encoding="utf-8"
        )
        validator = SchemaValidator()
        result = validator.lint_schema(bad_schema)
        assert not result.passed
        assert any("version" in e.lower() for e in result.errors)

    def test_lint_catches_duplicate_enum(self, tmp_path: Path):
        from src.archon.core.schema_validator import SchemaValidator
        bad_schema = tmp_path / "dup.schema.yaml"
        bad_schema.write_text(
            "title: test\ntype: object\nversion: '1.0.0'\n"
            "properties:\n  status:\n    type: string\n    enum: [a, b, a]\n",
            encoding="utf-8",
        )
        validator = SchemaValidator()
        result = validator.lint_schema(bad_schema)
        assert not result.passed
        assert any("duplicate" in e.lower() for e in result.errors)

    def test_lint_catches_invalid_regex(self, tmp_path: Path):
        from src.archon.core.schema_validator import SchemaValidator
        bad_schema = tmp_path / "regex.schema.yaml"
        bad_schema.write_text(
            "title: test\ntype: object\nversion: '1.0.0'\n"
            "properties:\n  id:\n    type: string\n    pattern: '[invalid'\n",
            encoding="utf-8",
        )
        validator = SchemaValidator()
        result = validator.lint_schema(bad_schema)
        assert not result.passed
        assert any("regex" in e.lower() or "invalid" in e.lower() for e in result.errors)

    def test_lint_catches_unreachable_state(self, tmp_path: Path):
        from src.archon.core.schema_validator import SchemaValidator
        bad_schema = tmp_path / "state.schema.yaml"
        bad_schema.write_text(
            "title: test\ntype: object\nversion: '1.0.0'\n"
            "properties:\n  status:\n    type: string\n    enum: [a, b]\n"
            "state_transitions:\n  a: [b, c]\n  b: []\n",
            encoding="utf-8",
        )
        validator = SchemaValidator()
        result = validator.lint_schema(bad_schema)
        assert not result.passed
        assert any("undefined" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# E1-S3: v2-to-v3 compatibility diagnostics
# ---------------------------------------------------------------------------

class TestCompatibilityChecker:
    """CompatibilityChecker must produce deterministic report."""

    def test_no_v2_schemas_removed(self):
        from src.archon.core.schema_validator import CompatibilityChecker
        checker = CompatibilityChecker()
        report = checker.check(SCHEMAS_DIR)
        assert report.compatible, f"Breaking changes: {report.breaking_changes}"

    def test_all_v2_schemas_preserved(self):
        from src.archon.core.schema_validator import CompatibilityChecker
        checker = CompatibilityChecker()
        report = checker.check(SCHEMAS_DIR)
        assert len(report.v2_preserved) == len(V2_SCHEMAS)

    def test_v3_schemas_detected(self):
        from src.archon.core.schema_validator import CompatibilityChecker
        checker = CompatibilityChecker()
        report = checker.check(SCHEMAS_DIR)
        assert len(report.v3_new_schemas) == len(V3_SCHEMAS)

    def test_report_is_deterministic(self):
        from src.archon.core.schema_validator import CompatibilityChecker
        checker = CompatibilityChecker()
        r1 = checker.check(SCHEMAS_DIR)
        r2 = checker.check(SCHEMAS_DIR)
        assert r1.to_dict() == r2.to_dict(), "Report is non-deterministic"

    def test_migration_hints_present(self):
        from src.archon.core.schema_validator import CompatibilityChecker
        checker = CompatibilityChecker()
        report = checker.check(SCHEMAS_DIR)
        assert len(report.migration_hints) > 0

    def test_detects_missing_v2_schema(self, tmp_path: Path):
        """If a v2 schema is removed, compatibility must report breaking."""
        from src.archon.core.schema_validator import CompatibilityChecker
        # Create dir with only some v2 schemas
        for name in ["agent-manifest.schema.yaml"]:
            (tmp_path / name).write_text("title: test\nversion: '1.0'\ntype: object\n")
        checker = CompatibilityChecker()
        report = checker.check(tmp_path)
        assert not report.compatible
        assert len(report.breaking_changes) > 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_schema(name: str) -> dict:
    path = SCHEMAS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
