#!/usr/bin/env python3
"""
OMNISKILL Installer
Installs skills and bundles to detected or specified platforms.

Usage:
    python install.py --all                          # Install all skills to all detected platforms
    python install.py --platform copilot-cli --all   # Install all to specific platform
    python install.py --skill godot-best-practices   # Install specific skill
    python install.py --bundle godot-kit             # Install specific bundle
"""

import argparse
import sys
from pathlib import Path
from typing import List, Set

# Add adapters to path
OMNISKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(OMNISKILL_ROOT / "adapters"))

from base import BaseAdapter
import importlib.util


def detect_platforms() -> Set[str]:
    """
    Detects which AI coding platforms are installed on this system.
    
    Returns:
        Set of detected platform names
    """
    detected = set()
    home = Path.home()
    cwd = Path.cwd()
    
    # Check for Claude Code
    if (home / ".claude").exists():
        detected.add("claude-code")
    
    # Check for Copilot CLI
    if (home / ".copilot").exists():
        detected.add("copilot-cli")
    
    # Check for Cursor (project-specific)
    if (cwd / ".cursor").exists() or (cwd / ".cursorrules").exists():
        detected.add("cursor")
    
    # Check for Windsurf (project-specific)
    if (cwd / ".windsurfrules").exists():
        detected.add("windsurf")
    
    # Check for Antigravity (project-specific)
    if (cwd / ".antigravity").exists():
        detected.add("antigravity")
    
    return detected


