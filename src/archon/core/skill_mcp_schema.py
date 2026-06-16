"""skill_mcp_schema — Generate MCP Tool schemas from Archon skill manifests.

Converts skill YAML manifests into MCP-compatible tool definitions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def skill_to_mcp_tool(skill_manifest: dict[str, Any]) -> dict[str, Any]:
    """Convert an Archon skill manifest dict to an MCP Tool schema.

    Archon skills are invoked by natural-language triggers, not typed APIs.
    When the manifest declares an explicit ``input-schema``, we honour it.
    Otherwise we synthesise a minimal-but-correct ``inputSchema`` that exposes
    the single ``prompt`` parameter every skill actually accepts.

    The skill's ``output-schema`` (what the skill *produces*) is NOT placed
    inside ``inputSchema`` — doing so would be the inversion bug.  It is
    surfaced as a non-standard ``annotations.outputSchema`` entry so capable
    MCP clients can display it without breaking standard clients.
    """
    name = skill_manifest.get("name", "")
    description = skill_manifest.get("description", "")

    explicit_input = skill_manifest.get("input-schema")

    if explicit_input and isinstance(explicit_input, dict):
        # Honour an explicit input-schema declaration.
        # Support both full JSON Schema (has "properties" key) and Archon's
        # flat {field: {type, description, required}} shorthand.
        if "properties" in explicit_input or "type" in explicit_input:
            # Already a proper JSON Schema object — use as-is.
            input_schema: dict[str, Any] = explicit_input
        else:
            # Archon flat shorthand: {field: {type, description, required?}}
            properties: dict[str, Any] = {}
            required_fields: list[str] = []
            for field_name, spec in explicit_input.items():
                if not isinstance(spec, dict):
                    continue
                prop: dict[str, Any] = {}
                if "type" in spec:
                    prop["type"] = spec["type"]
                if "description" in spec:
                    prop["description"] = spec["description"]
                if "enum" in spec:
                    prop["enum"] = spec["enum"]
                properties[field_name] = prop
                if spec.get("required", False):
                    required_fields.append(field_name)
            input_schema = {
                "type": "object",
                "properties": properties,
            }
            if required_fields:
                input_schema["required"] = required_fields
    else:
        # No explicit input-schema — synthesise from trigger metadata.
        # Every Archon skill is invokable with a natural-language prompt.
        triggers = skill_manifest.get("triggers", {}) or {}
        keywords: list[str] = triggers.get("keywords", [])
        prompt_desc = "The natural-language request for this skill."
        if keywords:
            examples = ", ".join(f'"{kw}"' for kw in keywords[:4])
            prompt_desc += f" Example triggers: {examples}."
        input_schema = {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": prompt_desc,
                },
            },
            "required": ["prompt"],
        }

    # Build optional annotations.
    # output-schema lives HERE (not in inputSchema — that would be the inversion).
    annotations: dict[str, Any] = {}
    output_schema = skill_manifest.get("output-schema")
    if output_schema:
        annotations["outputSchema"] = output_schema
    priority = skill_manifest.get("priority")
    if priority:
        annotations["archonPriority"] = priority
    tags = skill_manifest.get("tags")
    if tags:
        annotations["tags"] = tags

    tool: dict[str, Any] = {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
    }
    if annotations:
        tool["annotations"] = annotations
    return tool


def load_all_skill_manifests(root: Path) -> list[dict[str, Any]]:
    """Walk the skills directory and load all skill YAML manifests."""
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML is required to load skill manifests")

    manifests = []
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return manifests

    for manifest_path in skills_dir.rglob("manifest.yaml"):
        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "name" in data:
                manifests.append(data)
        except Exception:
            pass  # Skip malformed manifests

    return manifests


def write_mcp_tools_manifest(root: Path, registry: dict[str, Any] | None = None) -> Path:
    """Generate mcp-tools.json from all skill manifests.

    Args:
        root: Archon project root directory.
        registry: Optional pre-loaded registry dict. If None, manifests are
                  discovered from the skills/ directory.

    Returns:
        Path to the written mcp-tools.json file.
    """
    if registry is not None:
        skill_manifests = registry.get("skills", [])
    else:
        skill_manifests = load_all_skill_manifests(root)

    tools = [skill_to_mcp_tool(s) for s in skill_manifests if "name" in s]
    output = {"tools": tools}

    output_path = root / "mcp-tools.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
