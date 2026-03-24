#!/usr/bin/env python3
"""
Archon Skill Compliance Checker

Validates every skill against the 9-section SKILL.md template and manifest.yaml requirements.
Outputs a compliance report with per-skill scores and framework-wide summary.

Usage:
    python scripts/skill-compliance-check.py [--json] [--threshold N] [--skill SKILL_NAME]
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Optional

# 9 required sections in SKILL.md
REQUIRED_SECTIONS = [
    "Identity",
    "When to Use",
    "Workflow",
    "Rules",
    "Output Format",
    "Resources",
    "Handoff",
    "Platform Notes",
]

# Sections that have quality sub-checks
SECTION_QUALITY_CHECKS = {
    "Identity": {
        "min_lines": 3,
        "must_contain_any": ["you are", "You are", "persona", "expert", "architect"],
        "description": "Must establish an AI persona with traits",
    },
    "When to Use": {
        "min_lines": 3,
        "must_contain_any": ["keyword", "Keyword", "Keywords", "Do NOT", "Do not use"],
        "description": "Must have keywords and anti-patterns",
    },
    "Workflow": {
        "must_contain_any": ["Step 1", "Step 2", "Step 3", "Phase 1", "Phase 2", "### Step", "### Phase"],
        "description": "Must have numbered steps or phases (min 3)",
    },
    "Rules": {
        "must_contain_any": ["DO:", "DON'T:", "Don't", "Do:"],
        "description": "Must have DO and DON'T sections",
    },
}

GRADE_THRESHOLDS = {
    9: ("A", "gold"),
    8: ("A-", "gold"),
    7: ("B", "silver"),
    6: ("B-", "silver"),
    5: ("C", "bronze"),
    4: ("C-", "bronze"),
    3: ("D", "stub"),
    2: ("D-", "stub"),
    1: ("F", "stub"),
    0: ("F", "stub"),
}

GRADE_ICONS = {
    "gold":   "[A]",
    "silver": "[B]",
    "bronze": "[C]",
    "stub":   "[F]",
}


def find_archon_root() -> Path:
    """Find the Archon root directory."""
    # Try relative to script location
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent
    if (root / "archon.yaml").exists():
        return root

    # Try common paths
    for candidate in [
        Path(r"C:\Users\tahaa\archon"),
        Path.home() / "archon",
    ]:
        if (candidate / "archon.yaml").exists():
            return candidate

    print("ERROR: Cannot find Archon root (archon.yaml not found)")
    sys.exit(1)


def get_skill_dirs(root: Path, skill_filter: Optional[str] = None) -> list[Path]:
    """Get all skill directories, excluding _template."""
    skills_dir = root / "skills"
    dirs = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.is_dir() and entry.name != "_template" and entry.name != "__pycache__":
            if skill_filter and entry.name != skill_filter:
                continue
            dirs.append(entry)
    return dirs


def parse_sections(content: str) -> dict[str, str]:
    """Parse SKILL.md into sections by ## headings."""
    sections = {}
    current_section = None
    current_content = []

    for line in content.split("\n"):
        # Match ## headings (not ### or #)
        heading_match = re.match(r"^##\s+(.+)$", line)
        if heading_match:
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = heading_match.group(1).strip()
            # Normalize: remove emoji prefixes
            current_section = re.sub(r"^[^\w\s]+\s*", "", current_section).strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def normalize_section_name(name: str) -> Optional[str]:
    """Map parsed section names to required section names."""
    name_lower = name.lower().strip()

    mappings = {
        "identity": "Identity",
        "when to use": "When to Use",
        "when to use this skill": "When to Use",
        "workflow": "Workflow",
        "rules": "Rules",
        "core rules": "Rules",
        "output format": "Output Format",
        "output": "Output Format",
        "resources": "Resources",
        "handoff": "Handoff",
        "platform notes": "Platform Notes",
        "platform support": "Platform Notes",
    }

    return mappings.get(name_lower)


