"""
Cursor Adapter
Installs skills to .cursor/rules/{skill-name}.mdc
"""

from pathlib import Path
from typing import Dict, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base import BaseAdapter


class CursorAdapter(BaseAdapter):
    """Adapter for Cursor rules."""
    
    def __init__(self):
        super().__init__("cursor")
    
    def get_target_path(self, skill_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns .cursor/rules/{skill-name}.mdc
        
        Args:
            skill_name: Name of the skill
            target_dir: Optional override for target directory
            
        Returns:
            Path where the skill should be installed
        """
        if target_dir:
            base_dir = target_dir
        else:
            # Cursor rules are project-specific, so use current directory
            base_dir = Path.cwd() / ".cursor" / "rules"
        
        return base_dir / f"{skill_name}.mdc"
    
    def transform_content(self, content: str, manifest: Dict) -> str:
        """
        Wraps content in Cursor .mdc format with front-matter.
        
        Args:
            content: Original SKILL.md content
            manifest: Parsed manifest.yaml
            
        Returns:
            Content wrapped in .mdc format
        """
        # Extract description and tags from manifest
        description = manifest.get('description', 'OMNISKILL skill')
        tags = manifest.get('tags', [])
        
        # Determine globs from triggers if patterns exist
        triggers = manifest.get('triggers', {})
        patterns = triggers.get('patterns', [])
        globs_str = "\n".join([f"  - {pattern}" for pattern in patterns]) if patterns else ""
        
        # Build front-matter
        front_matter = f"""---
description: {description}
"""
        
        if globs_str:
            front_matter += f"globs:\n{globs_str}\n"
        else:
            front_matter += "globs:\n"
        
        front_matter += "alwaysApply: false\n---\n\n"
        
        # Combine front-matter with content
        return front_matter + content


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install skills to Cursor")
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument("--target-dir", type=Path, help="Override target directory")
    
    args = parser.parse_args()
    
    adapter = CursorAdapter()
    success = adapter.install_skill(args.skill_path, args.target_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
