"""
Claude Code Adapter
Installs skills to ~/.claude/skills/{skill-name}/SKILL.md
"""

from pathlib import Path
from typing import Dict, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from base import BaseAdapter


class ClaudeCodeAdapter(BaseAdapter):
    """Adapter for Claude Code skills."""
    
    def __init__(self):
        super().__init__("claude-code")
    
    def get_target_path(self, skill_name: str, target_dir: Optional[Path] = None) -> Path:
        """
        Returns ~/.claude/skills/{skill-name}/SKILL.md
        
        Args:
            skill_name: Name of the skill
            target_dir: Optional override for target directory
            
        Returns:
            Path where the skill should be installed
        """
        if target_dir:
            base_dir = target_dir
        else:
            base_dir = Path.home() / ".claude" / "skills"
        
        return base_dir / skill_name / "SKILL.md"
    
    def transform_content(self, content: str, manifest: Dict) -> str:
        """
        Claude Code uses the same format, so no transformation needed.
        
        Args:
            content: Original SKILL.md content
            manifest: Parsed manifest.yaml
            
        Returns:
            Unchanged content
        """
        return content


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install skills to Claude Code")
    parser.add_argument("skill_path", type=Path, help="Path to skill directory")
    parser.add_argument("--target-dir", type=Path, help="Override target directory")
    
    args = parser.parse_args()
    
    adapter = ClaudeCodeAdapter()
    success = adapter.install_skill(args.skill_path, args.target_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