def check_manifest(skill_dir: Path) -> dict:
    """Check manifest.yaml for required fields."""
    manifest_path = skill_dir / "manifest.yaml"
    result = {
        "exists": False,
        "has_triggers": False,
        "trigger_keywords_count": 0,
        "trigger_patterns_count": 0,
        "has_platforms": False,
        "has_tags": False,
        "issues": [],
    }

    if not manifest_path.exists():
        result["issues"].append("manifest.yaml missing")
        return result

    result["exists"] = True
    content = manifest_path.read_text(encoding="utf-8", errors="replace")

    # Check triggers
    if "triggers:" in content:
        # Count keywords
        kw_match = re.search(r"keywords:\s*\n((?:\s+-\s+.+\n)*)", content)
        if kw_match:
            keywords = [l.strip("- \n\"'") for l in kw_match.group(1).split("\n") if l.strip().startswith("-")]
            result["trigger_keywords_count"] = len(keywords)

        # Also check inline format: keywords: ["a", "b"]
        kw_inline = re.search(r"keywords:\s*\[(.+)\]", content)
        if kw_inline:
            items = [s.strip().strip("\"'") for s in kw_inline.group(1).split(",")]
            result["trigger_keywords_count"] = max(result["trigger_keywords_count"], len([i for i in items if i]))

        # Check patterns
        pat_match = re.search(r"patterns:\s*\n((?:\s+-\s+.+\n)*)", content)
        if pat_match:
            patterns = [l.strip("- \n\"'") for l in pat_match.group(1).split("\n") if l.strip().startswith("-")]
            result["trigger_patterns_count"] = len(patterns)

        pat_inline = re.search(r"patterns:\s*\[(.+)\]", content)
        if pat_inline:
            items = [s.strip().strip("\"'") for s in pat_inline.group(1).split(",")]
            result["trigger_patterns_count"] = max(result["trigger_patterns_count"], len([i for i in items if i]))

        result["has_triggers"] = result["trigger_keywords_count"] > 0 or result["trigger_patterns_count"] > 0

        # Check for empty triggers
        empty_kw = re.search(r"keywords:\s*\[\s*\]", content)
        empty_pat = re.search(r"patterns:\s*\[\s*\]", content)
        if empty_kw and empty_pat:
            result["has_triggers"] = False
    else:
        result["issues"].append("No triggers section")

    # Check platforms
    if "platforms:" in content:
        result["has_platforms"] = True

    # Check tags
    if "tags:" in content:
        result["has_tags"] = True

    if not result["has_triggers"]:
        result["issues"].append("Triggers empty or missing keywords")
    if result["trigger_keywords_count"] < 3:
        result["issues"].append(f"Only {result['trigger_keywords_count']} trigger keywords (need >=3)")

    return result


def check_skill(skill_dir: Path) -> dict:
    """Run full compliance check on a skill directory."""
    skill_name = skill_dir.name
    result = {
        "name": skill_name,
        "score": 0,
        "max_score": 9,
        "grade": "F",
        "tier": "stub",
        "sections_present": [],
        "sections_missing": [],
        "section_quality": {},
        "manifest": {},
        "has_resources": False,
        "issues": [],
    }

    # Check SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        result["issues"].append("SKILL.md missing!")
        result["sections_missing"] = list(REQUIRED_SECTIONS)
        result["manifest"] = check_manifest(skill_dir)
        return result

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    total_lines = len(content.split("\n"))

    # Parse sections
    raw_sections = parse_sections(content)

    # Map to required section names
    found_sections = {}
    for raw_name, section_content in raw_sections.items():
        normalized = normalize_section_name(raw_name)
        if normalized:
            found_sections[normalized] = section_content

    # Also check for sections embedded without ## heading (legacy format)
    content_lower = content.lower()
    for req_section in REQUIRED_SECTIONS:
        if req_section not in found_sections:
            # Heuristic: check if section name appears as heading-like text
            search_variants = [
                f"## {req_section.lower()}",
                f"### {req_section.lower()}",
            ]
            for variant in search_variants:
                if variant in content_lower:
                    found_sections[req_section] = "(detected via heuristic)"
                    break

    # Score sections
    score = 0
    for req_section in REQUIRED_SECTIONS:
        if req_section in found_sections:
            result["sections_present"].append(req_section)
            score += 1
        else:
            result["sections_missing"].append(req_section)

    # The 9th "section" is having a proper first-line tagline (> description)
    has_tagline = content.strip().startswith("#") and ">" in content[:500]
    if has_tagline:
        score = min(score + 1, 9)
        result["sections_present"].append("Tagline")
    else:
        if len(result["sections_present"]) >= 8:
            # Don't penalize if all 8 sections present but no tagline
            score = min(score, 9)
        result["sections_missing"].append("Tagline (> description)")

    # Cap at 9
    result["score"] = min(score, 9)

    # Quality checks on found sections
    for section_name, checks in SECTION_QUALITY_CHECKS.items():
        if section_name in found_sections:
            section_text = found_sections[section_name]
            quality = {"present": True, "issues": []}

            if "min_lines" in checks:
                line_count = len([l for l in section_text.split("\n") if l.strip()])
                if line_count < checks["min_lines"]:
                    quality["issues"].append(f"Only {line_count} lines (need >={checks['min_lines']})")

            if "must_contain_any" in checks:
                if not any(term in section_text for term in checks["must_contain_any"]):
                    quality["issues"].append(checks["description"])

            result["section_quality"][section_name] = quality

    # Grade
    grade_letter, tier = GRADE_THRESHOLDS.get(result["score"], ("F", "stub"))
    result["grade"] = grade_letter
    result["tier"] = tier

    # Check resources
    resources_dir = skill_dir / "resources"
    if resources_dir.exists() and any(resources_dir.iterdir()):
        result["has_resources"] = True

    # Check manifest
    result["manifest"] = check_manifest(skill_dir)

    # Compile issues
    if result["score"] < 7:
        result["issues"].append(f"Low compliance: {result['score']}/9")
    if not result["has_resources"]:
        result["issues"].append("No resources/ directory or empty")
    if not result["manifest"]["exists"]:
        result["issues"].append("Missing manifest.yaml")
    result["issues"].extend(result["manifest"].get("issues", []))

    return result


