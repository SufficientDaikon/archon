#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt for the Archon framework.

Standalone script — works with only Python 3.10+ and PyYAML installed.
If the archon package is installed, uses its core module for generation.
Otherwise, uses a self-contained fallback implementation.

Usage:
    python scripts/generate-llms-txt.py                     # Generate both files
    python scripts/generate-llms-txt.py --concise           # Only llms.txt
    python scripts/generate-llms-txt.py --full              # Only llms-full.txt
    python scripts/generate-llms-txt.py --output ./dist/    # Custom output directory
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path

import yaml

ARCHON_ROOT = Path(__file__).resolve().parent.parent


# ── Fallback implementation (stdlib + pyyaml only) ──────────────

_DOCS_URL = "https://sufficientdaikon.github.io/archon/"
_TRUNCATE_LEN = 200


def _yaml_field(path: Path, field: str) -> str:
    """Read a single field from a YAML file."""
    if not path.exists():
        return ""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        value = data.get(field, "")
        return str(value) if value else ""
    except Exception:
        return ""


def _extract_first_paragraph(md_content: str) -> str:
    """Extract first non-heading, non-blockquote, non-empty paragraph."""
    for line in md_content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith(">"):
            continue
        if len(stripped) > _TRUNCATE_LEN:
            return stripped[: _TRUNCATE_LEN - 3] + "..."
        return stripped
    return ""


def _read_file_safe(path: Path) -> str | None:
    """Read file content or return None."""
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _docs_display_name(filename: str) -> str:
    """Convert 'creating-skills.md' -> 'Creating Skills'."""
    stem = filename.rsplit(".", 1)[0]
    return stem.replace("-", " ").title()


def _get_skill_description(root: Path, entry: dict) -> str:
    """Extract description for a skill."""
    skill_path = entry.get("path", f"skills/{entry['name']}")
    desc = _yaml_field(root / skill_path / "manifest.yaml", "description")
    if desc:
        return desc
    skill_md = root / skill_path / "SKILL.md"
    if skill_md.exists():
        content = _read_file_safe(skill_md)
        if content:
            para = _extract_first_paragraph(content)
            if para:
                return para
    return "No description available"


def _get_agent_summary(root: Path, entry: dict) -> tuple[str, str]:
    """Extract (role, description) for an agent."""
    agent_path = entry.get("path", f"agents/{entry['name']}")
    manifest_path = root / agent_path / "agent-manifest.yaml"
    role = _yaml_field(manifest_path, "role")
    desc = _yaml_field(manifest_path, "description")
    if role or desc:
        return role, desc
    agent_md = root / agent_path / "AGENT.md"
    if agent_md.exists():
        content = _read_file_safe(agent_md)
        if content:
            para = _extract_first_paragraph(content)
            if para:
                return "", para
    return "", ""


def _get_synapse_summary(root: Path, entry: dict) -> tuple[str, str]:
    """Extract (type, description) for a synapse."""
    syn_path = entry.get("path", f"synapses/{entry['name']}")
    stype = _yaml_field(root / syn_path / "manifest.yaml", "synapse-type") or entry.get("type", "core")
    desc = _yaml_field(root / syn_path / "manifest.yaml", "description")
    if not desc:
        syn_md = root / syn_path / "SYNAPSE.md"
        if syn_md.exists():
            content = _read_file_safe(syn_md)
            if content:
                para = _extract_first_paragraph(content)
                if para:
                    desc = para
    return stype, desc


