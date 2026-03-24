"""
Antigravity Adapter
Installs skills to .antigravity/skills/{skill-name}.md
"""

from pathlib import Path
from typing import Dict, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base import BaseAdapter


class AntigravityAdapter(BaseAdapter):
    """Adapter for Antigravity skills."""
    
    def __init__(self):
        super().__init__("antigravity")
    
    def get_target_path(self, skill_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns .antigravity/skills/{skill-name}.md
        
        Args:
            skill_name: Name of the skill
            target_dir: Optional override for target directory
            
        Returns:
            Path where the skill should be installed
        """
        if target_dir:
            base_dir = target_dir
        else:
            # Antigravity skills are project-specific, so use current directory
            base_dir = Path.cwd() / ".antigravity" / "skills"
        
        return base_dir / f"{skill_name}.md"
    
    def transform_content(self, content: str, manifest: Dict) -> str:
        """
        Antigravity uses markdown format similar to SKILL.md.
        
        Args:
            content: Original SKILL.md content
            manifest: Parsed manifest.yaml
            
        Returns:
            Content (with minimal transformation)
        """
        # Add a header comment with metadata
        skill_name = manifest.get('name', 'unknown')
        version = manifest.get('version', '1.0.0')
        description = manifest.get('description', '')
        
        header = f"<!-- Archon: {skill_name} v{version} -->\n"
        header += f"<!-- {description} -->\n\n"
        
        return header + content


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install skills to Antigravity")
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument("--target-dir", type=Path, help="Override target directory")
    
    args = parser.parse_args()
    
    adapter = AntigravityAdapter()
    success = adapter.install_skill(args.skill_path, args.target_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
