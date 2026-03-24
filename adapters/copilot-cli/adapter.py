"""
Copilot CLI Adapter
Installs skills to ~/.copilot/skills/{skill-name}/SKILL.md
"""

from pathlib import Path
from typing import Dict, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base import BaseAdapter


class CopilotCLIAdapter(BaseAdapter):
    """Adapter for Copilot CLI skills."""
    
    def __init__(self):
        super().__init__("copilot-cli")
    
    def get_target_path(self, skill_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns ~/.copilot/skills/{skill-name}/SKILL.md
        
        Args:
            skill_name: Name of the skill
            target_dir: Optional override for target directory
            
        Returns:
            Path where the skill should be installed
        """
        if target_dir:
            base_dir = target_dir
        else:
            base_dir = Path.home() / ".copilot" / "skills"
        
        return base_dir / skill_name / "SKILL.md"
    
    def transform_content(self, content: str, manifest: Dict) -> str:
        """
        Copilot CLI uses the same format, so no transformation needed.
        
        Args:
            content: Original SKILL.md content
            manifest: Parsed manifest.yaml
            
        Returns:
            Unchanged content
        """
        return content
    
    def _copy_additional_resources(self, skill_path: Path, target_parent: Path):
        """
        Copilot CLI supports examples/ and templates/ directories.
        
        Args:
            skill_path: Source skill directory
            target_parent: Parent directory of target installation
        """
        # Copy examples if they exist
        examples_src = skill_path / "examples"
        if examples_src.exists():
            examples_dst = target_parent / "examples"
            self.copy_directory(examples_src, examples_dst)
            print(f"   📁 Copied examples/")
        
        # Copy templates if they exist
        templates_src = skill_path / "templates"
        if templates_src.exists():
            templates_dst = target_parent / "templates"
            self.copy_directory(templates_src, templates_dst)
            print(f"   📁 Copied templates/")


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install skills to Copilot CLI")
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument("--target-dir", type=Path, help="Override target directory")
    
    args = parser.parse_args()
    
    adapter = CopilotCLIAdapter()
    success = adapter.install_skill(args.skill_path, args.target_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