def _get_pipeline_chain(root: Path, entry: dict) -> tuple[str, str, str]:
    """Extract (trigger, description, chain_str)."""
    trigger = entry.get("trigger", "")
    pl_path = root / entry.get("path", "")
    desc = ""
    chain = ""
    if pl_path.exists():
        try:
            with open(pl_path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            desc = data.get("description", "")
            steps = data.get("steps", [])
            if steps:
                parts = []
                for step in steps:
                    step_name = step.get("name", "?")
                    agent = step.get("agent", "?")
                    parts.append(f"{step_name}({agent})")
                chain = " → ".join(parts)
        except Exception:
            pass
    return trigger, desc, chain


def _get_bundle_summary(root: Path, entry: dict) -> tuple[str, list[str]]:
    """Extract (description, skills_list)."""
    bnd_path = entry.get("path", f"bundles/{entry['name']}")
    bundle_yaml = root / bnd_path / "bundle.yaml"
    desc = ""
    skills: list[str] = entry.get("skills", [])
    if bundle_yaml.exists():
        try:
            with open(bundle_yaml, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            desc = data.get("description", "")
            if data.get("skills"):
                skills = data["skills"]
        except Exception:
            pass
    return desc, skills


def _section_separator(title: str, source_path: str) -> str:
    """Build section separator for llms-full.txt."""
    return f"\n---\n\n## {title}\n\n> Source: {source_path}\n\n"


def _fallback_generate_concise(root: Path, registry: dict) -> str:
    """Generate concise llms.txt using raw YAML data."""
    name = registry.get("name", "archon").upper()
    version = registry.get("version", "0.0.0")
    description = registry.get("description", "")
    repository = registry.get("repository", "")

    parts: list[str] = []

    # Header
    parts.append(f"# {name}\n\n")
    if description:
        parts.append(f"> {description}\n\n")
    parts.append(f"- Version: {version}\n")
    if repository:
        parts.append(f"- Repository: {repository}\n")
    parts.append(f"- Documentation: {_DOCS_URL}\n")
    parts.append("- License: MIT\n\n")

    # Skills
    parts.append("## Skills\n")
    for entry in sorted(registry.get("skills", []), key=lambda e: e["name"]):
        desc = _get_skill_description(root, entry)
        path = entry.get("path", f"skills/{entry['name']}")
        parts.append(f"- [{entry['name']}]({path}/SKILL.md): {desc}\n")
    parts.append("\n")

    # Agents
    parts.append("## Agents\n")
    for entry in sorted(registry.get("agents", []), key=lambda e: e["name"]):
        role, desc = _get_agent_summary(root, entry)
        path = entry.get("path", f"agents/{entry['name']}")
        if role and desc:
            parts.append(f"- [{entry['name']}]({path}/AGENT.md): {role} — {desc}\n")
        elif role:
            parts.append(f"- [{entry['name']}]({path}/AGENT.md): {role}\n")
        elif desc:
            parts.append(f"- [{entry['name']}]({path}/AGENT.md): {desc}\n")
        else:
            parts.append(f"- [{entry['name']}]({path}/AGENT.md): No description available\n")
    parts.append("\n")

    # Synapses
    parts.append("## Synapses\n")
    for entry in sorted(registry.get("synapses", []), key=lambda e: e["name"]):
        stype, desc = _get_synapse_summary(root, entry)
        path = entry.get("path", f"synapses/{entry['name']}")
        if desc:
            parts.append(f"- [{entry['name']}]({path}/SYNAPSE.md): ({stype}) {desc}\n")
        else:
            parts.append(f"- [{entry['name']}]({path}/SYNAPSE.md): ({stype}) No description available\n")
    parts.append("\n")

    # Pipelines
    parts.append("## Pipelines\n")
    for entry in sorted(registry.get("pipelines", []), key=lambda e: e["name"]):
        trigger, _desc, chain = _get_pipeline_chain(root, entry)
        line = f"- **{entry['name']}**"
        if trigger:
            line += f': "{trigger}"'
        if chain:
            line += f" — {chain}"
        parts.append(line + "\n")
    parts.append("\n")

    # Bundles
    parts.append("## Bundles\n")
    for entry in sorted(registry.get("bundles", []), key=lambda e: e["name"]):
        desc, skills = _get_bundle_summary(root, entry)
        line = f"- **{entry['name']}**"
        if desc:
            line += f": {desc}"
        if skills:
            line += f" — skills: {', '.join(skills)}"
        parts.append(line + "\n")
    parts.append("\n")

    # Documentation
    parts.append("## Documentation\n")
    docs_dir = root / "docs"
    if docs_dir.exists():
        md_files = sorted(f.name for f in docs_dir.iterdir() if f.suffix == ".md" and f.name != "README.md")
        for fname in md_files:
            display = _docs_display_name(fname)
            parts.append(f"- [{display}](docs/{fname})\n")
    parts.append("\n")

    # Installation
    parts.append("## Installation\n")
    parts.append("\nInstall via pip:\n")
    parts.append("\n```\npip install archon\narchon init\narchon install --all\n```\n")
    parts.append("\nOr clone and install manually:\n")
    parts.append("\n```\ngit clone https://github.com/SufficientDaikon/archon.git\ncd archon\npython scripts/install.py\n```\n")
    parts.append("\nSupported platforms: Claude Code, Copilot CLI, Cursor, Windsurf, Antigravity.\n\n")

    # Links
    repo_url = registry.get("repository", "https://github.com/SufficientDaikon/archon")
    parts.append("## Links\n")
    parts.append(f"\n- Repository: {repo_url}\n")
    parts.append(f"- Documentation: {_DOCS_URL}\n")
    parts.append("- Full documentation dump: [llms-full.txt](llms-full.txt)\n")

    return "".join(parts)


def _fallback_generate_full(root: Path, registry: dict) -> str:
    """Generate complete llms-full.txt using raw YAML data."""
    description = registry.get("description", "")
    version = registry.get("version", "0.0.0")
    parts: list[str] = []

    # Header
    parts.append("# Archon — Full Documentation\n\n")
    parts.append(f"> {description}\n")
    parts.append("> This file contains the complete documentation for the Archon framework.\n")
    parts.append("> For a concise index, see [llms.txt](llms.txt).\n\n")
    parts.append(f"- Version: {version}\n")
    parts.append(f"- Generated: {date.today().isoformat()}\n")

    # README
    content = _read_file_safe(root / "README.md")
    if content is not None:
        parts.append(_section_separator("README", "README.md"))
        parts.append(content)

    # Registry
    content = _read_file_safe(root / "archon.yaml")
    if content is not None:
        parts.append(_section_separator("Registry: archon.yaml", "archon.yaml"))
        parts.append(content)

    # Skills
    for entry in sorted(registry.get("skills", []), key=lambda e: e["name"]):
        path = entry.get("path", f"skills/{entry['name']}")
        skill_md = root / path / "SKILL.md"
        content = _read_file_safe(skill_md)
        if content is not None:
            parts.append(_section_separator(f"Skill: {entry['name']}", f"{path}/SKILL.md"))
            parts.append(content if content.strip() else "(empty file)\n")

    # Agents
    for entry in sorted(registry.get("agents", []), key=lambda e: e["name"]):
        path = entry.get("path", f"agents/{entry['name']}")
        agent_md = root / path / "AGENT.md"
        content = _read_file_safe(agent_md)
        if content is not None:
            parts.append(_section_separator(f"Agent: {entry['name']}", f"{path}/AGENT.md"))
            parts.append(content if content.strip() else "(empty file)\n")

    # Synapses
    for entry in sorted(registry.get("synapses", []), key=lambda e: e["name"]):
        path = entry.get("path", f"synapses/{entry['name']}")
        syn_md = root / path / "SYNAPSE.md"
        content = _read_file_safe(syn_md)
        if content is not None:
            parts.append(_section_separator(f"Synapse: {entry['name']}", f"{path}/SYNAPSE.md"))
            parts.append(content if content.strip() else "(empty file)\n")

    # Pipelines
    for entry in sorted(registry.get("pipelines", []), key=lambda e: e["name"]):
        pl_path = root / entry.get("path", "")
        content = _read_file_safe(pl_path)
        if content is not None:
            parts.append(_section_separator(f"Pipeline: {entry['name']}", entry.get("path", "")))
            parts.append(content)

    # Bundles
    for entry in sorted(registry.get("bundles", []), key=lambda e: e["name"]):
        path = entry.get("path", f"bundles/{entry['name']}")
        bundle_yaml = root / path / "bundle.yaml"
        content = _read_file_safe(bundle_yaml)
        if content is not None:
            parts.append(_section_separator(f"Bundle: {entry['name']}", f"{path}/bundle.yaml"))
            parts.append(content)

    # Documentation
    docs_dir = root / "docs"
    if docs_dir.exists():
        md_files = sorted(f for f in docs_dir.iterdir() if f.suffix == ".md" and f.name != "README.md")
        for md_file in md_files:
            content = _read_file_safe(md_file)
            if content is not None:
                display = _docs_display_name(md_file.name)
                parts.append(_section_separator(f"Docs: {display}", f"docs/{md_file.name}"))
                parts.append(content)

    return "".join(parts)


# ── Main ────────────────────────────────────────────────────────

def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Generate llms.txt for Archon")
    parser.add_argument("--output", type=str, default=None, help="Output directory (default: repo root)")
    parser.add_argument("--concise", action="store_true", help="Generate only llms.txt")
    parser.add_argument("--full", action="store_true", help="Generate only llms-full.txt")
    args = parser.parse_args()

    root = ARCHON_ROOT
    if not (root / "archon.yaml").exists():
        print(f"Error: archon.yaml not found at {root}. Run this script from the Archon repository root.", file=sys.stderr)
        return 1

    # Determine what to generate
    gen_concise = True
    gen_full = True
    if args.concise and not args.full:
        gen_full = False
    elif args.full and not args.concise:
        gen_concise = False

    output_dir = Path(args.output) if args.output else root
    if output_dir.exists() and output_dir.is_file():
        print(f"Error: Output path is a file, not a directory: {output_dir}", file=sys.stderr)
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()

    # Try the archon package first
    try:
        from archon.core.llms_txt import write_files as _write_files
        result = _write_files(root, output_dir=output_dir, concise=gen_concise, full=gen_full)
    except ImportError:
        # Fallback: self-contained implementation
        with open(root / "archon.yaml", "r", encoding="utf-8") as fh:
            registry = yaml.safe_load(fh) or {}

        result = {"concise": None, "full": None, "stats": {}, "warnings": []}

        skills = registry.get("skills", [])
        agents = registry.get("agents", [])
        synapses = registry.get("synapses", [])
        pipelines = registry.get("pipelines", [])
        bundles = registry.get("bundles", [])
        docs_dir = root / "docs"
        docs_count = 0
        if docs_dir.exists():
            docs_count = len([f for f in docs_dir.iterdir() if f.suffix == ".md" and f.name != "README.md"])

        result["stats"] = {
            "skills": len(skills),
            "agents": len(agents),
            "synapses": len(synapses),
            "pipelines": len(pipelines),
            "bundles": len(bundles),
            "docs_pages": docs_count,
        }

        if gen_concise:
            content = _fallback_generate_concise(root, registry)
            p = output_dir / "llms.txt"
            p.write_text(content, encoding="utf-8", newline="\n")
            result["concise"] = {"path": p, "size": p.stat().st_size}

        if gen_full:
            content = _fallback_generate_full(root, registry)
            p = output_dir / "llms-full.txt"
            p.write_text(content, encoding="utf-8", newline="\n")
            result["full"] = {"path": p, "size": p.stat().st_size}

    elapsed = time.time() - start

    # Print summary
    stats = result.get("stats", {})
    total_components = sum(stats.get(k, 0) for k in ("skills", "agents", "synapses", "pipelines", "bundles"))

    print("\n✅ llms.txt generation complete\n")
    print("Files generated:")
    if result.get("concise"):
        info = result["concise"]
        size_kb = info["size"] / 1024
        print(f"  📄 {info['path']}  ({size_kb:.1f} KB)")
    if result.get("full"):
        info = result["full"]
        size_kb = info["size"] / 1024
        print(f"  📄 {info['path']}  ({size_kb:.1f} KB)")

    print(f"\nComponents: {total_components} total", end="")
    if stats:
        print(f" ({stats.get('skills', 0)} skills, {stats.get('agents', 0)} agents, "
              f"{stats.get('synapses', 0)} synapses, {stats.get('pipelines', 0)} pipelines, "
              f"{stats.get('bundles', 0)} bundles)")
    else:
        print()

    print(f"Docs pages: {stats.get('docs_pages', 0)}")
    print(f"Time: {elapsed:.2f}s\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
