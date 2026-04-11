#!/usr/bin/env python3
"""
Archon Update Manager
Manages skill and bundle updates from the repository.

Usage:
    python update.py --check                # Check for available updates
    python update.py --apply                # Apply all updates
    python update.py --apply godot-gdscript # Update specific skill
    python update.py --rollback godot-kit   # Rollback to previous version
"""

import argparse
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
from datetime import datetime


ARCHON_ROOT = Path(__file__).parent.parent


class VersionInfo:
    """Stores version information."""
    
    def __init__(self, path: Path, manifest: Dict):
        self.path = path
        self.name = manifest.get('name', path.name)
        self.version = manifest.get('version', '0.0.0')
        self.manifest = manifest
    
    def __lt__(self, other):
        """Compare versions for sorting."""
        return self._parse_version(self.version) < self._parse_version(other.version)
    
    @staticmethod
    def _parse_version(version_str: str) -> Tuple[int, int, int]:
        """Parse semantic version string."""
        try:
            parts = version_str.split('.')
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return (0, 0, 0)


def get_installed_skills(platform: str = "claude-code") -> Dict[str, VersionInfo]:
    """
    Gets installed skills for a platform.

    Args:
        platform: Platform name (only claude-code is supported)

    Returns:
        Dict mapping skill names to VersionInfo
    """
    installed = {}
    home = Path.home()
    skills_dir = home / ".claude" / "skills"
    
    if not skills_dir.exists():
        return installed
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        manifest_path = skill_dir / "manifest.yaml"
        if not manifest_path.exists():
            # Try to read from SKILL.md header
            skill_md_path = skill_dir / "SKILL.md"
            if skill_md_path.exists():
                # Create a dummy manifest
                installed[skill_dir.name] = VersionInfo(
                    skill_dir,
                    {'name': skill_dir.name, 'version': '0.0.0'}
                )
            continue
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            installed[manifest['name']] = VersionInfo(skill_dir, manifest)
        except Exception:
            continue
    
    return installed


def get_available_skills() -> Dict[str, VersionInfo]:
    """
    Gets available skills from the repository.
    
    Returns:
        Dict mapping skill names to VersionInfo
    """
    available = {}
    skills_dir = ARCHON_ROOT / "skills"
    
    if not skills_dir.exists():
        return available
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        manifest_path = skill_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            available[manifest['name']] = VersionInfo(skill_dir, manifest)
        except Exception:
            continue
    
    return available


