"""Skill migration — moves full SKILL.md content to skill-library/,
replaces originals with proxy stubs for Claude Code discovery.

Preserves manifest.yaml, handles symlinks, supports rollback.

Usage:
    python migrate.py                    # Run migration
    python migrate.py --rollback         # Restore originals from library
    python migrate.py --dry-run          # Preview what would happen
    python migrate.py --list-tiers       # Show tier classification
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────

SKILLS_DIR = Path.home() / ".claude" / "skills"
LIBRARY_DIR = Path.home() / ".claude" / "skill-library"

# Tier 1 — Always-on skills (keep full SKILL.md, never stub)
TIER1_SKILLS = frozenset({
    "virtuoso",
    "complexity-router",
    "context-curator",
})

# Directories to skip entirely
SKIP_DIRS = frozenset({
    "_synapses",
})

STUB_TEMPLATE = """---
name: {name}
description: {description}
---

<!-- PROXY STUB — Full content served by skill-router MCP -->

This skill's complete instructions are loaded on-demand via the skill-router MCP server.

**To use this skill**, call one of these MCP tools:

1. `get_skill(name="{name}")` — load this skill's full instructions
2. `find_skill(task="your task description")` — discover the best skill for your task

Read the returned content and follow its instructions to execute the skill.
"""


def _md5(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def _extract_frontmatter_fields(content: str) -> dict[str, str]:
    """Extract name and description from YAML frontmatter."""
    import re
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                fields[key] = value
    return fields


def _escape_yaml(text: str) -> str:
    """Escape text for YAML value."""
    if any(c in text for c in ':"{}[]|>&*!#%@`'):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def discover_skills() -> list[tuple[str, Path]]:
    """Discover all skill directories with SKILL.md files."""
    results = []
    if not SKILLS_DIR.exists():
        return results

    for item in sorted(SKILLS_DIR.iterdir()):
        if item.name in SKIP_DIRS:
            continue

        # Handle symlinks — resolve to find SKILL.md
        if item.is_symlink():
            target = item.resolve()
            skill_md = target / "SKILL.md"
        elif item.is_dir():
            skill_md = item / "SKILL.md"
        else:
            continue

        if skill_md.exists():
            results.append((item.name, skill_md))

    return results


def classify_tier(name: str) -> int:
    """Classify a skill into tiers. Returns 1 or 2."""
    return 1 if name in TIER1_SKILLS else 2


def migrate(dry_run: bool = False) -> dict:
    """Run the migration."""
    stats = {
        "tier1_kept": [],
        "tier2_migrated": [],
        "errors": [],
        "bytes_before": 0,
        "bytes_after": 0,
    }

    if not dry_run:
        LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    skills = discover_skills()
    print(f"Discovered {len(skills)} skills with SKILL.md files\n")

    for name, skill_md_path in skills:
        tier = classify_tier(name)

        try:
            content = skill_md_path.read_text(encoding="utf-8")
        except Exception as e:
            stats["errors"].append(f"{name}: failed to read -- {e}")
            continue

        size = len(content.encode("utf-8"))
        stats["bytes_before"] += size

        if tier == 1:
            stats["tier1_kept"].append(name)
            stats["bytes_after"] += size
            print(f"  [TIER 1] {name} — KEEP ({size:,} bytes)")
            continue

        # Check if already a stub
        if "PROXY STUB" in content:
            print(f"  [SKIP]   {name} — already stubbed")
            # Count stub size
            stats["bytes_after"] += size
            stats["tier2_migrated"].append(name)
            continue

        # Extract frontmatter
        fm = _extract_frontmatter_fields(content)
        skill_name = fm.get("name", name)
        description = fm.get("description", "")

        # Build stub
        stub = STUB_TEMPLATE.format(
            name=skill_name,
            description=_escape_yaml(description) if description else skill_name,
        )
        stub_size = len(stub.encode("utf-8"))
        stats["bytes_after"] += stub_size

        library_dest = LIBRARY_DIR / f"{name}.md"
        checksum = _md5(content)

        if dry_run:
            print(f"  [MIGRATE] {name} -- {size:,} bytes -> stub ({stub_size} bytes), save {size - stub_size:,}")
        else:
            # Copy full content to library
            library_dest.write_text(content, encoding="utf-8")

            # Verify checksum
            verify = _md5(library_dest.read_text(encoding="utf-8"))
            if verify != checksum:
                stats["errors"].append(f"{name}: checksum mismatch after copy!")
                continue

            # Handle symlinked skill directories
            skill_dir = SKILLS_DIR / name
            if skill_dir.is_symlink():
                # Read manifest from symlink target before removing
                target = skill_dir.resolve()
                target_manifest = target / "manifest.yaml"
                manifest_content = None
                if target_manifest.exists():
                    manifest_content = target_manifest.read_text(encoding="utf-8")

                # Remove symlink and create real directory
                skill_dir.unlink()
                skill_dir.mkdir(parents=True, exist_ok=True)

                # Restore manifest if it existed
                if manifest_content:
                    (skill_dir / "manifest.yaml").write_text(manifest_content, encoding="utf-8")

            # Write stub
            stub_path = skill_dir / "SKILL.md"
            stub_path.write_text(stub, encoding="utf-8")
            print(f"  [MIGRATED] {name} -- {size:,} -> {stub_size} bytes (saved {size - stub_size:,})")

        stats["tier2_migrated"].append(name)

    # Summary
    saved = stats["bytes_before"] - stats["bytes_after"]
    print(f"\n{'DRY RUN ' if dry_run else ''}Summary:")
    print(f"  Tier 1 (kept full):   {len(stats['tier1_kept'])} skills")
    print(f"  Tier 2 (migrated):    {len(stats['tier2_migrated'])} skills")
    print(f"  Errors:               {len(stats['errors'])}")
    print(f"  Bytes before:         {stats['bytes_before']:,}")
    print(f"  Bytes after:          {stats['bytes_after']:,}")
    print(f"  Bytes saved:          {saved:,} ({saved / max(stats['bytes_before'], 1) * 100:.1f}%)")
    print(f"  Est. tokens saved:    ~{saved // 4:,}")

    if stats["errors"]:
        print(f"\nErrors:")
        for err in stats["errors"]:
            print(f"  - {err}")

    return stats


def rollback() -> None:
    """Restore original SKILL.md files from the library."""
    if not LIBRARY_DIR.exists():
        print("No skill-library found. Nothing to rollback.")
        return

    restored = 0
    for lib_file in sorted(LIBRARY_DIR.glob("*.md")):
        name = lib_file.stem
        skill_dir = SKILLS_DIR / name

        if not skill_dir.exists():
            skill_dir.mkdir(parents=True, exist_ok=True)

        target = skill_dir / "SKILL.md"
        content = lib_file.read_text(encoding="utf-8")
        target.write_text(content, encoding="utf-8")
        restored += 1
        print(f"  [RESTORED] {name}")

    print(f"\nRestored {restored} skills from library.")


def list_tiers() -> None:
    """Show tier classification for all skills."""
    skills = discover_skills()
    tier1 = []
    tier2 = []

    for name, path in skills:
        try:
            size = path.stat().st_size
        except Exception:
            size = 0

        if classify_tier(name) == 1:
            tier1.append((name, size))
        else:
            tier2.append((name, size))

    print("Tier 1 — Always-On (keep full):")
    for name, size in tier1:
        print(f"  {name} ({size:,} bytes)")

    print(f"\nTier 2 — On-Demand ({len(tier2)} skills):")
    for name, size in sorted(tier2, key=lambda x: -x[1]):
        print(f"  {name} ({size:,} bytes)")

    total_t2 = sum(s for _, s in tier2)
    print(f"\nTier 2 total: {total_t2:,} bytes (~{total_t2 // 4:,} tokens)")


if __name__ == "__main__":
    if "--rollback" in sys.argv:
        rollback()
    elif "--dry-run" in sys.argv:
        migrate(dry_run=True)
    elif "--list-tiers" in sys.argv:
        list_tiers()
    else:
        migrate(dry_run=False)
