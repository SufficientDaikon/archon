"""
OMNISKILL Base Adapter
Shared functionality for all platform adapters.
"""

import os
import shutil
import yaml
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class BaseAdapter(ABC):
    """Base class for all platform adapters."""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
    
    def read_skill(self, skill_path: Path) -> Tuple[str, Dict]:
        """
        Reads SKILL.md and manifest.yaml from a skill directory.
        
        Args:
            skill_path: Path to skill directory
            
        Returns:
            Tuple of (skill_md_content, manifest_dict)
        """
        skill_md_path = skill_path / "SKILL.md"
        manifest_path = skill_path / "manifest.yaml"
        
        if not skill_md_path.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_path}")
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"manifest.yaml not found in {skill_path}")
        
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            skill_content = f.read()
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
        
        return skill_content, manifest
    
    def apply_overrides(self, content: str, skill_path: Path) -> str:
        """
        Merges platform-specific overrides into the skill content.
        
        Args:
            content: Original SKILL.md content
            skill_path: Path to skill directory
            
        Returns:
            Modified content with overrides applied
        """
        override_path = skill_path / "overrides" / f"{self.platform_name}.md"
        
        if override_path.exists():
            with open(override_path, 'r', encoding='utf-8') as f:
                override_content = f.read()
            
            # Append overrides with a separator
            content = f"{content}\n\n---\n\n# Platform Overrides ({self.platform_name})\n\n{override_content}"
        
        return content
    
    def write_output(self, content: str, target_path: Path, create_dirs: bool = True):
        """
        Writes content to target file, creating directories if needed.
        
        Args:
            content: Content to write
            target_path: Destination file path
            create_dirs: Whether to create parent directories
        """
        if create_dirs:
            target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def copy_directory(self, src: Path, dst: Path):
        """
        Copies a directory tree.
        
        Args:
            src: Source directory
            dst: Destination directory
        """
        if src.exists() and src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
    
    @abstractmethod
    def get_target_path(self, skill_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns the platform-specific installation path for a skill.
        
        Args:
            skill_name: Name of the skill
            target_dir: Optional override for target directory
            
        Returns:
            Path where the skill should be installed
        """
        pass
    
    @abstractmethod
    def transform_content(self, content: str, manifest: Dict) -> str:
        """
        Transforms SKILL.md content to platform-specific format.
        
        Args:
            content: Original SKILL.md content
            manifest: Parsed manifest.yaml
            
        Returns:
            Platform-specific formatted content
        """
        pass
    
    def install_skill(self, skill_path: Path, target_dir: Optional[Path] = None) -> bool:
        """
        Full install flow for a single skill.
        
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
            
            # Write output
            self.write_output(content, target_path)
            
            # Copy additional directories if they exist
            self._copy_additional_resources(skill_path, target_path.parent)
            
            print(f"✅ Installed {manifest['name']} to {target_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install skill from {skill_path}: {e}")
            return False
    
    def install_bundle(self, bundle_path: Path, target_dir: Optional[Path] = None) -> Tuple[int, int]:
        """
        Installs all skills in a bundle.
        
        Args:
            bundle_path: Path to bundle directory
            target_dir: Optional override for target directory
            
        Returns:
            Tuple of (success_count, total_count)
        """
        bundle_manifest_path = bundle_path / "bundle.yaml"
        
        if not bundle_manifest_path.exists():
            print(f"❌ bundle.yaml not found in {bundle_path}")
            return (0, 0)
        
        with open(bundle_manifest_path, 'r', encoding='utf-8') as f:
            bundle_manifest = yaml.safe_load(f)
        
        skills = bundle_manifest.get('skills', [])
        success_count = 0
        
        # Get omniskill root (assume bundle is in bundles/)
        omniskill_root = bundle_path.parent.parent
        
        print(f"\n📦 Installing bundle: {bundle_manifest['name']}")
        print(f"   Skills: {', '.join(skills)}")
        
        for skill_name in skills:
            skill_path = omniskill_root / "skills" / skill_name
            
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
        
        print(f"\n✅ Installed {success_count}/{len(skills)} skills from {bundle_manifest['name']}")
        return (success_count, len(skills))
    
    def _copy_additional_resources(self, skill_path: Path, target_parent: Path):
        """
        Copies additional directories (examples, templates, etc.) if needed by platform.
        Override in subclasses if needed.
        
        Args:
            skill_path: Source skill directory
            target_parent: Parent directory of target installation
        """
        pass