def print_report(results: list[dict], json_output: bool = False):
    """Print the compliance report."""
    if json_output:
        print(json.dumps(results, indent=2))
        return

    # Sort by score (worst first)
    results.sort(key=lambda r: (r["score"], r["name"]))

    print()
    print("Archon Skill Compliance Report")
    print("=" * 90)
    print(f"{'SKILL':<35} {'SCORE':>5}  {'GRADE':>5}  {'TIER':>6}  MISSING SECTIONS")
    print("-" * 90)

    for r in results:
        icon = GRADE_ICONS.get(r["tier"], "")
        missing = ", ".join(r["sections_missing"]) if r["sections_missing"] else "—"
        if len(missing) > 40:
            missing = missing[:37] + "..."
        print(f"{r['name']:<35} {r['score']}/{r['max_score']}    {icon} {r['grade']:<3}  {r['tier']:<6}  {missing}")

    print("-" * 90)

    # Summary
    total = len(results)
    gold = sum(1 for r in results if r["tier"] == "gold")
    silver = sum(1 for r in results if r["tier"] == "silver")
    bronze = sum(1 for r in results if r["tier"] == "bronze")
    stub = sum(1 for r in results if r["tier"] == "stub")

    triggers_ok = sum(1 for r in results if r["manifest"].get("has_triggers", False))
    manifest_ok = sum(1 for r in results if r["manifest"].get("exists", False))
    resources_ok = sum(1 for r in results if r["has_resources"])

    print(f"\nSUMMARY: {total} skills analyzed")
    print(f"  [A] Gold  (9/9):  {gold}")
    print(f"  [B] Silver (7-8): {silver}")
    print(f"  [C] Bronze (5-6): {bronze}")
    print(f"  [F] Stub  (<5):   {stub}")
    print(f"\n  Manifests present: {manifest_ok}/{total}")
    print(f"  Triggers populated: {triggers_ok}/{total}")
    print(f"  Resources present: {resources_ok}/{total}")

    # Quality warnings
    quality_issues = []
    for r in results:
        for section, quality in r.get("section_quality", {}).items():
            for issue in quality.get("issues", []):
                quality_issues.append(f"  {r['name']}: {section} — {issue}")

    if quality_issues:
        print(f"\nQUALITY WARNINGS ({len(quality_issues)}):")
        for issue in quality_issues[:20]:
            print(issue)
        if len(quality_issues) > 20:
            print(f"  ... and {len(quality_issues) - 20} more")

    print()


def main():
    parser = argparse.ArgumentParser(description="Archon Skill Compliance Checker")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--threshold", type=int, default=0, help="Exit code 1 if any skill below this score")
    parser.add_argument("--skill", type=str, default=None, help="Check a single skill by name")
    args = parser.parse_args()

    root = find_archon_root()
    skill_dirs = get_skill_dirs(root, args.skill)

    if not skill_dirs:
        if args.skill:
            print(f"ERROR: Skill '{args.skill}' not found")
        else:
            print("ERROR: No skills found")
        sys.exit(1)

    results = [check_skill(d) for d in skill_dirs]
    print_report(results, args.json)

    # Threshold check
    if args.threshold > 0:
        below = [r for r in results if r["score"] < args.threshold]
        if below:
            print(f"FAIL: {len(below)} skill(s) below threshold {args.threshold}/9:")
            for r in below:
                print(f"  {r['name']}: {r['score']}/9")
            sys.exit(1)
        else:
            print(f"PASS: All skills at or above threshold {args.threshold}/9")


if __name__ == "__main__":
    main()
