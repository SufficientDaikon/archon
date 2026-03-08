#!/usr/bin/env python3
"""
OMNISKILL Doctor
Health checker that diagnoses platform installations and skill conflicts.

Usage:
    python doctor.py                    # Full health check
    python doctor.py --platforms        # List detected platforms only
    python doctor.py --conflicts        # Check for conflicts only
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


OMNISKILL_ROOT = Path(__file__).parent.parent


def detect_platforms() -> Dict[str, Dict]:
    """
    Detects which AI coding platforms are installed and their details.
    
    Returns:
        Dict mapping platform names to their details
    """
    platforms = {}
    home = Path.home()
    cwd = Path.cwd()
    
    # Check for Claude Code
    claude_dir = home / ".claude"
    if claude_dir.exists():
        skills_dir = claude_dir / "skills"
        installed_skills = []
        if skills_dir.exists():
            installed_skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        
        platforms["claude-code"] = {
            "path": claude_dir,
            "type": "global",
            "skills_count": len(installed_skills),
            "skills": installed_skills
        }
    
    # Check for Copilot CLI
    copilot_dir = home / ".copilot"
    if copilot_dir.exists():
        skills_dir = copilot_dir / "skills"
        installed_skills = []
        if skills_dir.exists():
            installed_skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        
        platforms["copilot-cli"] = {
            "path": copilot_dir,
            "type": "global",
            "skills_count": len(installed_skills),
            "skills": installed_skills
        }
    
    # Check for Cursor
    cursor_dir = cwd / ".cursor"
    cursor_rules = cwd / ".cursorrules"
    if cursor_dir.exists() or cursor_rules.exists():
        rules_dir = cursor_dir / "rules"
        installed_skills = []
        if rules_dir.exists():
            installed_skills = [f.stem for f in rules_dir.glob("*.mdc")]
        
        platforms["cursor"] = {
            "path": cursor_dir if cursor_dir.exists() else cursor_rules,
            "type": "project",
            "skills_count": len(installed_skills),
            "skills": installed_skills
        }
    
    # Check for Windsurf
    windsurf_rules = cwd / ".windsurfrules"
    if windsurf_rules.exists():
        # Parse the file to count skills
        installed_skills = []
        try:
            with open(windsurf_rules, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count skill sections
            import re
            skill_matches = re.findall(r'^# SKILL: (.+)$', content, re.MULTILINE)
            installed_skills = skill_matches
        except Exception:
            pass
        
        platforms["windsurf"] = {
            "path": windsurf_rules,
            "type": "project",
            "skills_count": len(installed_skills),
            "skills": installed_skills
        }
    
    # Check for Antigravity
    antigravity_dir = cwd / ".antigravity"
    if antigravity_dir.exists():
        skills_dir = antigravity_dir / "skills"
        installed_skills = []
        if skills_dir.exists():
            installed_skills = [f.stem for f in skills_dir.glob("*.md")]
        
        platforms["antigravity"] = {
            "path": antigravity_dir,
            "type": "project",
            "skills_count": len(installed_skills),
            "skills": installed_skills
        }
    
    return platforms


def get_all_available_skills() -> List[str]:
    """
    Gets list of all available skills in the OMNISKILL repository.
    
    Returns:
        List of skill names
    """
    skills_dir = OMNISKILL_ROOT / "skills"
    
    if not skills_dir.exists():
        return []
    
    return [d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]


def check_trigger_conflicts() -> List[Tuple[str, List[str]]]:
    """
    Checks for duplicate triggers across all skills.
    
    Returns:
        List of (trigger, [skill_names]) tuples for conflicts
    """
    conflicts = []
    trigger_map: Dict[str, List[str]] = {}
    
    skills_dir = OMNISKILL_ROOT / "skills"
    if not skills_dir.exists():
        return conflicts
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        manifest_path = skill_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            triggers = manifest.get('triggers', {})
            keywords = triggers.get('keywords', [])
            
            for keyword in keywords:
                if keyword not in trigger_map:
                    trigger_map[keyword] = []
                trigger_map[keyword].append(manifest['name'])
        
        except Exception:
            continue
    
    # Find conflicts
    for trigger, skills in trigger_map.items():
        if len(skills) > 1:
            conflicts.append((trigger, skills))
    
    return conflicts


def check_broken_references() -> List[str]:
    """
    Checks for broken references in bundles (skills that don't exist).
    
    Returns:
        List of error messages
    """
    errors = []
    bundles_dir = OMNISKILL_ROOT / "bundles"
    
    if not bundles_dir.exists():
        return errors
    
    available_skills = set(get_all_available_skills())
    
    for bundle_dir in bundles_dir.iterdir():
        if not bundle_dir.is_dir():
            continue
        
        manifest_path = bundle_dir / "bundle.yaml"
        if not manifest_path.exists():
            continue
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            bundle_name = manifest.get('name', bundle_dir.name)
            skills = manifest.get('skills', [])
            
            for skill in skills:
                if skill not in available_skills:
                    errors.append(f"Bundle '{bundle_name}' references non-existent skill '{skill}'")
        
        except Exception as e:
            errors.append(f"Failed to parse {bundle_dir.name}/bundle.yaml: {e}")
    
    return errors


def calculate_health_score(platforms: Dict, conflicts: List, broken_refs: List) -> int:
    """
    Calculates overall health score (0-100).
    
    Args:
        platforms: Detected platforms dict
        conflicts: List of trigger conflicts
        broken_refs: List of broken references
        
    Returns:
        Health score (0-100)
    """
    score = 100
    
    # Deduct points for no platforms detected
    if not platforms:
        score -= 30
    
    # Deduct points for conflicts
    score -= min(len(conflicts) * 5, 30)
    
    # Deduct points for broken references
    score -= min(len(broken_refs) * 10, 40)
    
    return max(0, score)


def print_platforms_report(platforms: Dict):
    """
    Prints detected platforms report.
    
    Args:
        platforms: Detected platforms dict
    """
    print("\n" + "=" * 60)
    print("DETECTED PLATFORMS")
    print("=" * 60)
    
    if not platforms:
        print("⚠️  No platforms detected")
        print("\nSupported platforms:")
        print("  • claude-code  (~/.claude)")
        print("  • copilot-cli  (~/.copilot)")
        print("  • cursor       (.cursor/)")
        print("  • windsurf     (.windsurfrules)")
        print("  • antigravity  (.antigravity/)")
        return
    
    for platform_name, details in sorted(platforms.items()):
        print(f"\n✅ {platform_name}")
        print(f"   Path: {details['path']}")
        print(f"   Type: {details['type']}")
        print(f"   Skills: {details['skills_count']}")
        
        if details['skills']:
            print(f"   Installed:")
            for skill in sorted(details['skills'][:5]):  # Show first 5
                print(f"     • {skill}")
            if len(details['skills']) > 5:
                print(f"     ... and {len(details['skills']) - 5} more")


def print_conflicts_report(conflicts: List[Tuple[str, List[str]]]):
    """
    Prints trigger conflicts report.
    
    Args:
        conflicts: List of conflicts
    """
    print("\n" + "=" * 60)
    print("TRIGGER CONFLICTS")
    print("=" * 60)
    
    if not conflicts:
        print("✅ No conflicts detected")
        return
    
    print(f"⚠️  Found {len(conflicts)} conflict(s):\n")
    
    for trigger, skills in conflicts:
        print(f"• Trigger: '{trigger}'")
        print(f"  Used by: {', '.join(skills)}")


def print_broken_references_report(broken_refs: List[str]):
    """
    Prints broken references report.
    
    Args:
        broken_refs: List of broken reference errors
    """
    print("\n" + "=" * 60)
    print("BROKEN REFERENCES")
    print("=" * 60)
    
    if not broken_refs:
        print("✅ No broken references")
        return
    
    print(f"❌ Found {len(broken_refs)} broken reference(s):\n")
    
    for error in broken_refs:
        print(f"• {error}")


def print_health_summary(score: int, platforms: Dict, conflicts: List, broken_refs: List):
    """
    Prints overall health summary.
    
    Args:
        score: Health score
        platforms: Platforms dict
        conflicts: Conflicts list
        broken_refs: Broken references list
    """
    print("\n" + "=" * 60)
    print("HEALTH SUMMARY")
    print("=" * 60)
    
    # Determine status emoji
    if score >= 90:
        status = "🟢 EXCELLENT"
    elif score >= 70:
        status = "🟡 GOOD"
    elif score >= 50:
        status = "🟠 FAIR"
    else:
        status = "🔴 POOR"
    
    print(f"\n{status}")
    print(f"Health Score: {score}/100")
    
    print(f"\n📊 Statistics:")
    print(f"  • Platforms detected: {len(platforms)}")
    print(f"  • Trigger conflicts: {len(conflicts)}")
    print(f"  • Broken references: {len(broken_refs)}")
    
    # Available skills
    available_skills = get_all_available_skills()
    print(f"  • Available skills: {len(available_skills)}")
    
    # Recommendations
    issues = []
    
    if not platforms:
        issues.append("Install at least one supported platform")
    
    if conflicts:
        issues.append("Resolve trigger conflicts to avoid skill collisions")
    
    if broken_refs:
        issues.append("Fix broken references in bundle manifests")
    
    if issues:
        print(f"\n💡 Recommendations:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OMNISKILL health checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python doctor.py                    # Full health check
  python doctor.py --platforms        # List platforms only
  python doctor.py --conflicts        # Check conflicts only
        """
    )
    
    parser.add_argument('--platforms', action='store_true', help='List detected platforms only')
    parser.add_argument('--conflicts', action='store_true', help='Check for conflicts only')
    parser.add_argument('--references', action='store_true', help='Check for broken references only')
    
    args = parser.parse_args()
    
    print("🏥 OMNISKILL Health Check")
    print("=" * 60)
    
    # Detect platforms
    platforms = detect_platforms()
    
    if args.platforms:
        print_platforms_report(platforms)
        return 0
    
    # Check conflicts
    conflicts = check_trigger_conflicts()
    
    if args.conflicts:
        print_conflicts_report(conflicts)
        return 0 if not conflicts else 1
    
    # Check broken references
    broken_refs = check_broken_references()
    
    if args.references:
        print_broken_references_report(broken_refs)
        return 0 if not broken_refs else 1
    
    # Full health check
    print_platforms_report(platforms)
    print_conflicts_report(conflicts)
    print_broken_references_report(broken_refs)
    
    # Calculate and print health score
    health_score = calculate_health_score(platforms, conflicts, broken_refs)
    print_health_summary(health_score, platforms, conflicts, broken_refs)
    
    # Return exit code based on health
    if health_score < 50:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
