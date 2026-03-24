"""
Archon Artifact Validator — Validates pipeline step outputs.

Checks:
- File existence (glob patterns)
- Required markdown sections (heading validation)
- Minimum content length (word count)
- Schema compliance (YAML/JSON validation)
- Compliance score thresholds (for review steps)
"""

from __future__ import annotations

import glob as glob_module
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    """Result of artifact validation."""
    passed: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 100.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": self.checks,
            "errors": self.errors,
            "warnings": self.warnings,
            "score": self.score,
        }


class ArtifactValidator:
    """
    Validates pipeline artifacts between steps.

    Used by post-step hooks and the pipeline engine to ensure
    each step produces valid, complete outputs before proceeding.
    """

    def validate_exists(self, pattern: str, base_dir: str = ".") -> ValidationResult:
        """Check if files matching the pattern exist."""
        result = ValidationResult(passed=True)
        matches = glob_module.glob(str(Path(base_dir) / pattern))

        check = {
            "type": "file_exists",
            "pattern": pattern,
            "base_dir": base_dir,
            "found": len(matches),
            "files": [str(m) for m in matches],
        }

        if not matches:
            result.passed = False
            result.errors.append(f"No files found matching '{pattern}' in '{base_dir}'")
            check["status"] = "fail"
        else:
            check["status"] = "pass"

        result.checks.append(check)
        return result

    def validate_sections(
        self, filepath: str, required_sections: list[str]
    ) -> ValidationResult:
        """Check that a markdown file contains required section headings."""
        result = ValidationResult(passed=True)
        path = Path(filepath)

        check: dict[str, Any] = {
            "type": "required_sections",
            "file": filepath,
            "required": required_sections,
            "found": [],
            "missing": [],
        }

        if not path.exists():
            result.passed = False
            result.errors.append(f"File not found: {filepath}")
            check["status"] = "fail"
            result.checks.append(check)
            return result

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            result.passed = False
            result.errors.append(f"Cannot read file: {e}")
            check["status"] = "fail"
            result.checks.append(check)
            return result

        headings = set()
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                heading_text = stripped.lstrip("#").strip().lower()
                headings.add(heading_text)

        for section in required_sections:
            normalized = section.lower().strip()
            if normalized in headings:
                check["found"].append(section)
            else:
                check["missing"].append(section)

        if check["missing"]:
            result.passed = False
            for section in check["missing"]:
                result.errors.append(f"Missing required section: '{section}'")
            check["status"] = "fail"
        else:
            check["status"] = "pass"

        result.checks.append(check)
        return result

    def validate_min_content(
        self, filepath: str, min_words: int
    ) -> ValidationResult:
        """Check that a file has minimum word count."""
        result = ValidationResult(passed=True)
        path = Path(filepath)

        check: dict[str, Any] = {
            "type": "min_content",
            "file": filepath,
            "min_words": min_words,
            "actual_words": 0,
        }

        if not path.exists():
            result.passed = False
            result.errors.append(f"File not found: {filepath}")
            check["status"] = "fail"
            result.checks.append(check)
            return result

        try:
            content = path.read_text(encoding="utf-8")
            word_count = len(content.split())
            check["actual_words"] = word_count

            if word_count < min_words:
                result.passed = False
                result.errors.append(
                    f"Content too short: {word_count} words (minimum: {min_words})"
                )
                check["status"] = "fail"
            else:
                check["status"] = "pass"
        except Exception as e:
            result.passed = False
            result.errors.append(f"Cannot read file: {e}")
            check["status"] = "fail"

        result.checks.append(check)
        return result

    def validate_schema(
        self, filepath: str, schema_path: str
    ) -> ValidationResult:
        """Validate a YAML/JSON file against a schema."""
        import yaml

        result = ValidationResult(passed=True)
        path = Path(filepath)
        s_path = Path(schema_path)

        check: dict[str, Any] = {
            "type": "schema_validation",
            "file": filepath,
            "schema": schema_path,
        }

        if not path.exists():
            result.passed = False
            result.errors.append(f"File not found: {filepath}")
            check["status"] = "fail"
            result.checks.append(check)
            return result

        if not s_path.exists():
            result.warnings.append(f"Schema not found: {schema_path} — skipping validation")
            check["status"] = "skip"
            result.checks.append(check)
            return result

        try:
            with open(path, "r", encoding="utf-8") as f:
                if filepath.endswith(".json"):
                    import json
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            with open(s_path, "r", encoding="utf-8") as f:
                schema = yaml.safe_load(f)

            # Basic structural validation (required fields)
            required_fields = schema.get("required", [])
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                result.passed = False
                for field_name in missing_fields:
                    result.errors.append(f"Missing required field: '{field_name}'")
                check["status"] = "fail"
                check["missing_fields"] = missing_fields
            else:
                check["status"] = "pass"

        except Exception as e:
            result.passed = False
            result.errors.append(f"Schema validation error: {e}")
            check["status"] = "fail"

        result.checks.append(check)
        return result

    def validate_compliance_score(
        self, score: float, threshold: float
    ) -> ValidationResult:
        """Check if a compliance score meets the threshold."""
        result = ValidationResult(passed=True)

        check = {
            "type": "compliance_score",
            "score": score,
            "threshold": threshold,
        }

        if score < threshold:
            result.passed = False
            result.errors.append(
                f"Compliance score {score:.1f}% below threshold {threshold:.1f}%"
            )
            check["status"] = "fail"
        else:
            check["status"] = "pass"

        result.checks.append(check)
        result.score = score
        return result

    def validate_step_output(
        self,
        validation_config: dict[str, Any],
        project_dir: str = ".",
    ) -> ValidationResult:
        """
        Run all validations defined in a step's validation config.

        Args:
            validation_config: Dict with keys:
                - expected-artifacts: list of {path-pattern, description}
                - required-sections: list of heading strings
                - min-word-count: int
                - compliance-threshold: float

        Returns:
            Combined ValidationResult
        """
        combined = ValidationResult(passed=True)

        # Artifact existence
        for artifact in validation_config.get("expected-artifacts", []):
            pattern = artifact.get("path-pattern", "")
            if pattern:
                r = self.validate_exists(pattern, project_dir)
                combined.checks.extend(r.checks)
                combined.errors.extend(r.errors)
                combined.warnings.extend(r.warnings)
                if not r.passed:
                    combined.passed = False

        # Required sections
        sections = validation_config.get("required-sections", [])
        if sections:
            for artifact in validation_config.get("expected-artifacts", []):
                pattern = artifact.get("path-pattern", "")
                if pattern:
                    matches = glob_module.glob(str(Path(project_dir) / pattern))
                    for match in matches:
                        if match.endswith(".md"):
                            r = self.validate_sections(match, sections)
                            combined.checks.extend(r.checks)
                            combined.errors.extend(r.errors)
                            if not r.passed:
                                combined.passed = False

        # Min word count
        min_words = validation_config.get("min-word-count", 0)
        if min_words > 0:
            for artifact in validation_config.get("expected-artifacts", []):
                pattern = artifact.get("path-pattern", "")
                if pattern:
                    matches = glob_module.glob(str(Path(project_dir) / pattern))
                    for match in matches:
                        r = self.validate_min_content(match, min_words)
                        combined.checks.extend(r.checks)
                        combined.errors.extend(r.errors)
                        if not r.passed:
                            combined.passed = False

        # Compliance threshold
        threshold = validation_config.get("compliance-threshold", 0)
        if threshold > 0:
            # Score must be provided externally
            combined.warnings.append(
                f"Compliance threshold set to {threshold}% — requires external score"
            )

        return combined
