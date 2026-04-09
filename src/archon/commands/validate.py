"""``archon validate`` — manifest & skill validation (US-5, FR-034 through FR-038)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
import yaml

from archon.core.registry import Registry
from archon.utils.output import (
    console, print_success, print_error, print_warning, print_info, print_verbose,
    is_json, json_envelope, print_json,
)
from archon.utils.paths import get_archon_root


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


_ALLOWED_COST_TIERS = {"fast", "standard", "premium"}
_REQUIRED_CAPABILITIES = {"streaming", "multi-turn", "file-output", "self-evaluation", "context-aware"}


def _validate_card_section(agent_name: str, card_data: dict) -> list[str]:
    """Validate the card: section of an agent manifest. Returns list of error strings."""
    errors: list[str] = []

    # Capabilities
    caps = card_data.get("capabilities")
    if caps is None:
        errors.append(f"card.capabilities: required field missing")
    elif not isinstance(caps, dict):
        errors.append(f"card.capabilities: expected object, got {type(caps).__name__}")
    else:
        for cap_name in _REQUIRED_CAPABILITIES:
            if cap_name not in caps:
                errors.append(f"card.capabilities.{cap_name}: required field missing")
            elif not isinstance(caps[cap_name], bool):
                errors.append(f"card.capabilities.{cap_name}: expected boolean, got {type(caps[cap_name]).__name__}")

    # Skills provided
    skills = card_data.get("skills-provided")
    if skills is None:
        errors.append(f"card.skills-provided: required field missing")
    elif not isinstance(skills, list):
        errors.append(f"card.skills-provided: expected list, got {type(skills).__name__}")
    elif len(skills) < 1:
        errors.append(f"card.skills-provided: 0 items < minimum 1")
    else:
        for i, skill in enumerate(skills):
            if not isinstance(skill, dict):
                errors.append(f"card.skills-provided[{i}]: expected object, got {type(skill).__name__}")
                continue
            for req_field in ("id", "name", "description"):
                if req_field not in skill:
                    errors.append(f"card.skills-provided[{i}].{req_field}: required field missing")

    # Input modes
    in_modes = card_data.get("input-modes")
    if in_modes is None:
        errors.append(f"card.input-modes: required field missing")
    elif not isinstance(in_modes, list):
        errors.append(f"card.input-modes: expected list, got {type(in_modes).__name__}")
    elif len(in_modes) < 1:
        errors.append(f"card.input-modes: 0 items < minimum 1")

    # Output modes
    out_modes = card_data.get("output-modes")
    if out_modes is None:
        errors.append(f"card.output-modes: required field missing")
    elif not isinstance(out_modes, list):
        errors.append(f"card.output-modes: expected list, got {type(out_modes).__name__}")
    elif len(out_modes) < 1:
        errors.append(f"card.output-modes: 0 items < minimum 1")

    # Cost tier
    cost_tier = card_data.get("cost-tier")
    if cost_tier is None:
        errors.append(f"card.cost-tier: required field missing")
    elif cost_tier not in _ALLOWED_COST_TIERS:
        errors.append(f"card.cost-tier: '{cost_tier}' not in allowed values [fast, standard, premium]")

    # Avg tokens
    avg_tokens = card_data.get("avg-tokens")
    if avg_tokens is None:
        errors.append(f"card.avg-tokens: required field missing")
    elif not isinstance(avg_tokens, dict):
        errors.append(f"card.avg-tokens: expected object, got {type(avg_tokens).__name__}")
    else:
        for token_field in ("input", "output"):
            val = avg_tokens.get(token_field)
            if val is None:
                errors.append(f"card.avg-tokens.{token_field}: required field missing")
            elif isinstance(val, bool):
                errors.append(f"card.avg-tokens.{token_field}: expected integer, got boolean")
            elif isinstance(val, float):
                errors.append(f"card.avg-tokens.{token_field}: expected integer, got float")
            elif not isinstance(val, int):
                errors.append(f"card.avg-tokens.{token_field}: expected integer, got {type(val).__name__}")
            elif val < 0:
                errors.append(f"card.avg-tokens.{token_field}: must be ≥ 0")

    # Quality metrics (optional)
    qm = card_data.get("quality-metrics")
    if qm is not None and isinstance(qm, dict):
        for float_field in ("completeness", "last-eval-score"):
            if float_field in qm:
                fv = qm[float_field]
                if not isinstance(fv, (int, float)):
                    errors.append(f"card.quality-metrics.{float_field}: expected float, got {type(fv).__name__}")
                elif fv < 0.0:
                    errors.append(f"card.quality-metrics.{float_field}: {fv} below minimum 0.0")
                elif fv > 1.0:
                    errors.append(f"card.quality-metrics.{float_field}: {fv} exceeds maximum 1.0")
        if "eval-count" in qm:
            ec = qm["eval-count"]
            if isinstance(ec, bool):
                errors.append(f"card.quality-metrics.eval-count: expected integer, got boolean")
            elif not isinstance(ec, int):
                errors.append(f"card.quality-metrics.eval-count: expected integer, got {type(ec).__name__}")
            elif ec < 0:
                errors.append(f"card.quality-metrics.eval-count: must be ≥ 0")

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

    # Card validation (FR-AC-033 through FR-AC-035)
    card_data = manifest.get("card")
    if card_data is not None and isinstance(card_data, dict) and card_data:
        result["errors"].extend(_validate_card_section(agent_dir.name, card_data))
    elif card_data is not None and (not isinstance(card_data, dict) or not card_data):
        result["warnings"].append("card section is empty or null (treated as absent)")
    else:
        result["warnings"].append("card section missing (recommended)")

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


# ── Catalog validation (FR-CAT-061) ────────────────────────────

_CATALOG_VALID_CATEGORIES = {"core", "development", "database", "research", "design", "ai", "cloud", "communication"}
_KEBAB_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")


def _validate_catalog(root: Path) -> dict:
    """Validate the MCP server catalog file against its schema."""
    result = {"path": "catalog/mcp-servers.yaml", "errors": [], "warnings": [], "status": "passed"}

    catalog_path = root / "catalog" / "mcp-servers.yaml"
    if not catalog_path.exists():
        # Catalog is optional — just note it
        result["warnings"].append("MCP catalog file not found (optional)")
        result["status"] = "warnings"
        return result

    try:
        with open(catalog_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:
        result["errors"].append(f"YAML parse error: {exc}")
        result["status"] = "failed"
        return result

    # Root fields
    if "schema_version" not in data:
        result["errors"].append("Missing required field: schema_version")

    servers = data.get("servers")
    if servers is None:
        result["errors"].append("Missing required field: servers")
        result["status"] = "failed"
        return result

    if not isinstance(servers, list):
        result["errors"].append("Field 'servers' must be a list")
        result["status"] = "failed"
        return result

    if len(servers) == 0:
        result["errors"].append("Field 'servers' must have at least 1 entry")

    # Validate each server entry
    seen_names: set[str] = set()
    for i, entry in enumerate(servers):
        prefix = f"servers[{i}]"
        if not isinstance(entry, dict):
            result["errors"].append(f"{prefix}: expected object, got {type(entry).__name__}")
            continue

        # Required fields
        name = entry.get("name")
        if name is None:
            result["errors"].append(f"{prefix}: missing required field 'name'")
        elif not isinstance(name, str):
            result["errors"].append(f"{prefix}.name: expected string, got {type(name).__name__}")
        else:
            prefix = f"servers[{i}] ({name})"
            if not _KEBAB_PATTERN.match(name):
                result["errors"].append(f"{prefix}.name: '{name}' doesn't match kebab-case pattern")
            if name in seen_names:
                result["errors"].append(f"{prefix}.name: duplicate name '{name}'")
            seen_names.add(name)

        package = entry.get("package")
        if package is None:
            result["errors"].append(f"{prefix}: missing required field 'package'")
        elif not isinstance(package, str):
            result["errors"].append(f"{prefix}.package: expected string")

        category = entry.get("category")
        if category is None:
            result["errors"].append(f"{prefix}: missing required field 'category'")
        elif category not in _CATALOG_VALID_CATEGORIES:
            result["errors"].append(f"{prefix}.category: '{category}' not in allowed values")

        desc = entry.get("description")
        if desc is None:
            result["errors"].append(f"{prefix}: missing required field 'description'")
        elif not isinstance(desc, str):
            result["errors"].append(f"{prefix}.description: expected string")
        elif len(desc) < 10:
            result["errors"].append(f"{prefix}.description: length {len(desc)} < minimum 10")
        elif len(desc) > 300:
            result["errors"].append(f"{prefix}.description: length {len(desc)} > maximum 300")

        install_cmd = entry.get("install-command")
        if install_cmd is None:
            result["errors"].append(f"{prefix}: missing required field 'install-command'")
        elif not isinstance(install_cmd, str):
            result["errors"].append(f"{prefix}.install-command: expected string")

        tags = entry.get("tags")
        if tags is None:
            result["errors"].append(f"{prefix}: missing required field 'tags'")
        elif not isinstance(tags, list):
            result["errors"].append(f"{prefix}.tags: expected list")
        elif len(tags) < 1:
            result["errors"].append(f"{prefix}.tags: must have at least 1 tag")

        # Optional: required-env
        req_env = entry.get("required-env")
        if req_env is not None:
            if not isinstance(req_env, list):
                result["errors"].append(f"{prefix}.required-env: expected list")
            else:
                for j, ev in enumerate(req_env):
                    if isinstance(ev, dict):
                        if "name" not in ev:
                            result["errors"].append(f"{prefix}.required-env[{j}]: missing 'name'")
                        if "description" not in ev:
                            result["errors"].append(f"{prefix}.required-env[{j}]: missing 'description'")

        # Optional: server-type
        stype = entry.get("server-type")
        if stype is not None and stype not in ("stdio", "sse", "http"):
            result["errors"].append(f"{prefix}.server-type: '{stype}' not in [stdio, sse]")

    if result["errors"]:
        result["status"] = "failed"
    elif result["warnings"]:
        result["status"] = "warnings"
    return result


# ── Command ─────────────────────────────────────────────────────

def validate_cmd(
    path: Optional[str] = typer.Argument(None, help="Path to a skill/agent/bundle directory to validate."),
    check_llms_txt: bool = typer.Option(False, "--check-llms-txt", help="Check if llms.txt files are up to date."),
    check_agent_cards: bool = typer.Option(False, "--check-agent-cards", help="Check if agent-cards.json is up to date."),
) -> None:
    """Validate manifests, SKILL.md / AGENT.md, and dependency references."""

    root = get_archon_root()
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

        # MCP Catalog (FR-CAT-061)
        catalog_path = root / "catalog" / "mcp-servers.yaml"
        if catalog_path.exists():
            results.append(_validate_catalog(root))

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

    # ── llms.txt freshness check (FR-043 through FR-048) ────────
    if check_llms_txt:
        from archon.core.llms_txt import generate_concise, generate_full

        if not is_json():
            console.print()
            console.rule("[bold]llms.txt Freshness Check[/bold]")

        for filename, gen_fn in [("llms.txt", generate_concise), ("llms-full.txt", generate_full)]:
            file_path = root / filename
            if not file_path.exists():
                if not is_json():
                    console.print(f"  [yellow]⚠[/yellow] {filename} not found — generate with: archon generate llms-txt")
            else:
                expected = gen_fn(root)
                actual = file_path.read_text(encoding="utf-8")
                # For llms-full.txt, ignore the Generated: date line
                if filename == "llms-full.txt":
                    expected_cmp = re.sub(r"^- Generated: .+$", "", expected, count=1, flags=re.MULTILINE)
                    actual_cmp = re.sub(r"^- Generated: .+$", "", actual, count=1, flags=re.MULTILINE)
                else:
                    expected_cmp = expected
                    actual_cmp = actual

                if expected_cmp == actual_cmp:
                    if not is_json():
                        console.print(f"  [green]✓[/green] {filename} is up to date")
                else:
                    if not is_json():
                        console.print(f"  [yellow]⚠[/yellow] {filename} is stale — regenerate with: archon generate llms-txt")

        if not is_json():
            console.print()

    # ── agent-cards.json freshness check (FR-AC-036) ────────────
    if check_agent_cards:
        from archon.core.agent_cards import generate_agent_cards

        if not is_json():
            console.print()
            console.rule("[bold]agent-cards.json Freshness Check[/bold]")

        file_path = root / "agent-cards.json"
        if not file_path.exists():
            if not is_json():
                console.print(f"  [yellow]⚠[/yellow] agent-cards.json not found — generate with: archon generate agent-cards")
        else:
            expected = generate_agent_cards(root)
            actual = file_path.read_text(encoding="utf-8")
            # Ignore the "generated" timestamp when comparing
            expected_cmp = re.sub(r'"generated":\s*"[^"]+"', '"generated": ""', expected)
            actual_cmp = re.sub(r'"generated":\s*"[^"]+"', '"generated": ""', actual)

            if expected_cmp == actual_cmp:
                if not is_json():
                    console.print(f"  [green]✓[/green] agent-cards.json is up to date")
            else:
                if not is_json():
                    console.print(f"  [yellow]⚠[/yellow] agent-cards.json is stale — regenerate with: archon generate agent-cards")

        if not is_json():
            console.print()
