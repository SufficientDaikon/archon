"""Virtuoso Engine — build and install the cognitive kernel.

Reads virtuoso.xml, wraps it in SKILL.md for Claude Code auto-loading,
installs all synapses, and generates/updates CLAUDE.md.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from archon.utils.output import print_success, print_error, print_info, print_verbose
from archon.utils.paths import get_archon_root


VIRTUOSO_DIR = "virtuoso"
VIRTUOSO_XML = "virtuoso.xml"
SKILL_MD_HEADER = """\
---
description: "Virtuoso Engine — Archon's cognitive kernel. Enforces reasoning quality through 5 synapses, the Virtuoso execution loop, and model-aware scaffolding."
---

<!-- VIRTUOSO ENGINE — This is your operating system. Internalize it. -->

"""

CLAUDE_MD_MARKER = "<!-- Virtuoso Engine active"
CLAUDE_MD_BLOCK = """\
<!-- Virtuoso Engine active. Cognitive kernel loaded via skills/virtuoso/SKILL.md -->
<!-- Do not remove this line — it signals Virtuoso is installed. -->
"""


def get_virtuoso_xml_path(archon_root: Optional[Path] = None) -> Path:
    """Return the path to virtuoso.xml in the Archon repo."""
    root = archon_root or get_archon_root()
    return root / VIRTUOSO_DIR / VIRTUOSO_XML


def build_virtuoso_skill(archon_root: Optional[Path] = None) -> str:
    """Read virtuoso.xml and wrap it in SKILL.md format.

    Returns the full SKILL.md content string.
    """
    xml_path = get_virtuoso_xml_path(archon_root)
    if not xml_path.exists():
        raise FileNotFoundError(f"Virtuoso engine not found at {xml_path}")

    xml_content = xml_path.read_text(encoding="utf-8")
    return SKILL_MD_HEADER + xml_content


def install_virtuoso_skill(archon_root: Path, skills_target: Path) -> bool:
    """Install the Virtuoso SKILL.md to a platform's skills directory.

    Creates ~/.claude/skills/virtuoso/SKILL.md (or equivalent) containing
    the full virtuoso.xml wrapped in SKILL.md frontmatter.

    Returns True on success.
    """
    try:
        skill_content = build_virtuoso_skill(archon_root)
    except FileNotFoundError as exc:
        print_error(str(exc))
        return False

    target_dir = skills_target / "virtuoso"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "SKILL.md"

    try:
        target_file.write_text(skill_content, encoding="utf-8")
        return True
    except Exception as exc:
        print_error(f"Failed to write Virtuoso SKILL.md: {exc}")
        return False


def install_all_synapses(archon_root: Path, skills_target: Path) -> int:
    """Install all 5 synapses to the platform's _synapses directory.

    Copies SYNAPSE.md + resources/ for each synapse from the Archon repo.

    Returns the count of successfully installed synapses.
    """
    synapses_src = archon_root / "synapses"
    if not synapses_src.exists():
        print_error(f"Synapses directory not found at {synapses_src}")
        return 0

    target_base = skills_target / "_synapses"
    target_base.mkdir(parents=True, exist_ok=True)
    installed = 0

    for synapse_dir in sorted(synapses_src.iterdir()):
        if not synapse_dir.is_dir() or synapse_dir.name.startswith("_"):
            continue

        synapse_md = synapse_dir / "SYNAPSE.md"
        if not synapse_md.exists():
            continue

        dst = target_base / synapse_dir.name
        dst.mkdir(parents=True, exist_ok=True)

        # Copy SYNAPSE.md
        shutil.copy2(synapse_md, dst / "SYNAPSE.md")

        # Copy resources/ if exists
        resources_src = synapse_dir / "resources"
        if resources_src.exists() and resources_src.is_dir():
            resources_dst = dst / "resources"
            if resources_dst.exists():
                shutil.rmtree(resources_dst)
            shutil.copytree(resources_src, resources_dst)

        # Copy manifest.yaml if exists
        manifest_src = synapse_dir / "manifest.yaml"
        if manifest_src.exists():
            shutil.copy2(manifest_src, dst / "manifest.yaml")

        installed += 1
        print_verbose(f"  Installed synapse: {synapse_dir.name}")

    # Update _synapses-index.md
    _rebuild_synapse_index(target_base)

    return installed


def _rebuild_synapse_index(synapses_dir: Path) -> None:
    """Rebuild the _synapses-index.md from installed synapse directories."""
    entries = []
    for d in sorted(synapses_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        synapse_md = d / "SYNAPSE.md"
        if not synapse_md.exists():
            continue
        # Extract name and type from SYNAPSE.md
        name = d.name
        synapse_type = "core"
        content = synapse_md.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("**Type:**"):
                synapse_type = line.split("**Type:**")[1].strip().split("(")[0].strip().lower()
                break
        entries.append(f"- **{name}** ({synapse_type}) — installed")

    index_content = (
        "# Installed Synapses Index\n\n"
        "> Core synapses are enforced through the Virtuoso Engine (skills/virtuoso/SKILL.md).\n"
        "> These reference files provide the full specification for each synapse.\n\n"
        + "\n".join(entries) + "\n"
    )
    (synapses_dir / "_synapses-index.md").write_text(index_content, encoding="utf-8")


def update_claude_md(claude_dir: Path) -> bool:
    """Add or update the Virtuoso marker in CLAUDE.md.

    If CLAUDE.md exists and already has the marker, does nothing.
    If CLAUDE.md exists without the marker, appends it.
    If CLAUDE.md doesn't exist, creates a minimal one.

    Returns True on success.
    """
    claude_md = claude_dir / "CLAUDE.md"

    try:
        if claude_md.exists():
            content = claude_md.read_text(encoding="utf-8")
            if CLAUDE_MD_MARKER in content:
                return True  # already present
            # Append the marker
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + CLAUDE_MD_BLOCK
            claude_md.write_text(content, encoding="utf-8")
        else:
            claude_md.write_text(CLAUDE_MD_BLOCK, encoding="utf-8")
        return True
    except Exception as exc:
        print_error(f"Failed to update CLAUDE.md: {exc}")
        return False


def install_virtuoso(archon_root: Path, skills_target: Path, claude_dir: Path) -> bool:
    """Full Virtuoso installation: engine + synapses + CLAUDE.md update.

    Args:
        archon_root: Path to the Archon repository (contains virtuoso/ and synapses/)
        skills_target: Platform skills directory (e.g., ~/.claude/skills/)
        claude_dir: Directory containing CLAUDE.md (e.g., ~/.claude/)

    Returns True if all steps succeed.
    """
    # 1. Install the Virtuoso SKILL.md
    if not install_virtuoso_skill(archon_root, skills_target):
        print_error("Failed to install Virtuoso engine.")
        return False
    print_success("Installed Virtuoso engine → skills/virtuoso/SKILL.md")

    # 2. Install all synapses
    count = install_all_synapses(archon_root, skills_target)
    if count > 0:
        print_success(f"Installed {count} synapse(s) → skills/_synapses/")
    else:
        print_error("No synapses installed.")
        return False

    # 3. Update CLAUDE.md
    if update_claude_md(claude_dir):
        print_info("CLAUDE.md updated with Virtuoso marker.")
    else:
        print_error("Failed to update CLAUDE.md.")
        return False

    return True
