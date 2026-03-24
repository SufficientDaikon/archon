"""Core generation logic for llms.txt and llms-full.txt.

Produces machine-readable Markdown indexes of the Archon framework
following the `llms.txt <https://llmstxt.org/>`_ convention.

Public API
----------
- :func:`generate_concise` — concise index (``llms.txt``)
- :func:`generate_full` — complete documentation dump (``llms-full.txt``)
- :func:`write_files` — generate and write files to disk
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from archon.core.registry import Registry


# ── Constants ───────────────────────────────────────────────────

_DOCS_URL = "https://sufficientdaikon.github.io/archon/"
_TRUNCATE_LEN = 200


# ── Public API ──────────────────────────────────────────────────

def generate_concise(root: Path, registry: Registry | None = None) -> str:
    """Generate the concise ``llms.txt`` content.

    Args:
        root: Path to the Archon repository root.
        registry: Pre-loaded Registry instance.  If *None*, one is created
            and loaded automatically.

    Returns:
        The complete ``llms.txt`` content as a string.
    """
    reg = _ensure_registry(root, registry)
    parts: list[str] = []

    # Header
    parts.append(_get_header(reg.name, reg.version, reg._raw.get("description", ""), reg._raw.get("repository", "")))

    # Skills
    parts.append("## Skills\n")
    for skill in sorted(reg.skills, key=lambda s: s.name):
        desc = _get_skill_description(root, skill)
        parts.append(f"- [{skill.name}]({skill.path}/SKILL.md): {desc}\n")
    parts.append("\n")

    # Agents
    parts.append("## Agents\n")
    for agent in sorted(reg.agents, key=lambda a: a.name):
        role, desc = _get_agent_summary(root, agent)
        if role and desc:
            parts.append(f"- [{agent.name}]({agent.path}/AGENT.md): {role} — {desc}\n")
        elif role:
            parts.append(f"- [{agent.name}]({agent.path}/AGENT.md): {role}\n")
        elif desc:
            parts.append(f"- [{agent.name}]({agent.path}/AGENT.md): {desc}\n")
        else:
            parts.append(f"- [{agent.name}]({agent.path}/AGENT.md): No description available\n")
    parts.append("\n")

    # Synapses
    parts.append("## Synapses\n")
    for syn in sorted(reg.synapses, key=lambda s: s.name):
        stype, desc = _get_synapse_summary(root, syn)
        if desc:
            parts.append(f"- [{syn.name}]({syn.path}/SYNAPSE.md): ({stype}) {desc}\n")
        else:
            parts.append(f"- [{syn.name}]({syn.path}/SYNAPSE.md): ({stype}) No description available\n")
    parts.append("\n")

    # Pipelines
    parts.append("## Pipelines\n")
    for pl in sorted(reg.pipelines, key=lambda p: p.name):
        trigger, _desc, chain = _get_pipeline_chain(root, pl)
        entry = f"- **{pl.name}**"
        if trigger:
            entry += f': "{trigger}"'
        if chain:
            entry += f" — {chain}"
        parts.append(entry + "\n")
    parts.append("\n")

    # Bundles
    parts.append("## Bundles\n")
    for bnd in sorted(reg.bundles, key=lambda b: b.name):
        desc, skills = _get_bundle_summary(root, bnd)
        entry = f"- **{bnd.name}**"
        if desc:
            entry += f": {desc}"
        if skills:
            entry += f" — skills: {', '.join(skills)}"
        parts.append(entry + "\n")
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
    repo_url = reg._raw.get("repository", "https://github.com/SufficientDaikon/archon")
    parts.append("## Links\n")
    parts.append(f"\n- Repository: {repo_url}\n")
    parts.append(f"- Documentation: {_DOCS_URL}\n")
    parts.append("- Full documentation dump: [llms-full.txt](llms-full.txt)\n")

    return "".join(parts)


def generate_full(root: Path, registry: Registry | None = None) -> str:
    """Generate the complete ``llms-full.txt`` content.

    Args:
        root: Path to the Archon repository root.
        registry: Pre-loaded Registry instance.  If *None*, one is created
            and loaded automatically.

    Returns:
        The complete ``llms-full.txt`` content as a string.
    """
    reg = _ensure_registry(root, registry)
    parts: list[str] = []
    description = reg._raw.get("description", "")

    # Header
    parts.append("# Archon — Full Documentation\n\n")
    parts.append(f"> {description}\n")
    parts.append("> This file contains the complete documentation for the Archon framework.\n")
    parts.append("> For a concise index, see [llms.txt](llms.txt).\n\n")
    parts.append(f"- Version: {reg.version}\n")
    parts.append(f"- Generated: {date.today().isoformat()}\n")

    # README
    readme_path = root / "README.md"
    content, _warn = _read_file_safe(readme_path)
    if content is not None:
        parts.append(_section_separator("README", "README.md"))
        parts.append(content)

    # Registry (archon.yaml)
    reg_path = root / "archon.yaml"
    content, _warn = _read_file_safe(reg_path)
    if content is not None:
        parts.append(_section_separator("Registry: archon.yaml", "archon.yaml"))
        parts.append(content)

    # Skills
    for skill in sorted(reg.skills, key=lambda s: s.name):
        skill_md = root / skill.path / "SKILL.md"
        content, _warn = _read_file_safe(skill_md)
        if content is not None:
            parts.append(_section_separator(f"Skill: {skill.name}", f"{skill.path}/SKILL.md"))
            parts.append(content if content.strip() else "(empty file)\n")

    # Agents
    for agent in sorted(reg.agents, key=lambda a: a.name):
        agent_md = root / agent.path / "AGENT.md"
        content, _warn = _read_file_safe(agent_md)
        if content is not None:
            parts.append(_section_separator(f"Agent: {agent.name}", f"{agent.path}/AGENT.md"))
            parts.append(content if content.strip() else "(empty file)\n")

    # Synapses
    for syn in sorted(reg.synapses, key=lambda s: s.name):
        syn_md = root / syn.path / "SYNAPSE.md"
        content, _warn = _read_file_safe(syn_md)
        if content is not None:
            parts.append(_section_separator(f"Synapse: {syn.name}", f"{syn.path}/SYNAPSE.md"))
            parts.append(content if content.strip() else "(empty file)\n")

    # Pipelines
    for pl in sorted(reg.pipelines, key=lambda p: p.name):
        pl_path = root / pl.path
        content, _warn = _read_file_safe(pl_path)
        if content is not None:
            parts.append(_section_separator(f"Pipeline: {pl.name}", pl.path))
            parts.append(content)

    # Bundles
    for bnd in sorted(reg.bundles, key=lambda b: b.name):
        bundle_yaml = root / bnd.path / "bundle.yaml"
        content, _warn = _read_file_safe(bundle_yaml)
        if content is not None:
            parts.append(_section_separator(f"Bundle: {bnd.name}", f"{bnd.path}/bundle.yaml"))
            parts.append(content)

    # Documentation
    docs_dir = root / "docs"
    if docs_dir.exists():
        md_files = sorted(f for f in docs_dir.iterdir() if f.suffix == ".md" and f.name != "README.md")
        for md_file in md_files:
            content, _warn = _read_file_safe(md_file)
            if content is not None:
                display = _docs_display_name(md_file.name)
                parts.append(_section_separator(f"Docs: {display}", f"docs/{md_file.name}"))
                parts.append(content)

    return "".join(parts)


def write_files(
    root: Path,
    output_dir: Path | None = None,
    concise: bool = True,
    full: bool = True,
    registry: Registry | None = None,
) -> dict[str, Any]:
    """Generate and write llms.txt file(s).

    Args:
        root: Archon repository root.
        output_dir: Directory to write files to.  Defaults to *root*.
        concise: Whether to generate ``llms.txt``.
        full: Whether to generate ``llms-full.txt``.
        registry: Pre-loaded Registry instance.

    Returns:
        A dict with keys ``concise``, ``full``, ``stats``, ``warnings``.
    """
    out = output_dir or root
    out.mkdir(parents=True, exist_ok=True)

    reg = _ensure_registry(root, registry)

    # Count docs pages
    docs_dir = root / "docs"
    docs_count = 0
    if docs_dir.exists():
        docs_count = len([f for f in docs_dir.iterdir() if f.suffix == ".md" and f.name != "README.md"])

    stats = {
        "skills": len(reg.skills),
        "agents": len(reg.agents),
        "synapses": len(reg.synapses),
        "pipelines": len(reg.pipelines),
        "bundles": len(reg.bundles),
        "docs_pages": docs_count,
    }

    result: dict[str, Any] = {"concise": None, "full": None, "stats": stats, "warnings": []}

    if concise:
        content = generate_concise(root, reg)
        p = out / "llms.txt"
        p.write_text(content, encoding="utf-8", newline="\n")
        result["concise"] = {"path": p, "size": p.stat().st_size}

    if full:
        content = generate_full(root, reg)
        p = out / "llms-full.txt"
        p.write_text(content, encoding="utf-8", newline="\n")
        result["full"] = {"path": p, "size": p.stat().st_size}

    return result


# ── Private helpers ─────────────────────────────────────────────

def _ensure_registry(root: Path, registry: Registry | None) -> Registry:
    """Return *registry* if provided, else create and load one."""
    if registry is not None:
        registry.ensure_loaded()
        return registry
    reg = Registry(root=root)
    reg.load()
    return reg


def _get_header(name: str, version: str, description: str, repository: str) -> str:
    """Build the header block for ``llms.txt``."""
    lines = [
        f"# {name.upper()}\n\n",
        f"> {description}\n\n" if description else "\n",
        f"- Version: {version}\n",
        f"- Repository: {repository}\n" if repository else "",
        f"- Documentation: {_DOCS_URL}\n",
        "- License: MIT\n\n",
    ]
    return "".join(lines)


def _extract_first_paragraph(md_content: str) -> str:
    """Extract the first non-heading, non-blockquote, non-empty paragraph.

    Follows the algorithm from the spec (§5 "First Content Paragraph"):
    1. Split into lines.
    2. Skip empty, heading (``#``), and blockquote (``>``) lines.
    3. Take the first remaining non-empty line.
    4. Strip whitespace; truncate at 200 chars with ``...`` suffix.
    """
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


def _get_skill_description(root: Path, skill: Any) -> str:
    """Extract description for a skill (manifest → SKILL.md → fallback)."""
    # Priority 1: manifest.yaml description
    manifest_path = root / skill.path / "manifest.yaml"
    desc = _yaml_field(manifest_path, "description")
    if desc:
        return desc

    # Priority 2: first paragraph from SKILL.md
    skill_md = root / skill.path / "SKILL.md"
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            para = _extract_first_paragraph(content)
            if para:
                return para
        except OSError:
            pass

    # Priority 3: fallback
    return "No description available"


def _get_agent_summary(root: Path, agent: Any) -> tuple[str, str]:
    """Extract (role, description) for an agent."""
    manifest_path = root / agent.path / "agent-manifest.yaml"
    role = _yaml_field(manifest_path, "role") or ""
    desc = _yaml_field(manifest_path, "description") or ""

    if role or desc:
        return role, desc

    # Fallback: first paragraph from AGENT.md
    agent_md = root / agent.path / "AGENT.md"
    if agent_md.exists():
        try:
            content = agent_md.read_text(encoding="utf-8", errors="replace")
            para = _extract_first_paragraph(content)
            if para:
                return "", para
        except OSError:
            pass

    return "", ""


def _get_synapse_summary(root: Path, synapse: Any) -> tuple[str, str]:
    """Extract (synapse_type, description) for a synapse."""
    manifest_path = root / synapse.path / "manifest.yaml"
    stype = _yaml_field(manifest_path, "synapse-type") or synapse.synapse_type or "core"
    desc = _yaml_field(manifest_path, "description") or ""

    if not desc:
        syn_md = root / synapse.path / "SYNAPSE.md"
        if syn_md.exists():
            try:
                content = syn_md.read_text(encoding="utf-8", errors="replace")
                para = _extract_first_paragraph(content)
                if para:
                    desc = para
            except OSError:
                pass

    return stype, desc


def _get_pipeline_chain(root: Path, pipeline: Any) -> tuple[str, str, str]:
    """Extract (trigger, description, chain_str) from a pipeline YAML file.

    *chain_str* format: ``step-name(agent) → step-name(agent) → ...``
    """
    trigger = pipeline.trigger or ""
    pl_path = root / pipeline.path
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
        except (OSError, yaml.YAMLError):
            pass

    return trigger, desc, chain


def _get_bundle_summary(root: Path, bundle: Any) -> tuple[str, list[str]]:
    """Extract (description, skills_list) from ``bundle.yaml``."""
    bundle_yaml = root / bundle.path / "bundle.yaml"
    desc = ""
    skills: list[str] = list(bundle.skills) if bundle.skills else []

    if bundle_yaml.exists():
        try:
            with open(bundle_yaml, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            desc = data.get("description", "")
            if data.get("skills"):
                skills = data["skills"]
        except (OSError, yaml.YAMLError):
            pass

    return desc, skills


def _yaml_field(path: Path, field: str) -> str:
    """Read a single field from a YAML file.  Returns ``""`` on any error."""
    if not path.exists():
        return ""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        value = data.get(field, "")
        return str(value) if value else ""
    except (OSError, yaml.YAMLError):
        return ""


def _section_separator(title: str, source_path: str) -> str:
    """Build the section separator for ``llms-full.txt``."""
    return f"\n---\n\n## {title}\n\n> Source: {source_path}\n\n"


def _read_file_safe(path: Path) -> tuple[str | None, str | None]:
    """Read a file safely.  Returns ``(content, warning)``."""
    if not path.exists():
        return None, f"File not found: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return content, None
    except OSError as exc:
        return None, f"Error reading {path}: {exc}"


def _docs_display_name(filename: str) -> str:
    """Convert ``'creating-skills.md'`` → ``'Creating Skills'``."""
    stem = filename.rsplit(".", 1)[0]
    return stem.replace("-", " ").title()
