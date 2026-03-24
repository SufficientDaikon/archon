"""
Archon v3 E6 Tests — Migration and Release.

Tests:
- E6-S1: Migration dry-run with diff and remediation
- E6-S2: Release gates pass for all 6 hard gates
- E6-S3: Docs readiness (prompts, schemas, test coverage)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.archon.core.migration import (
    MigrationRunner,
    ReleaseGateValidator,
    ReleaseScorecard,
)

ARCHON_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# E6-S1: Migration dry-run
# ---------------------------------------------------------------------------

class TestMigrationDryRun:
    """Migration runner must produce complete, deterministic report."""

    def test_dry_run_succeeds(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        assert report.ready, f"Migration not ready: {report.blockers}"

    def test_zero_blockers(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        assert len(report.blockers) == 0

    def test_all_v2_schemas_preserved(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        v2_diffs = [d for d in report.diffs if d.category == "schema" and "v2" in d.description]
        for d in v2_diffs:
            assert d.change_type == "unchanged", f"v2 schema not preserved: {d.path}"

    def test_all_v3_schemas_present(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        v3_schema_diffs = [
            d for d in report.diffs
            if d.category == "schema" and "v3" in d.description and "added" in d.change_type
        ]
        assert len(v3_schema_diffs) == 6

    def test_all_v3_modules_present(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        module_diffs = [
            d for d in report.diffs
            if d.category == "module" and d.change_type == "added"
        ]
        assert len(module_diffs) == 4

    def test_all_v3_tests_present(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        test_diffs = [d for d in report.diffs if d.category == "test" and d.change_type == "added"]
        assert len(test_diffs) == 4

    def test_all_v2_modules_intact(self):
        runner = MigrationRunner()
        report = runner.dry_run(ARCHON_ROOT)
        v2_module_diffs = [
            d for d in report.diffs
            if d.category == "module" and "v2" in d.description
        ]
        for d in v2_module_diffs:
            assert d.change_type == "unchanged", f"v2 module modified: {d.path}"

    def test_report_is_deterministic(self):
        runner = MigrationRunner()
        r1 = runner.dry_run(ARCHON_ROOT)
        r2 = runner.dry_run(ARCHON_ROOT)
        assert r1.to_dict()["total_changes"] == r2.to_dict()["total_changes"]
        assert r1.to_dict()["blockers"] == r2.to_dict()["blockers"]
        assert r1.to_dict()["ready"] == r2.to_dict()["ready"]

    def test_detects_missing_schema(self, tmp_path: Path):
        """If a v3 schema is missing, report must flag it as a blocker."""
        # Create minimal structure without v3 schemas
        (tmp_path / "schemas").mkdir()
        for name in MigrationRunner.V2_SCHEMAS:
            (tmp_path / "schemas" / name).write_text("title: test\nversion: '1.0'\ntype: object\n")
        (tmp_path / "src" / "archon" / "core").mkdir(parents=True)
        (tmp_path / "tests").mkdir()

        runner = MigrationRunner()
        report = runner.dry_run(tmp_path)
        assert not report.ready
        assert any("v3 schema" in b for b in report.blockers)


# ---------------------------------------------------------------------------
# E6-S2: Release gates
# ---------------------------------------------------------------------------

class TestReleaseGates:
    """All 6 hard gates must pass against the current codebase."""

    def test_all_gates_pass(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        for gate in scorecard.gates:
            assert gate.passed, (
                f"Gate '{gate.gate_name}' FAILED: {gate.errors}"
            )

    def test_schema_and_contracts_gate(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        gate = _find_gate(scorecard, "SchemaAndContracts")
        assert gate.passed
        assert len(gate.evidence) > 0

    def test_policy_and_security_gate(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        gate = _find_gate(scorecard, "PolicyAndSecurity")
        assert gate.passed

    def test_replay_determinism_gate(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        gate = _find_gate(scorecard, "ReplayDeterminism")
        assert gate.passed

    def test_context_integrity_gate(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        gate = _find_gate(scorecard, "ContextIntegrity")
        assert gate.passed

    def test_prompt_quality_gate(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        gate = _find_gate(scorecard, "PromptQuality")
        assert gate.passed

    def test_migration_readiness_gate(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        gate = _find_gate(scorecard, "MigrationReadiness")
        assert gate.passed


class TestReleaseScorecard:
    """Scorecard must meet go/no-go threshold."""

    def test_weighted_score_at_least_90(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        assert scorecard.weighted_score >= 90.0, (
            f"Weighted score {scorecard.weighted_score} < 90"
        )

    def test_go_recommendation(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        assert scorecard.go is True, (
            f"Go recommendation is False. Score: {scorecard.weighted_score}, "
            f"Failed gates: {[g.gate_name for g in scorecard.gates if not g.passed]}"
        )

    def test_scorecard_serializes(self):
        validator = ReleaseGateValidator()
        scorecard = validator.validate_all(ARCHON_ROOT)
        d = scorecard.to_dict()
        assert "gates" in d
        assert "weighted_score" in d
        assert "go" in d
        assert "hard_gates_passed" in d


# ---------------------------------------------------------------------------
# E6-S3: Docs readiness
# ---------------------------------------------------------------------------

class TestDocsReadiness:
    """Documentation and runbook artifacts must exist."""

    def test_prompts_directory_exists(self):
        assert (ARCHON_ROOT / "prompts").is_dir()

    def test_system_prompt_exists(self):
        assert (ARCHON_ROOT / "prompts" / "system.md").exists()

    def test_schemas_have_descriptions(self):
        schemas_dir = ARCHON_ROOT / "schemas"
        import yaml
        for schema_path in schemas_dir.glob("*.schema.yaml"):
            with open(schema_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert "description" in data or "title" in data, (
                f"Schema {schema_path.name} has no description or title"
            )

    def test_docs_exist(self):
        docs_dir = ARCHON_ROOT / "docs"
        assert docs_dir.is_dir()
        getting_started = docs_dir / "getting-started.md"
        assert getting_started.exists(), "getting-started.md docs not found"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_gate(scorecard: ReleaseScorecard, name: str):
    for g in scorecard.gates:
        if g.gate_name == name:
            return g
    raise ValueError(f"Gate '{name}' not found in scorecard")
