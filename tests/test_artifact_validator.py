"""
Archon v2.0 Test Suite — Artifact Validator Tests

Tests file existence, section validation, word count, and schema validation.
"""

import sys
import tempfile
from pathlib import Path

import pytest

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "src"))


class TestValidateExists:
    """Test file existence validation."""

    def test_existing_file(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.md").write_text("hello")
            result = validator.validate_exists("test.md", tmpdir)
            assert result.passed is True

    def test_missing_file(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validator.validate_exists("nonexistent.md", tmpdir)
            assert result.passed is False
            assert len(result.errors) > 0

    def test_glob_pattern(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "spec.md").write_text("spec content")
            Path(tmpdir, "design.md").write_text("design content")
            result = validator.validate_exists("*.md", tmpdir)
            assert result.passed is True
            assert result.checks[0]["found"] == 2


class TestValidateSections:
    """Test markdown section heading validation."""

    def test_all_sections_present(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "# Introduction\n\nHello\n\n## Requirements\n\nStuff\n\n## Architecture\n\nMore"
            filepath = str(Path(tmpdir, "spec.md"))
            Path(filepath).write_text(content)

            result = validator.validate_sections(filepath, ["Introduction", "Requirements", "Architecture"])
            assert result.passed is True

    def test_missing_section(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "# Introduction\n\nHello"
            filepath = str(Path(tmpdir, "spec.md"))
            Path(filepath).write_text(content)

            result = validator.validate_sections(filepath, ["Introduction", "Requirements"])
            assert result.passed is False
            assert any("Requirements" in e for e in result.errors)

    def test_file_not_found(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        result = validator.validate_sections("/nonexistent/file.md", ["Test"])
        assert result.passed is False

    def test_case_insensitive_sections(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "# INTRODUCTION\n\nHello"
            filepath = str(Path(tmpdir, "spec.md"))
            Path(filepath).write_text(content)

            result = validator.validate_sections(filepath, ["introduction"])
            assert result.passed is True


class TestValidateMinContent:
    """Test minimum word count validation."""

    def test_sufficient_words(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = " ".join(["word"] * 100)
            filepath = str(Path(tmpdir, "doc.md"))
            Path(filepath).write_text(content)

            result = validator.validate_min_content(filepath, 50)
            assert result.passed is True

    def test_insufficient_words(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "Just a few words"
            filepath = str(Path(tmpdir, "doc.md"))
            Path(filepath).write_text(content)

            result = validator.validate_min_content(filepath, 100)
            assert result.passed is False

    def test_empty_file(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir, "empty.md"))
            Path(filepath).write_text("")

            result = validator.validate_min_content(filepath, 10)
            assert result.passed is False


class TestValidateComplianceScore:
    """Test compliance score threshold validation."""

    def test_passing_score(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        result = validator.validate_compliance_score(85.0, 80.0)
        assert result.passed is True

    def test_failing_score(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        result = validator.validate_compliance_score(60.0, 80.0)
        assert result.passed is False

    def test_exact_threshold(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        result = validator.validate_compliance_score(80.0, 80.0)
        assert result.passed is True


class TestValidateStepOutput:
    """Test combined step output validation."""

    def test_full_validation_pass(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "# Spec\n\n" + " ".join(["word"] * 200) + "\n\n## Requirements\n\nStuff"
            Path(tmpdir, "spec.md").write_text(content)

            config = {
                "expected-artifacts": [{"path-pattern": "spec.md"}],
                "required-sections": ["Spec", "Requirements"],
                "min-word-count": 50,
            }
            result = validator.validate_step_output(config, tmpdir)
            assert result.passed is True

    def test_full_validation_fail_missing_artifact(self):
        from archon.core.artifact_validator import ArtifactValidator

        validator = ArtifactValidator()
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "expected-artifacts": [{"path-pattern": "missing.md"}],
            }
            result = validator.validate_step_output(config, tmpdir)
            assert result.passed is False


class TestValidationResult:
    """Test ValidationResult data class."""

    def test_to_dict(self):
        from archon.core.artifact_validator import ValidationResult

        result = ValidationResult(
            passed=True,
            checks=[{"type": "test", "status": "pass"}],
            errors=[],
            warnings=["something minor"],
            score=95.0,
        )
        d = result.to_dict()
        assert d["passed"] is True
        assert d["score"] == 95.0
        assert len(d["warnings"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
