"""
Archon v2.0 Test Suite — Guardrails Tests

Tests the anti-rationalization synapse loading, forbidden phrases detection,
iron laws enforcement, and guardrail schema validation.
"""

import sys
from pathlib import Path

import pytest
import yaml

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestAntiRationalizationSynapse:
    """Test anti-rationalization synapse structure and content."""

    @pytest.fixture
    def synapse_dir(self):
        return ARCHON_ROOT / "synapses" / "anti-rationalization"

    def test_synapse_directory_exists(self, synapse_dir):
        assert synapse_dir.exists(), "Anti-rationalization synapse directory missing"

    def test_synapse_md_exists(self, synapse_dir):
        assert (synapse_dir / "SYNAPSE.md").exists()

    def test_manifest_exists(self, synapse_dir):
        assert (synapse_dir / "manifest.yaml").exists()

    def test_manifest_is_core_type(self, synapse_dir):
        with open(synapse_dir / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)
        assert manifest["synapse-type"] == "core"
        assert manifest["name"] == "anti-rationalization"

    def test_manifest_has_firing_phases(self, synapse_dir):
        with open(synapse_dir / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)
        phases = [p["name"] for p in manifest["firing-phases"]]
        assert "DETECT" in phases
        assert "ENFORCE" in phases
        assert "AUDIT" in phases

    def test_iron_laws_resource_exists(self, synapse_dir):
        assert (synapse_dir / "resources" / "iron-laws.md").exists()

    def test_rationalization_tables_exist(self, synapse_dir):
        assert (synapse_dir / "resources" / "rationalization-tables.md").exists()

    def test_red_flags_exist(self, synapse_dir):
        assert (synapse_dir / "resources" / "red-flags.md").exists()

    def test_forbidden_phrases_exist(self, synapse_dir):
        assert (synapse_dir / "resources" / "forbidden-phrases.md").exists()

    def test_iron_laws_has_10_laws(self, synapse_dir):
        content = (synapse_dir / "resources" / "iron-laws.md").read_text(encoding="utf-8")
        law_count = content.count("## Law ")
        assert law_count == 10, f"Expected 10 Iron Laws, found {law_count}"

    def test_synapse_md_has_iron_laws_table(self, synapse_dir):
        content = (synapse_dir / "SYNAPSE.md").read_text(encoding="utf-8")
        assert "Iron Law" in content
        assert "Iron Law #" in content or "| 1 |" in content

    def test_forbidden_phrases_has_alternatives(self, synapse_dir):
        content = (synapse_dir / "resources" / "forbidden-phrases.md").read_text(encoding="utf-8")
        assert "Say Instead" in content or "✅" in content

    def test_red_flags_has_checklists(self, synapse_dir):
        content = (synapse_dir / "resources" / "red-flags.md").read_text(encoding="utf-8")
        assert "- [ ]" in content


class TestForbiddenPhrasesDetection:
    """Test that forbidden phrases can be programmatically detected."""

    FORBIDDEN_PHRASES = [
        "This should work",
        "I believe this is correct",
        "This is probably fine",
        "I'll handle that later",
        "The user won't notice",
        "It's just a small change",
        "Close enough",
    ]

    def test_forbidden_phrases_detected(self):
        for phrase in self.FORBIDDEN_PHRASES:
            assert _contains_forbidden_phrase(phrase), f"Should detect: '{phrase}'"

    def test_clean_text_not_flagged(self):
        clean_texts = [
            "I verified this works by running the test suite",
            "I confirmed this is correct because the tests pass",
            "The change affects 3 components and I've verified all tests",
        ]
        for text in clean_texts:
            assert not _contains_forbidden_phrase(text), f"False positive: '{text}'"


def _contains_forbidden_phrase(text: str) -> bool:
    """Simple forbidden phrase detector."""
    forbidden = [
        "should work",
        "believe this is correct",
        "probably fine",
        "handle that later",
        "won't notice",
        "just a small",
        "close enough",
        "basically done",
        "think i fixed",
        "seems to work",
        "fairly confident",
        "looks right",
        "should be compatible",
        "no issues expected",
    ]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in forbidden)


class TestGuardrailsSchema:
    """Test the guardrails schema file."""

    def test_schema_exists(self):
        schema_path = ARCHON_ROOT / "schemas" / "guardrails.schema.yaml"
        assert schema_path.exists()

    def test_schema_parses(self):
        schema_path = ARCHON_ROOT / "schemas" / "guardrails.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        assert "properties" in schema
        assert "guardrails" in schema["properties"]

    def test_schema_defines_types(self):
        schema_path = ARCHON_ROOT / "schemas" / "guardrails.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        guardrail_props = schema["properties"]["guardrails"]["items"]["properties"]
        type_enum = guardrail_props["type"]["enum"]
        assert "must-always" in type_enum
        assert "must-never" in type_enum

    def test_schema_defines_severity(self):
        schema_path = ARCHON_ROOT / "schemas" / "guardrails.schema.yaml"
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        guardrail_props = schema["properties"]["guardrails"]["items"]["properties"]
        severity_enum = guardrail_props["severity"]["enum"]
        assert "critical" in severity_enum
        assert "major" in severity_enum
        assert "minor" in severity_enum


class TestDeviationLogSchema:
    """Test the deviation log schema."""

    def test_schema_exists(self):
        assert (ARCHON_ROOT / "schemas" / "deviation-log.schema.yaml").exists()

    def test_schema_parses(self):
        with open(ARCHON_ROOT / "schemas" / "deviation-log.schema.yaml") as f:
            schema = yaml.safe_load(f)
        assert schema["title"] == "Archon Deviation Log Schema"


class TestThinkingTraceSchema:
    """Test the thinking trace schema."""

    def test_schema_exists(self):
        assert (ARCHON_ROOT / "schemas" / "thinking-trace.schema.yaml").exists()

    def test_schema_parses(self):
        with open(ARCHON_ROOT / "schemas" / "thinking-trace.schema.yaml") as f:
            schema = yaml.safe_load(f)
        assert schema["title"] == "Archon Thinking Trace Schema"
        assert "phases" in schema["properties"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