def compare_versions(v1: str, v2: str) -> int:
    """
    Compares two semantic versions.
    
    Args:
        v1: First version
        v2: Second version
        
    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    def parse_version(v):
        try:
            parts = v.split('.')
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    parsed_v1 = parse_version(v1)
    parsed_v2 = parse_version(v2)
    
    if parsed_v1 < parsed_v2:
        return -1
    elif parsed_v1 > parsed_v2:
        return 1
    else:
        return 0


def check_updates(platform: str = "claude-code") -> List[Tuple[str, str, str]]:
    """
    Checks for available updates.

    Args:
        platform: Platform to check (default: claude-code)

    Returns:
        List of (skill_name, current_version, new_version) tuples
    """
    installed = get_installed_skills(platform)
    available = get_available_skills()
    
    updates = []
    
    for skill_name, available_info in available.items():
        if skill_name not in installed:
            continue  # Not installed
        
        installed_info = installed[skill_name]
        
        if compare_versions(installed_info.version, available_info.version) < 0:
            updates.append((skill_name, installed_info.version, available_info.version))
    
    return updates


def backup_skill(skill_path: Path) -> Optional[Path]:
    """
    Creates a backup of a skill.
    
    Args:
        skill_path: Path to skill directory
        
    Returns:
        Path to backup directory or None if failed
    """
    try:
        backup_dir = skill_path.parent / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{skill_path.name}_{timestamp}"
        
        shutil.copytree(skill_path, backup_path)
        return backup_path
        
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
        return None


def apply_update(skill_name: str, platform: str = "claude-code") -> bool:
    """
    Applies an update for a skill.

    Args:
        skill_name: Name of the skill to update
        platform: Platform name (only claude-code is supported)

    Returns:
        True if successful
    """
    # Get source and target paths
    source_path = ARCHON_ROOT / "skills" / skill_name

    if not source_path.exists():
        print(f"Skill not found in repository: {skill_name}")
        return False

    home = Path.home()
    target_base = home / ".claude" / "skills"
    
    target_path = target_base / skill_name
    
    if not target_path.exists():
        print(f"❌ Skill not installed: {skill_name}")
        return False
    
    try:
        # Create backup
        print(f"📦 Backing up {skill_name}...")
        backup_path = backup_skill(target_path)
        
        if backup_path:
            print(f"   Backup created: {backup_path.name}")
        
        # Update skill
        print(f"🔄 Updating {skill_name}...")
        
        # Remove old version
        shutil.rmtree(target_path)
        
        # Copy new version
        shutil.copytree(source_path, target_path)
        
        print(f"✅ Updated: {skill_name}")
        return True
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        
        # Try to restore backup
        if backup_path and backup_path.exists():
            print(f"🔄 Restoring from backup...")
            try:
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(backup_path, target_path)
                print(f"✅ Restored from backup")
            except Exception as restore_error:
                print(f"❌ Restore failed: {restore_error}")
        
        return False


def rollback_skill(skill_name: str, platform: str = "claude-code") -> bool:
    """
    Rolls back a skill to its previous version.

    Args:
        skill_name: Name of the skill to rollback
        platform: Platform name (only claude-code is supported)

    Returns:
        True if successful
    """
    home = Path.home()
    skills_base = home / ".claude" / "skills"
    
    backup_dir = skills_base / ".backups"
    
    if not backup_dir.exists():
        print(f"❌ No backups found")
        return False
    
    # Find latest backup for this skill
    backups = sorted([b for b in backup_dir.iterdir() if b.name.startswith(skill_name + "_")], reverse=True)
    
    if not backups:
        print(f"❌ No backup found for {skill_name}")
        return False
    
    latest_backup = backups[0]
    target_path = skills_base / skill_name
    
    try:
        print(f"🔄 Rolling back {skill_name} to {latest_backup.name}...")
        
        # Remove current version
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # Restore backup
        shutil.copytree(latest_backup, target_path)
        
        print(f"✅ Rolled back: {skill_name}")
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Archon updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update.py --check                # Check for updates
  python update.py --apply                # Apply all updates
  python update.py --apply godot-gdscript # Update specific skill
  python update.py --rollback godot-kit   # Rollback skill
        """
    )
    
    parser.add_argument('--check', action='store_true', help='Check for available updates')
    parser.add_argument('--apply', nargs='?', const='all', help='Apply updates (all or specific skill)')
    parser.add_argument('--rollback', help='Rollback a skill to previous version')
    parser.add_argument('--platform', default='claude-code',
                       help='Target platform')
    
    args = parser.parse_args()
    
    print("\n🔄 Archon Update Manager")
    print("=" * 60)
    
    if args.check or (not args.apply and not args.rollback):
        # Check for updates
        print(f"\n🔍 Checking for updates on {args.platform}...\n")
        
        updates = check_updates(args.platform)
        
        if not updates:
            print("✅ All skills are up to date!")
            return 0
        
        print(f"📦 {len(updates)} update(s) available:\n")
        
        for skill_name, current, new in updates:
            print(f"• {skill_name}")
            print(f"  {current} → {new}")
        
        print("\n💡 Run with --apply to install updates")
        
    elif args.apply:
        # Apply updates
        if args.apply == 'all':
            print(f"\n🔄 Applying all updates for {args.platform}...\n")
            
            updates = check_updates(args.platform)
            
            if not updates:
                print("✅ All skills are up to date!")
                return 0
            
            success_count = 0
            
            for skill_name, current, new in updates:
                print(f"\n📦 Updating {skill_name} ({current} → {new})")
                
                if apply_update(skill_name, args.platform):
                    success_count += 1
            
            print("\n" + "=" * 60)
            print(f"✅ Updated {success_count}/{len(updates)} skills")
            
        else:
            # Update specific skill
            print(f"\n🔄 Updating {args.apply} on {args.platform}...\n")
            
            if apply_update(args.apply, args.platform):
                return 0
            else:
                return 1
    
    elif args.rollback:
        # Rollback skill
        print(f"\n🔙 Rolling back {args.rollback} on {args.platform}...\n")
        
        if rollback_skill(args.rollback, args.platform):
            return 0
        else:
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
