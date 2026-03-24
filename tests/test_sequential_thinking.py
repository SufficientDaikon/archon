"""
Archon v2.0 Test Suite — Sequential Thinking Tests

Tests the sequential thinking synapse structure and reasoning patterns.
"""

import sys
from pathlib import Path

import pytest
import yaml

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestSequentialThinkingSynapse:
    """Test sequential thinking synapse structure."""

    @pytest.fixture
    def synapse_dir(self):
        return ARCHON_ROOT / "synapses" / "sequential-thinking"

    def test_synapse_directory_exists(self, synapse_dir):
        assert synapse_dir.exists()

    def test_synapse_md_exists(self, synapse_dir):
        assert (synapse_dir / "SYNAPSE.md").exists()

    def test_manifest_exists(self, synapse_dir):
        assert (synapse_dir / "manifest.yaml").exists()

    def test_manifest_is_core_type(self, synapse_dir):
        with open(synapse_dir / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)
        assert manifest["synapse-type"] == "core"
        assert manifest["name"] == "sequential-thinking"

    def test_four_firing_phases(self, synapse_dir):
        with open(synapse_dir / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)
        phases = [p["name"] for p in manifest["firing-phases"]]
        assert phases == ["DECOMPOSE", "REASON", "VALIDATE", "SYNTHESIZE"]

    def test_decomposition_patterns_resource(self, synapse_dir):
        assert (synapse_dir / "resources" / "decomposition-patterns.md").exists()

    def test_reasoning_templates_resource(self, synapse_dir):
        assert (synapse_dir / "resources" / "reasoning-templates.md").exists()

    def test_validation_checklist_resource(self, synapse_dir):
        assert (synapse_dir / "resources" / "validation-checklist.md").exists()


class TestSynapseContent:
    """Test synapse content quality."""

    def test_synapse_md_has_firing_phases(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "SYNAPSE.md").read_text(encoding="utf-8")
        assert "DECOMPOSE" in content
        assert "REASON" in content
        assert "VALIDATE" in content
        assert "SYNTHESIZE" in content

    def test_synapse_md_has_thinking_trace_format(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "SYNAPSE.md").read_text(encoding="utf-8")
        assert "[THINKING]" in content
        assert "[/THINKING]" in content

    def test_synapse_md_has_stuck_loop_detection(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "SYNAPSE.md").read_text(encoding="utf-8")
        assert "Stuck-Loop" in content or "STUCK LOOP" in content

    def test_synapse_md_has_complexity_scaling(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "SYNAPSE.md").read_text(encoding="utf-8")
        assert "Complexity" in content
        assert "trivial" in content.lower()
        assert "expert" in content.lower()

    def test_synapse_md_has_browsecomp_pattern(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "SYNAPSE.md").read_text(encoding="utf-8")
        assert "BrowseComp" in content
        assert "DETECT" in content
        assert "HYPOTHESIZE" in content

    def test_decomposition_has_patterns(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "resources" / "decomposition-patterns.md").read_text(encoding="utf-8")
        assert "Feature Implementation" in content
        assert "Bug Investigation" in content
        assert "Code Review" in content

    def test_reasoning_has_templates(self):
        content = (ARCHON_ROOT / "synapses" / "sequential-thinking" / "resources" / "reasoning-templates.md").read_text(encoding="utf-8")
        assert "Decision Template" in content
        assert "Investigation Template" in content
        assert "Error Analysis Template" in content


class TestThinkingTraceSchema:
    """Test thinking trace schema validation."""

    def test_schema_defines_complexity_levels(self):
        with open(ARCHON_ROOT / "schemas" / "thinking-trace.schema.yaml") as f:
            schema = yaml.safe_load(f)
        complexity_enum = schema["properties"]["complexity"]["enum"]
        assert complexity_enum == ["trivial", "simple", "moderate", "complex", "expert"]

    def test_schema_defines_phases(self):
        with open(ARCHON_ROOT / "schemas" / "thinking-trace.schema.yaml") as f:
            schema = yaml.safe_load(f)
        phases = schema["properties"]["phases"]["properties"]
        assert "decompose" in phases
        assert "reason" in phases
        assert "validate" in phases
        assert "synthesize" in phases

    def test_schema_has_metadata(self):
        with open(ARCHON_ROOT / "schemas" / "thinking-trace.schema.yaml") as f:
            schema = yaml.safe_load(f)
        metadata = schema["properties"]["metadata"]["properties"]
        assert "agent" in metadata
        assert "pipeline" in metadata
        assert "duration-ms" in metadata


class TestMetacognitionSynapse:
    """Test the existing metacognition synapse still works."""

    def test_synapse_dir_exists(self):
        assert (ARCHON_ROOT / "synapses" / "metacognition").exists()

    def test_synapse_md_exists(self):
        assert (ARCHON_ROOT / "synapses" / "metacognition" / "SYNAPSE.md").exists()

    def test_manifest_exists(self):
        assert (ARCHON_ROOT / "synapses" / "metacognition" / "manifest.yaml").exists()

    def test_manifest_is_core(self):
        with open(ARCHON_ROOT / "synapses" / "metacognition" / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)
        assert manifest.get("synapse-type") == "core"


class TestAllCoreSynapses:
    """Test that all 3 core synapses are registered and valid."""

    def test_three_core_synapses(self):
        with open(ARCHON_ROOT / "archon.yaml") as f:
            manifest = yaml.safe_load(f)
        synapses = manifest.get("synapses", [])
        core_synapses = [s for s in synapses if s.get("type") == "core"]
        assert len(core_synapses) == 3

    def test_all_synapse_dirs_exist(self):
        with open(ARCHON_ROOT / "archon.yaml") as f:
            manifest = yaml.safe_load(f)
        for synapse in manifest.get("synapses", []):
            synapse_path = ARCHON_ROOT / synapse["path"]
            assert synapse_path.exists(), f"Synapse dir missing: {synapse_path}"

    def test_all_synapses_have_manifest(self):
        with open(ARCHON_ROOT / "archon.yaml") as f:
            manifest = yaml.safe_load(f)
        for synapse in manifest.get("synapses", []):
            manifest_path = ARCHON_ROOT / synapse["path"] / "manifest.yaml"
            assert manifest_path.exists(), f"Synapse manifest missing: {manifest_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
