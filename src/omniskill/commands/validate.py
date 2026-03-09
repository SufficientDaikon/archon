"""``omniskill validate`` — manifest & skill validation (US-5, FR-034 through FR-038)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
import yaml

from omniskill.core.registry import Registry
from omniskill.utils.output import (
    console, print_success, print_error, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json,
)
from omniskill.utils.paths import get_omniskill_root


# ── Validation helpers ──────────────────────────────────────────

def _validate_field(field_name: str, value, schema: dict) -> list[str]:
    """Validate a single field against its schema. Returns list of error strings."""
    errors: list[str] = []
    ftype = schema.get("type")

    if ftype == "string":
        if not isinstance(value, str):
            errors.append(f"{field_name}: expected string, got {type(value).__name__}")
            return errors
        pat = schema.get("pattern")
        if pat and not re.match(pat, value):
            errors.append(f"{field_name}: '{value}' doesn't match pattern {pat}")
        minl = schema.get("min_length")
        if minl and len(value) < minl:
            errors.append(f"{field_name}: length {len(value)} < minimum {minl}")
        maxl = schema.get("max_length")
        if maxl and len(value) > maxl:
            errors.append(f"{field_name}: length {len(value)} > maximum {maxl}")

    elif ftype == "list":
        if not isinstance(value, list):
            errors.append(f"{field_name}: expected list, got {type(value).__name__}")
            return errors
        mini = schema.get("min_items")
        if mini and len(value) < mini:
            errors.append(f"{field_name}: {len(value)} items < minimum {mini}")
        allowed = schema.get("allowed_values")
        if allowed:
            for item in value:
                if item not in allowed:
                    errors.append(f"{field_name}: '{item}' not in allowed values")

    elif ftype == "object":
        if not isinstance(value, dict):
            errors.append(f"{field_name}: expected object, got {type(value).__name__}")
            return errors
        for child_name, child_schema in schema.get("required_children", {}).items():
            if child_name not in value:
                errors.append(f"{field_name}.{child_name}: required field missing")
            else:
                errors.extend(_validate_field(f"{field_name}.{child_name}", value[child_name], child_schema))

    return errors


def _validate_skill(skill_dir: Path, root: Path) -> dict:
    """Validate a single skill directory. Returns a result dict."""
    result = {"path": str(skill_dir.relative_to(root)), "errors": [], "warnings": [], "status": "passed"}

    manifest_path = skill_dir / "manifest.yaml"
    skill_md_path = skill_dir / "SKILL.md"

    # Check files exist
    if not manifest_path.exists():
        result["errors"].append("manifest.yaml not found")
        result["status"] = "failed"
        return result

    # Parse manifest
    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh) or {}
    except Exception as exc:
        result["errors"].append(f"YAML parse error: {exc}")
        result["status"] = "failed"
        return result

    # Load schema
    schema_path = root / "schemas" / "skill-manifest.schema.yaml"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema = yaml.safe_load(fh) or {}

        for field_name, field_schema in schema.get("required_fields", {}).items():
            if field_name not in manifest:
                result["errors"].append(f"Required field missing: {field_name}")
            else:
                result["errors"].extend(_validate_field(field_name, manifest[field_name], field_schema))

        # Extra fields warning
        known = set(schema.get("required_fields", {}).keys()) | set(schema.get("optional_fields", {}).keys())
        for key in manifest:
            if key not in known:
                result["warnings"].append(f"Unknown field: {key}")
    else:
        # Minimal validation without schema file
        for req in ["name", "version"]:
            if req not in manifest:
                result["errors"].append(f"Required field missing: {req}")

    # Validate SKILL.md
    if not skill_md_path.exists():
        result["errors"].append("SKILL.md not found")
    else:
        try:
            content = skill_md_path.read_text(encoding="utf-8")
        except Exception:
            content = ""

        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as fh:
                schema = yaml.safe_load(fh) or {}
            for section in schema.get("skill_md_required_sections", []):
                pattern = rf"(?i)^#+\s*{re.escape(section)}"
                if not re.search(pattern, content, re.MULTILINE):
                    result["warnings"].append(f"SKILL.md: missing recommended section '{section}'")

        if not content.strip():
            result["errors"].append("SKILL.md is empty")

    if result["errors"]:
        result["status"] = "failed"
    elif result["warnings"]:
        result["status"] = "warnings"

    return result


def _validate_agent(agent_dir: Path, root: Path) -> dict:
    """Validate a single agent directory."""
    result = {"path": str(agent_dir.relative_to(root)), "errors": [], "warnings": [], "status": "passed"}

    manifest_path = agent_dir / "agent-manifest.yaml"
    agent_md_path = agent_dir / "AGENT.md"

    if not manifest_path.exists():
        result["errors"].append("agent-manifest.yaml not found")
        result["status"] = "failed"
        return result

    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh) or {}
    except Exception as exc:
        result["errors"].append(f"YAML parse error: {exc}")
        result["status"] = "failed"
        return result

    # Schema validation
    schema_path = root / "schemas" / "agent-manifest.schema.yaml"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema = yaml.safe_load(fh) or {}
        for field_name, field_schema in schema.get("required_fields", {}).items():
            if field_name not in manifest:
                result["errors"].append(f"Required field missing: {field_name}")
            else:
                result["errors"].extend(_validate_field(field_name, manifest[field_name], field_schema))

    if not agent_md_path.exists():
        result["errors"].append("AGENT.md not found")

    if result["errors"]:
        result["status"] = "failed"
    elif result["warnings"]:
        result["status"] = "warnings"
    return result


def _validate_bundle(bundle_dir: Path, root: Path) -> dict:
    """Validate a single bundle directory."""
    result = {"path": str(bundle_dir.relative_to(root)), "errors": [], "warnings": [], "status": "passed"}

    manifest_path = bundle_dir / "bundle.yaml"
    if not manifest_path.exists():
        result["errors"].append("bundle.yaml not found")
        result["status"] = "failed"
        return result

    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh) or {}
    except Exception as exc:
        result["errors"].append(f"YAML parse error: {exc}")
        result["status"] = "failed"
        return result

    # Schema validation
    schema_path = root / "schemas" / "bundle-manifest.schema.yaml"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema = yaml.safe_load(fh) or {}
        for field_name, field_schema in schema.get("required_fields", {}).items():
            if field_name not in manifest:
                result["errors"].append(f"Required field missing: {field_name}")
            else:
                result["errors"].extend(_validate_field(field_name, manifest[field_name], field_schema))

    # Check skill references (FR-036)
    skills_dir = root / "skills"
    for skill_name in manifest.get("skills", []):
        if not (skills_dir / skill_name).exists():
            result["errors"].append(f"Referenced skill not found: {skill_name}")

    if result["errors"]:
        result["status"] = "failed"
    elif result["warnings"]:
        result["status"] = "warnings"
    return result


def _validate_synapse(synapse_dir: Path, root: Path) -> dict:
    """Validate a single synapse directory."""
    result = {"path": str(synapse_dir.relative_to(root)), "errors": [], "warnings": [], "status": "passed"}

    manifest_path = synapse_dir / "manifest.yaml"
    synapse_md_path = synapse_dir / "SYNAPSE.md"

    if not manifest_path.exists():
        result["errors"].append("manifest.yaml not found")
        result["status"] = "failed"
        return result

    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh) or {}
    except Exception as exc:
        result["errors"].append(f"YAML parse error: {exc}")
        result["status"] = "failed"
        return result

    # Schema validation
    schema_path = root / "schemas" / "synapse-manifest.schema.yaml"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema = yaml.safe_load(fh) or {}
        for field_name, field_schema in schema.get("required_fields", {}).items():
            if field_name not in manifest:
                result["errors"].append(f"Required field missing: {field_name}")
            else:
                result["errors"].extend(_validate_field(field_name, manifest[field_name], field_schema))

    # Validate SYNAPSE.md
    if not synapse_md_path.exists():
        result["errors"].append("SYNAPSE.md not found")
    else:
        try:
            content = synapse_md_path.read_text(encoding="utf-8")
        except Exception:
            content = ""

        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as fh:
                schema = yaml.safe_load(fh) or {}
            for section in schema.get("synapse_md_required_sections", []):
                pattern = rf"(?i)^#+\s*{re.escape(section)}"
                if not re.search(pattern, content, re.MULTILINE):
                    result["warnings"].append(f"SYNAPSE.md: missing recommended section '{section}'")

        if not content.strip():
            result["errors"].append("SYNAPSE.md is empty")

    # Validate resource references
    for res in manifest.get("resources", []):
        res_path = synapse_dir / res.get("path", "")
        if not res_path.exists():
            result["warnings"].append(f"Resource not found: {res.get('path', '?')}")

    if result["errors"]:
        result["status"] = "failed"
    elif result["warnings"]:
        result["status"] = "warnings"
    return result


# ── Command ─────────────────────────────────────────────────────

def validate_cmd(
    path: Optional[str] = typer.Argument(None, help="Path to a skill/agent/bundle directory to validate."),
) -> None:
    """Validate manifests, SKILL.md / AGENT.md, and dependency references."""

    root = get_omniskill_root()
    results: list[dict] = []

    if path:
        # FR-037: Validate specific path
        p = Path(path)
        if not p.is_absolute():
            p = root / p
        if not p.exists():
            print_error(f"Path not found: {p}")
            raise typer.Exit(1)

        if (p / "SYNAPSE.md").exists():
            results.append(_validate_synapse(p, root))
        elif (p / "manifest.yaml").exists():
            results.append(_validate_skill(p, root))
        elif (p / "agent-manifest.yaml").exists():
            results.append(_validate_agent(p, root))
        elif (p / "bundle.yaml").exists():
            results.append(_validate_bundle(p, root))
        else:
            print_error(f"Not a valid skill, agent, bundle, or synapse directory: {p}")
            raise typer.Exit(1)
    else:
        # FR-037: Validate entire registry
        if not is_json():
            console.print("\n[bold]Validating entire registry...[/bold]\n")

        # Skills
        skills_dir = root / "skills"
        if skills_dir.exists():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir() and (d / "manifest.yaml").exists():
                    results.append(_validate_skill(d, root))

        # Agents
        agents_dir = root / "agents"
        if agents_dir.exists():
            for d in sorted(agents_dir.iterdir()):
                if d.is_dir() and (d / "agent-manifest.yaml").exists():
                    results.append(_validate_agent(d, root))

        # Bundles
        bundles_dir = root / "bundles"
        if bundles_dir.exists():
            for d in sorted(bundles_dir.iterdir()):
                if d.is_dir() and (d / "bundle.yaml").exists():
                    results.append(_validate_bundle(d, root))

        # Synapses
        synapses_dir = root / "synapses"
        if synapses_dir.exists():
            for d in sorted(synapses_dir.iterdir()):
                if d.is_dir() and d.name != "_template" and (d / "manifest.yaml").exists():
                    results.append(_validate_synapse(d, root))

    # ── Output ──────────────────────────────────────────────────

    passed = [r for r in results if r["status"] == "passed"]
    warnings = [r for r in results if r["status"] == "warnings"]
    failed = [r for r in results if r["status"] == "failed"]

    if is_json():
        print_json(json_envelope(
            command="validate",
            status="success" if not failed else "error",
            data={
                "total": len(results),
                "passed": len(passed),
                "warnings": len(warnings),
                "failed": len(failed),
                "results": results,
            },
        ))
        if failed:
            raise typer.Exit(2)
        return

    # Rich output
    for r in results:
        if r["status"] == "passed":
            console.print(f"  [green]✓[/green] {r['path']}")
        elif r["status"] == "warnings":
            console.print(f"  [yellow]⚠[/yellow] {r['path']}")
            for w in r["warnings"]:
                console.print(f"      [yellow]{w}[/yellow]")
        else:
            console.print(f"  [red]✗[/red] {r['path']}")
            for e in r["errors"]:
                console.print(f"      [red]{e}[/red]")
            for w in r["warnings"]:
                console.print(f"      [yellow]{w}[/yellow]")

    console.print()
    console.rule("[bold]Validation Summary[/bold]")
    console.print(f"  ✅ Passed:   {len(passed)}")
    console.print(f"  ⚠  Warnings: {len(warnings)}")
    console.print(f"  ❌ Failed:   {len(failed)}")
    console.print(f"  📊 Total:    {len(results)}")
    console.print()

    # FR-038: exit code 2 for validation failures
    if failed:
        raise typer.Exit(2)