def get_adapter(platform: str) -> BaseAdapter:
    """
    Dynamically loads and returns an adapter for the given platform.
    
    Args:
        platform: Platform name
        
    Returns:
        Adapter instance
    """
    adapter_path = OMNISKILL_ROOT / "adapters" / platform / "adapter.py"
    
    if not adapter_path.exists():
        raise ValueError(f"Adapter not found for platform: {platform}")
    
    # Load module dynamically
    spec = importlib.util.spec_from_file_location(
        f"{platform}_adapter",
        adapter_path
    )
    
    if not spec or not spec.loader:
        raise ValueError(f"Failed to load adapter for platform: {platform}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Get adapter class (assumes naming convention: PlatformAdapter)
    adapter_class_name = ''.join(word.capitalize() for word in platform.split('-')) + 'Adapter'
    adapter_class = getattr(module, adapter_class_name)
    
    return adapter_class()


def get_all_skills() -> List[Path]:
    """
    Returns list of all skill directories.
    
    Returns:
        List of skill paths
    """
    skills_dir = OMNISKILL_ROOT / "skills"
    
    if not skills_dir.exists():
        return []
    
    return [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]


def get_all_bundles() -> List[Path]:
    """
    Returns list of all bundle directories.
    
    Returns:
        List of bundle paths
    """
    bundles_dir = OMNISKILL_ROOT / "bundles"
    
    if not bundles_dir.exists():
        return []
    
    return [d for d in bundles_dir.iterdir() if d.is_dir() and (d / "bundle.yaml").exists()]


def install_skill(skill_name: str, platforms: Set[str]) -> dict:
    """
    Installs a single skill to specified platforms.
    
    Args:
        skill_name: Name of the skill
        platforms: Set of platform names
        
    Returns:
        Dict with results per platform
    """
    skill_path = OMNISKILL_ROOT / "skills" / skill_name
    
    if not skill_path.exists():
        print(f"❌ Skill not found: {skill_name}")
        return {}
    
    results = {}
    
    for platform in platforms:
        try:
            adapter = get_adapter(platform)
            success = adapter.install_skill(skill_path)
            results[platform] = success
        except Exception as e:
            print(f"❌ Failed to install to {platform}: {e}")
            results[platform] = False
    
    return results


def install_bundle(bundle_name: str, platforms: Set[str]) -> dict:
    """
    Installs a bundle to specified platforms.
    
    Args:
        bundle_name: Name of the bundle
        platforms: Set of platform names
        
    Returns:
        Dict with results per platform
    """
    bundle_path = OMNISKILL_ROOT / "bundles" / bundle_name
    
    if not bundle_path.exists():
        print(f"❌ Bundle not found: {bundle_name}")
        return {}
    
    results = {}
    
    for platform in platforms:
        try:
            adapter = get_adapter(platform)
            success_count, total_count = adapter.install_bundle(bundle_path)
            results[platform] = (success_count, total_count)
        except Exception as e:
            print(f"❌ Failed to install bundle to {platform}: {e}")
            results[platform] = (0, 0)
    
    return results


def install_all_skills(platforms: Set[str]) -> dict:
    """
    Installs all skills to specified platforms.
    
    Args:
        platforms: Set of platform names
        
    Returns:
        Dict with results per platform
    """
    skills = get_all_skills()
    
    if not skills:
        print("⚠️  No skills found")
        return {}
    
    print(f"\n📦 Installing {len(skills)} skills to {len(platforms)} platform(s)")
    print(f"   Platforms: {', '.join(sorted(platforms))}")
    print(f"   Skills: {', '.join([s.name for s in skills])}\n")
    
    results = {platform: {'success': 0, 'failed': 0} for platform in platforms}
    
    for skill_path in skills:
        for platform in platforms:
            try:
                adapter = get_adapter(platform)
                if adapter.install_skill(skill_path):
                    results[platform]['success'] += 1
                else:
                    results[platform]['failed'] += 1
            except Exception as e:
                print(f"❌ Error installing {skill_path.name} to {platform}: {e}")
                results[platform]['failed'] += 1
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install OMNISKILL skills and bundles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py --all                          # Install all to detected platforms
  python install.py --platform copilot-cli --all   # Install all to Copilot CLI
  python install.py --skill godot-best-practices   # Install specific skill
  python install.py --bundle godot-kit             # Install specific bundle
  python install.py --detect                       # Just detect platforms
        """
    )
    
    parser.add_argument('--platform', action='append', help='Target platform (can specify multiple)')
    parser.add_argument('--skill', help='Specific skill to install')
    parser.add_argument('--bundle', help='Specific bundle to install')
    parser.add_argument('--all', action='store_true', help='Install all skills')
    parser.add_argument('--detect', action='store_true', help='Detect and list installed platforms')
    
    args = parser.parse_args()
    
    # Detect platforms
    detected_platforms = detect_platforms()
    
    if args.detect:
        print("\n🔍 Detected platforms:")
        if detected_platforms:
            for platform in sorted(detected_platforms):
                print(f"   ✅ {platform}")
        else:
            print("   ⚠️  No platforms detected")
        return 0
    
    # Determine target platforms
    if args.platform:
        target_platforms = set(args.platform)
    else:
        target_platforms = detected_platforms
    
    if not target_platforms:
        print("❌ No platforms detected or specified. Use --platform to specify one.")
        return 1
    
    print(f"\n🎯 Target platforms: {', '.join(sorted(target_platforms))}\n")
    
    # Execute installation
    if args.skill:
        results = install_skill(args.skill, target_platforms)
        
        # Print summary
        print("\n" + "=" * 60)
        print("INSTALLATION SUMMARY")
        print("=" * 60)
        for platform, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {platform}")
        
    elif args.bundle:
        results = install_bundle(args.bundle, target_platforms)
        
        # Print summary
        print("\n" + "=" * 60)
        print("INSTALLATION SUMMARY")
        print("=" * 60)
        for platform, (success, total) in results.items():
            print(f"   {platform}: {success}/{total} skills")
        
    elif args.all:
        results = install_all_skills(target_platforms)
        
        # Print summary
        print("\n" + "=" * 60)
        print("INSTALLATION SUMMARY")
        print("=" * 60)
        for platform, counts in results.items():
            total = counts['success'] + counts['failed']
            print(f"   {platform}: {counts['success']}/{total} skills installed")
        
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
