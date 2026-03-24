"""
Windsurf Adapter
Installs skills to .windsurfrules (single file, all rules concatenated)
"""

from pathlib import Path
from typing import Dict, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base import BaseAdapter


class WindsurfAdapter(BaseAdapter):
    """Adapter for Windsurf rules."""
    
    def __init__(self):
        super().__init__("windsurf")
    
    def get_target_path(self, skill_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns .windsurfrules (single file for all skills)
        """
        if target_dir:
            base_dir = target_dir
        else:
            base_dir = Path.cwd()
        
        return base_dir / ".windsurfrules"
    
    def get_synapse_target_path(self, synapse_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns .windsurf/_synapses/{synapse-name}/SYNAPSE.md
        Windsurf synapses go in a separate directory since .windsurfrules is a single file.
        """
        if target_dir:
            base_dir = target_dir
        else:
            base_dir = Path.cwd() / ".windsurf"
        
        return base_dir / "_synapses" / synapse_name / "SYNAPSE.md"
    
    def transform_content(self, content: str, manifest: Dict) -> str:
        """
        Wraps content with section separator for concatenation.
        
        Args:
            content: Original SKILL.md content
            manifest: Parsed manifest.yaml
            
        Returns:
            Content with section header
        """
        skill_name = manifest.get('name', 'unknown')
        description = manifest.get('description', '')
        
        # Create section separator
        header = f"\n\n{'=' * 80}\n"
        header += f"# SKILL: {skill_name}\n"
        header += f"# {description}\n"
        header += f"{'=' * 80}\n\n"
        
        return header + content
    
    def install_skill(self, skill_path: Path, target_dir: Optional[Path] = None) -> bool:
        """
        Appends skill to .windsurfrules file.
        
        Args:
            skill_path: Path to skill directory
            target_dir: Optional override for target directory
            
        Returns:
            True if installation succeeded, False otherwise
        """
        try:
            # Read skill
            content, manifest = self.read_skill(skill_path)
            
            # Check if platform is supported
            if self.platform_name not in manifest.get('platforms', []):
                print(f"⚠️  Skill {manifest['name']} does not support {self.platform_name}")
                return False
            
            # Apply overrides
            content = self.apply_overrides(content, skill_path)
            
            # Transform content
            content = self.transform_content(content, manifest)
            
            # Get target path
            target_path = self.get_target_path(manifest['name'], target_dir)
            
            # Append to file (create if doesn't exist)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if skill already exists in file
            if target_path.exists():
                with open(target_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Look for existing section
                skill_marker = f"# SKILL: {manifest['name']}"
                if skill_marker in existing_content:
                    print(f"⚠️  Skill {manifest['name']} already exists in {target_path}")
                    return False
            
            # Append to file
            with open(target_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Appended {manifest['name']} to {target_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install skill from {skill_path}: {e}")
            return False
    
    def install_bundle(self, bundle_path: Path, target_dir: Optional[Path] = None) -> tuple:
        """
        Installs all skills in a bundle to .windsurfrules.
        
        Args:
            bundle_path: Path to bundle directory
            target_dir: Optional override for target directory
            
        Returns:
            Tuple of (success_count, total_count)
        """
        import yaml
        
        bundle_manifest_path = bundle_path / "bundle.yaml"
        
        if not bundle_manifest_path.exists():
            print(f"❌ bundle.yaml not found in {bundle_path}")
            return (0, 0)
        
        with open(bundle_manifest_path, 'r', encoding='utf-8') as f:
            bundle_manifest = yaml.safe_load(f)
        
        skills = bundle_manifest.get('skills', [])
        success_count = 0
        
        # Get archon root (assume bundle is in bundles/)
        archon_root = bundle_path.parent.parent
        
        print(f"\n📦 Installing bundle: {bundle_manifest['name']}")
        print(f"   Skills: {', '.join(skills)}")
        
        # Add bundle header to .windsurfrules
        target_path = self.get_target_path("", target_dir)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        bundle_header = f"\n\n{'#' * 80}\n"
        bundle_header += f"# BUNDLE: {bundle_manifest['name']}\n"
        bundle_header += f"# {bundle_manifest.get('description', '')}\n"
        bundle_header += f"{'#' * 80}\n\n"
        
        with open(target_path, 'a', encoding='utf-8') as f:
            f.write(bundle_header)
        
        for skill_name in skills:
            skill_path = archon_root / "skills" / skill_name
            
            if not skill_path.exists():
                print(f"⚠️  Skill not found: {skill_name}")
                continue
            
            if self.install_skill(skill_path, target_dir):
                success_count += 1
        
        # Also install the meta-skill
        meta_skill_path = bundle_path / "meta-skill"
        if meta_skill_path.exists():
            print(f"\n📋 Installing meta-skill for {bundle_manifest['name']}")
            if self.install_skill(meta_skill_path, target_dir):
                success_count += 1
                skills.append(f"{bundle_manifest['name']}-meta")
        
        print(f"\n✅ Appended {success_count}/{len(skills)} skills to {target_path}")
        return (success_count, len(skills))


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install skills to Windsurf")
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument("--target-dir", type=Path, help="Override target directory")
    
    args = parser.parse_args()
    
    adapter = WindsurfAdapter()
    success = adapter.install_skill(args.skill_path, args.target_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
