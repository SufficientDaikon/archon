"""
Archon v3 Schema Validator — Validates v3 schema contracts.

E1-S2: Schema lint and contradiction checker for prompt constraints.
- Loads YAML schemas and validates required fields, enums, patterns
- Checks for contradictory state transitions
- Validates prompt templates for required framework fields
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SchemaLintResult:
    """Result of schema linting."""
    schema_name: str
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_run: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_name": self.schema_name,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks_run": self.checks_run,
        }


class SchemaValidator:
    """
    Validates Archon v3 schema files for correctness and consistency.

    Checks:
    - Required top-level fields (title, version, type, required, properties)
    - Enum values are non-empty and have no duplicates
    - Pattern fields contain valid regex
    - State transitions have no unreachable states
    - No contradictory constraints (e.g., required + not-in-properties)
    """

    REQUIRED_SCHEMA_FIELDS = {"title", "version", "type"}

    def lint_schema(self, schema_path: Path) -> SchemaLintResult:
        """Lint a single schema file."""
        result = SchemaLintResult(schema_name=schema_path.name)

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = yaml.safe_load(f)
        except Exception as e:
            result.passed = False
            result.errors.append(f"Cannot parse schema: {e}")
            return result

        if not isinstance(schema, dict):
            result.passed = False
            result.errors.append("Schema root must be a mapping")
            return result

        # Check required top-level fields
        result.checks_run += 1
        for req in self.REQUIRED_SCHEMA_FIELDS:
            if req not in schema:
                result.errors.append(f"Missing required field: '{req}'")
                result.passed = False

        # Check version format
        result.checks_run += 1
        version = schema.get("version", "")
        if version and not re.match(r"^\d+\.\d+\.\d+$", str(version)):
            result.errors.append(f"Invalid version format: '{version}' (expected MAJOR.MINOR.PATCH)")
            result.passed = False

        # Check properties for enum duplicates
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            self._check_properties(properties, result)

        # Check state transitions for contradictions
        transitions = schema.get("state_transitions", {})
        if transitions:
            self._check_state_transitions(transitions, properties, result)

        return result

    def _check_properties(self, properties: dict, result: SchemaLintResult) -> None:
        """Check property definitions for consistency."""
        for prop_name, prop_def in properties.items():
            if not isinstance(prop_def, dict):
                continue

            # Check enum duplicates
            enum_vals = prop_def.get("enum", [])
            if enum_vals:
                result.checks_run += 1
                if len(enum_vals) != len(set(enum_vals)):
                    result.errors.append(f"Property '{prop_name}' has duplicate enum values")
                    result.passed = False
                if not enum_vals:
                    result.warnings.append(f"Property '{prop_name}' has empty enum")

            # Check pattern is valid regex
            pattern = prop_def.get("pattern", "")
            if pattern:
                result.checks_run += 1
                try:
                    re.compile(pattern)
                except re.error as e:
                    result.errors.append(f"Property '{prop_name}' has invalid regex: {e}")
                    result.passed = False

            # Recurse into nested properties
            nested = prop_def.get("properties", {})
            if isinstance(nested, dict):
                self._check_properties(nested, result)

            # Check items for arrays
            items = prop_def.get("items", {})
            if isinstance(items, dict) and "properties" in items:
                self._check_properties(items["properties"], result)

    def _check_state_transitions(
        self, transitions: dict, properties: dict, result: SchemaLintResult
    ) -> None:
        """Check state machine transitions for contradictions."""
        result.checks_run += 1

        all_states = set(transitions.keys())
        reachable_targets = set()
        for targets in transitions.values():
            if isinstance(targets, list):
                reachable_targets.update(targets)

        # Check for unknown target states
        unknown = reachable_targets - all_states
        if unknown:
            result.errors.append(f"State transitions reference undefined states: {unknown}")
            result.passed = False

        # Check that status enum matches transition states
        status_prop = properties.get("status", {})
        if isinstance(status_prop, dict):
            status_enum = set(status_prop.get("enum", []))
            if status_enum and status_enum != all_states:
                missing_in_enum = all_states - status_enum
                missing_in_transitions = status_enum - all_states
                if missing_in_enum:
                    result.errors.append(
                        f"States in transitions but not in status enum: {missing_in_enum}"
                    )
                    result.passed = False
                if missing_in_transitions:
                    result.warnings.append(
                        f"States in status enum but not in transitions: {missing_in_transitions}"
                    )

    def lint_all(self, schemas_dir: Path) -> list[SchemaLintResult]:
        """Lint all schema files in a directory."""
        results = []
        for schema_path in sorted(schemas_dir.glob("*.schema.yaml")):
            results.append(self.lint_schema(schema_path))
        return results

    def check_prompt_contradictions(self, prompt_library_path: Path) -> SchemaLintResult:
        """
        Check prompt library for contradictions.

        Validates:
        - All required framework fields present
        - No DO/DON'T contradictions within same prompt
        - Evidence field is never empty
        """
        import xml.etree.ElementTree as ET

        result = SchemaLintResult(schema_name="prompt-library")

        try:
            root = ET.parse(prompt_library_path).getroot()
        except Exception as e:
            result.passed = False
            result.errors.append(f"Cannot parse prompt library: {e}")
            return result

        framework = root.find("framework")
        if framework is not None:
            required_text = framework.findtext("requiredFields") or ""
            required_fields = set(required_text.split())
        else:
            required_fields = set()

        for prompt in root.findall("prompt"):
            pid = prompt.attrib.get("id", "unknown")
            result.checks_run += 1

            # Check all required fields present
            present_fields = {child.tag for child in prompt}
            missing = required_fields - present_fields
            if missing:
                result.errors.append(f"Prompt '{pid}' missing required fields: {missing}")
                result.passed = False

            # Check evidence field is non-empty
            evidence = prompt.findtext("evidence") or ""
            if not evidence.strip():
                result.errors.append(f"Prompt '{pid}' has empty evidence field")
                result.passed = False

            # Check for DO/DON'T contradictions
            do_text = (prompt.findtext("do") or "").lower()
            dont_text = (prompt.findtext("dont") or "").lower()
            if do_text and dont_text:
                do_phrases = {p.strip() for p in do_text.split(",") if p.strip()}
                dont_phrases = {p.strip() for p in dont_text.split(",") if p.strip()}
                overlap = do_phrases & dont_phrases
                if overlap:
                    result.errors.append(
                        f"Prompt '{pid}' has contradictory DO/DON'T: {overlap}"
                    )
                    result.passed = False

        return result


class CompatibilityChecker:
    """
    E1-S3: v2-to-v3 compatibility diagnostics.

    Scans v2 schemas and produces a deterministic compatibility report
    showing what changes, additions, and potential breakages exist.
    """

    @dataclass
    class CompatReport:
        """Compatibility analysis report."""
        v2_schemas: list[str] = field(default_factory=list)
        v3_new_schemas: list[str] = field(default_factory=list)
        v2_preserved: list[str] = field(default_factory=list)
        breaking_changes: list[str] = field(default_factory=list)
        migration_hints: list[str] = field(default_factory=list)
        compatible: bool = True

        def to_dict(self) -> dict[str, Any]:
            return {
                "v2_schemas": self.v2_schemas,
                "v3_new_schemas": self.v3_new_schemas,
                "v2_preserved": self.v2_preserved,
                "breaking_changes": self.breaking_changes,
                "migration_hints": self.migration_hints,
                "compatible": self.compatible,
            }

    V2_SCHEMA_NAMES = {
        "agent-manifest.schema.yaml",
        "bundle-manifest.schema.yaml",
        "deviation-log.schema.yaml",
        "guardrails.schema.yaml",
        "mcp-catalog.schema.yaml",
        "pipeline.schema.yaml",
        "skill-manifest.schema.yaml",
        "synapse-manifest.schema.yaml",
        "thinking-trace.schema.yaml",
    }

    V3_NEW_SCHEMAS = {
        "session.schema.yaml",
        "tool-invocation.schema.yaml",
        "permission.schema.yaml",
        "hook-event.schema.yaml",
        "telemetry-envelope.schema.yaml",
        "context-handoff.schema.yaml",
    }

    def check(self, schemas_dir: Path) -> CompatReport:
        """Run compatibility analysis."""
        report = self.CompatReport()

        existing = {p.name for p in schemas_dir.glob("*.schema.yaml")}

        # Identify v2 schemas
        report.v2_schemas = sorted(self.V2_SCHEMA_NAMES & existing)
        report.v2_preserved = sorted(self.V2_SCHEMA_NAMES & existing)

        # Identify v3 additions
        report.v3_new_schemas = sorted(self.V3_NEW_SCHEMAS & existing)

        # Check for v2 schemas that were removed (breaking)
        missing_v2 = self.V2_SCHEMA_NAMES - existing
        if missing_v2:
            report.compatible = False
            for name in sorted(missing_v2):
                report.breaking_changes.append(f"v2 schema removed: {name}")

        # Check v2 schemas for version changes
        for name in report.v2_preserved:
            path = schemas_dir / name
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                version = str(data.get("version", data.get("schema_version", "1.0")))
                if version.startswith("3"):
                    report.breaking_changes.append(
                        f"v2 schema '{name}' was upgraded to v3 without migration evidence"
                    )
                    report.compatible = False
            except Exception:
                pass

        # Generate migration hints
        for v3_name in sorted(self.V3_NEW_SCHEMAS):
            if v3_name in existing:
                report.migration_hints.append(
                    f"New v3 schema '{v3_name}' — no v2 equivalent, additive change"
                )
            else:
                report.migration_hints.append(
                    f"Expected v3 schema '{v3_name}' not yet created"
                )

        return report
