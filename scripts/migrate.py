#!/usr/bin/env python3
"""
OMNISKILL Migration Helper
Converts skills from various formats to OMNISKILL format.

Usage:
    python migrate.py source/ --output-dir migrated/
    python migrate.py copilot-skill/ --format copilot-cli
    python migrate.py --auto-detect source-dir/
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, Optional, List
import yaml


OMNISKILL_ROOT = Path(__file__).parent.parent


def detect_format(source_path: Path) -> Optional[str]:
    """
    Detects the format of a skill directory.
    
    Args:
        source_path: Path to source skill directory
        
    Returns:
        Format name or None if unrecognized
    """
    # Check for OMNISKILL format
    if (source_path / "SKILL.md").exists() and (source_path / "manifest.yaml").exists():
        return "omniskill"
    
    # Check for Copilot CLI format
    if (source_path / "SKILL.md").exists():
        return "copilot-cli"
    
    # Check for Cursor format (.mdc files)
    if list(source_path.glob("*.mdc")):
        return "cursor"
    
    # Check for generic markdown
    md_files = list(source_path.glob("*.md"))
    if md_files:
        return "generic-md"
    
    return None


def extract_metadata_from_markdown(content: str) -> Dict:
    """
    Extracts metadata from markdown content using heuristics.
    
    Args:
        content: Markdown content
        
    Returns:
        Extracted metadata dict
    """
    metadata = {
        'name': '',
        'version': '1.0.0',
        'description': '',
        'author': 'unknown',
        'platforms': ['copilot-cli', 'claude-code'],
        'tags': [],
        'triggers': {'keywords': []},
        'priority': 'P2'
    }
    
    # Try to extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # Convert to kebab-case
        metadata['name'] = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        metadata['description'] = title
    
    # Try to extract description (first paragraph after title)
    desc_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n#)', content, re.MULTILINE | re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        # Limit to 200 chars
        if len(desc) > 200:
            desc = desc[:197] + "..."
        metadata['description'] = desc
    
    # Try to extract keywords from "Triggers", "When to Use", etc.
    triggers_section = re.search(r'(?i)##\s+(?:triggers?|when to use|activation)\s*\n(.+?)(?:\n##|\Z)', content, re.MULTILINE | re.DOTALL)
    if triggers_section:
        triggers_text = triggers_section.group(1)
        # Extract bullet points
        keywords = re.findall(r'[-*]\s*(.+?)(?:\n|$)', triggers_text)
        metadata['triggers']['keywords'] = [k.strip() for k in keywords[:5]]  # Limit to 5
    
    # Try to extract tags
    tags_match = re.search(r'(?i)(?:tags?|categories):\s*(.+?)$', content, re.MULTILINE)
    if tags_match:
        tags_text = tags_match.group(1)
        metadata['tags'] = [t.strip() for t in re.split(r'[,;]', tags_text) if t.strip()]
    
    # If no triggers found, use the skill name as a trigger
    if not metadata['triggers']['keywords']:
        if metadata['name']:
            metadata['triggers']['keywords'] = [metadata['name'].replace('-', ' ')]
    
    # If no tags found, try to infer from content
    if not metadata['tags']:
        # Common technology keywords
        tech_keywords = ['python', 'javascript', 'typescript', 'react', 'vue', 'angular', 
                        'godot', 'unity', 'django', 'flask', 'api', 'testing', 'database']
        
        content_lower = content.lower()
        found_tags = [kw for kw in tech_keywords if kw in content_lower]
        metadata['tags'] = found_tags[:5] if found_tags else ['general']
    
    return metadata


def migrate_copilot_cli(source_path: Path) -> tuple[str, Dict]:
    """
    Migrates a Copilot CLI skill.
    
    Args:
        source_path: Path to source skill
        
    Returns:
        Tuple of (skill_md_content, manifest_dict)
    """
    skill_md = source_path / "SKILL.md"
    
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata
    metadata = extract_metadata_from_markdown(content)
    metadata['name'] = source_path.name  # Use directory name
    
    return content, metadata


def migrate_cursor(source_path: Path) -> tuple[str, Dict]:
    """
    Migrates a Cursor .mdc skill.
    
    Args:
        source_path: Path to source skill
        
    Returns:
        Tuple of (skill_md_content, manifest_dict)
    """
    mdc_files = list(source_path.glob("*.mdc"))
    
    if not mdc_files:
        raise ValueError("No .mdc files found")
    
    # Read first .mdc file
    mdc_file = mdc_files[0]
    
    with open(mdc_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse front-matter
    metadata = {
        'name': mdc_file.stem,
        'version': '1.0.0',
        'description': '',
        'author': 'unknown',
        'platforms': ['cursor', 'copilot-cli', 'claude-code'],
        'tags': [],
        'triggers': {'keywords': []},
        'priority': 'P2'
    }
    
    # Extract front-matter if it exists
    front_matter_match = re.match(r'^---\n(.+?)\n---\n\n(.+)', content, re.DOTALL)
    
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        skill_content = front_matter_match.group(2)
        
        # Parse front-matter
        desc_match = re.search(r'description:\s*(.+?)$', front_matter_text, re.MULTILINE)
        if desc_match:
            metadata['description'] = desc_match.group(1).strip()
        
        globs_match = re.search(r'globs:\s*\n(.+?)(?:\n\w|$)', front_matter_text, re.MULTILINE | re.DOTALL)
        if globs_match:
            globs_text = globs_match.group(1)
            patterns = re.findall(r'-\s*(.+?)$', globs_text, re.MULTILINE)
            if patterns:
                metadata['triggers']['patterns'] = patterns
    else:
        skill_content = content
    
    # Extract additional metadata from content
    content_metadata = extract_metadata_from_markdown(skill_content)
    
    # Merge metadata
    if not metadata['description']:
        metadata['description'] = content_metadata['description']
    
    if not metadata['triggers']['keywords']:
        metadata['triggers']['keywords'] = content_metadata['triggers']['keywords']
    
    metadata['tags'] = content_metadata['tags']
    
    return skill_content, metadata


def migrate_generic_md(source_path: Path) -> tuple[str, Dict]:
    """
    Migrates a generic markdown skill.
    
    Args:
        source_path: Path to source skill
        
    Returns:
        Tuple of (skill_md_content, manifest_dict)
    """
    md_files = list(source_path.glob("*.md"))
    
    if not md_files:
        raise ValueError("No .md files found")
    
    # Read first markdown file
    md_file = md_files[0]
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata
    metadata = extract_metadata_from_markdown(content)
    metadata['name'] = source_path.name  # Use directory name
    
    return content, metadata


def create_omniskill(skill_content: str, metadata: Dict, output_dir: Path) -> bool:
    """
    Creates an OMNISKILL-format skill.
    
    Args:
        skill_content: SKILL.md content
        metadata: Manifest metadata
        output_dir: Output directory for the skill
        
    Returns:
        True if successful
    """
    try:
        # Create output directory
        skill_dir = output_dir / metadata['name']
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md
        skill_md_path = skill_dir / "SKILL.md"
        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(skill_content)
        
        # Write manifest.yaml
        manifest_path = skill_dir / "manifest.yaml"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"✅ Migrated: {metadata['name']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create skill {metadata['name']}: {e}")
        return False


def migrate_skill(source_path: Path, output_dir: Path, format_hint: Optional[str] = None) -> bool:
    """
    Migrates a single skill.
    
    Args:
        source_path: Path to source skill
        output_dir: Output directory
        format_hint: Optional format hint
        
    Returns:
        True if successful
    """
    # Detect format
    if format_hint:
        detected_format = format_hint
    else:
        detected_format = detect_format(source_path)
    
    if not detected_format:
        print(f"⚠️  Could not detect format for {source_path}")
        return False
    
    print(f"🔍 Detected format: {detected_format}")
    
    # Check if already OMNISKILL format
    if detected_format == "omniskill":
        print(f"⚠️  {source_path.name} is already in OMNISKILL format")
        return False
    
    # Migrate based on format
    try:
        if detected_format == "copilot-cli":
            content, metadata = migrate_copilot_cli(source_path)
        elif detected_format == "cursor":
            content, metadata = migrate_cursor(source_path)
        elif detected_format == "generic-md":
            content, metadata = migrate_generic_md(source_path)
        else:
            print(f"❌ Unsupported format: {detected_format}")
            return False
        
        # Create OMNISKILL skill
        return create_omniskill(content, metadata, output_dir)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate skills to OMNISKILL format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate.py source-skill/ --output-dir migrated/
  python migrate.py legacy-skills/ --format copilot-cli
  python migrate.py --auto-detect old-skills/
  
Supported formats:
  • copilot-cli   - Copilot CLI SKILL.md format
  • cursor        - Cursor .mdc format
  • generic-md    - Generic markdown files
        """
    )
    
    parser.add_argument('source', type=Path, help='Source skill directory or parent directory')
    parser.add_argument('--output-dir', type=Path, default=Path('migrated'), help='Output directory')
    parser.add_argument('--format', choices=['copilot-cli', 'cursor', 'generic-md'], help='Force specific format')
    parser.add_argument('--auto-detect', action='store_true', help='Auto-detect and migrate all subdirectories')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n🔄 OMNISKILL Migration Tool")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    if args.auto_detect:
        # Migrate all subdirectories
        print(f"\n📂 Auto-detecting skills in {args.source}\n")
        
        for item in args.source.iterdir():
            if item.is_dir():
                total_count += 1
                print(f"\n🔍 Processing: {item.name}")
                
                if migrate_skill(item, args.output_dir, args.format):
                    success_count += 1
    else:
        # Migrate single skill
        total_count = 1
        
        if migrate_skill(args.source, args.output_dir, args.format):
            success_count = 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✅ Migrated: {success_count}/{total_count}")
    print(f"📁 Output directory: {args.output_dir.absolute()}")
    
    if success_count > 0:
        print("\n💡 Next steps:")
        print("  1. Review the migrated skills")
        print("  2. Validate them with: python scripts/validate.py --skills")
        print("  3. Install them with: python scripts/install.py --all")
    
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
