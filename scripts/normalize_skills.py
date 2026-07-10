#!/usr/bin/env python3
"""One-off, idempotent normalization of skill SKILL.md + manifest.yaml pairs.

Canonical format after this script runs:
- Every SKILL.md starts with YAML frontmatter containing at least
  ``name`` and ``description`` (other keys are preserved as-is).
- SKILL.md frontmatter never carries ``version`` — manifest.yaml is the
  single owner of version, so the two can't drift.
- manifest.yaml never carries a placeholder description ("Skill: <name>");
  when the SKILL.md frontmatter has a real description it is copied over
  (clamped to the schema's 200-char limit at a sentence boundary).

Usage: python3 scripts/normalize_skills.py [--check]
  --check  report what would change and exit 1 if anything would; write nothing
"""

import re
import sys
from pathlib import Path

import yaml

ARCHON_ROOT = Path(__file__).parent.parent
SKILLS_DIR = ARCHON_ROOT / "skills"

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.S)
_PLACEHOLDER = re.compile(r"^Skill:\s")


def clamp_description(text: str, limit: int = 200) -> str:
    """Clamp to the schema limit, preferring a sentence boundary."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for boundary in (". ", "; ", ", "):
        idx = cut.rfind(boundary)
        if idx > limit // 2:
            return cut[: idx + 1].strip()
    return cut[: limit - 1].rstrip() + "…"


def parse_frontmatter(text: str):
    """Return (frontmatter dict or None, body)."""
    match = _FRONTMATTER.match(text)
    if not match:
        return None, text
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None, text
    if not isinstance(data, dict):
        return None, text
    return data, text[match.end() :]


def dump_frontmatter(data: dict) -> str:
    return (
        "---\n"
        + yaml.dump(
            data, sort_keys=False, allow_unicode=True, width=100000, default_flow_style=False
        )
        + "---\n"
    )


def normalize_skill(skill_dir: Path) -> list[str]:
    """Normalize one skill directory. Returns list of changes made."""
    changes: list[str] = []
    manifest_path = skill_dir / "manifest.yaml"
    skill_md_path = skill_dir / "SKILL.md"
    if not manifest_path.exists() or not skill_md_path.exists():
        return changes

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    skill_text = skill_md_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)

    # 1. Placeholder manifest description <- real SKILL.md description
    manifest_desc = str(manifest.get("description", ""))
    if _PLACEHOLDER.match(manifest_desc) and frontmatter and frontmatter.get("description"):
        manifest["description"] = clamp_description(str(frontmatter["description"]))
        manifest_path.write_text(
            yaml.dump(manifest, sort_keys=False, allow_unicode=True, width=100000),
            encoding="utf-8",
        )
        changes.append("manifest: replaced placeholder description")

    # 2. SKILL.md frontmatter: ensure present, strip version
    new_frontmatter = dict(frontmatter) if frontmatter else {}
    dirty = False
    if frontmatter is None:
        new_frontmatter = {
            "name": manifest.get("name", skill_dir.name),
            "description": clamp_description(str(manifest.get("description", ""))),
        }
        dirty = True
        changes.append("SKILL.md: added missing frontmatter")
    if "version" in new_frontmatter:
        del new_frontmatter["version"]
        dirty = True
        changes.append("SKILL.md: removed version (manifest owns it)")
    if "name" not in new_frontmatter:
        new_frontmatter = {"name": manifest.get("name", skill_dir.name), **new_frontmatter}
        dirty = True
        changes.append("SKILL.md: added missing name")

    if dirty:
        skill_md_path.write_text(dump_frontmatter(new_frontmatter) + body, encoding="utf-8")

    return changes


def main() -> int:
    check_only = "--check" in sys.argv
    total_changes = 0
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        if check_only:
            # Dry run: work on copies in memory is overkill here — reuse the
            # normalizer against a throwaway copy via changed-detection.
            import shutil
            import tempfile

            with tempfile.TemporaryDirectory() as tmp:
                tmp_skill = Path(tmp) / skill_dir.name
                shutil.copytree(skill_dir, tmp_skill)
                changes = normalize_skill(tmp_skill)
        else:
            changes = normalize_skill(skill_dir)
        if changes:
            total_changes += len(changes)
            print(f"{skill_dir.name}:")
            for change in changes:
                print(f"  - {change}")

    print(f"\n{total_changes} change(s){' would be made' if check_only else ''}")
    return 1 if (check_only and total_changes) else 0


if __name__ == "__main__":
    sys.exit(main())
