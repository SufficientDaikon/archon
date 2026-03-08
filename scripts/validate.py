#!/usr/bin/env python3
"""
OMNISKILL Validator
Validates skills, bundles, agents, and pipelines against schemas.

Usage:
    python validate.py --all                      # Validate everything
    python validate.py skills/godot-gdscript      # Validate specific skill
    python validate.py bundles/godot-kit          # Validate specific bundle
    python validate.py --skills                   # Validate all skills
    python validate.py --bundles                  # Validate all bundles
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import yaml


OMNISKILL_ROOT = Path(__file__).parent.parent


class ValidationResult:
    """Stores validation results."""
    
    def __init__(self, path: str):
        self.path = path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed = True
    
    def add_error(self, message: str):
        """Add an error."""
        self.errors.append(message)
        self.passed = False
    
    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)
    
    def has_issues(self) -> bool:
        """Check if there are any issues."""
        return bool(self.errors or self.warnings)
    
    def print_report(self):
        """Print the validation report."""
        if self.passed and not self.warnings:
            print(f"✅ {self.path}")
        else:
            print(f"\n{'❌' if not self.passed else '⚠️'} {self.path}")
            
            if self.errors:
                print("\n  Errors:")
                for error in self.errors:
                    print(f"    • {error}")
            
            if self.warnings:
                print("\n  Warnings:")
                for warning in self.warnings:
                    print(f"    • {warning}")


def load_schema(schema_name: str) -> Dict:
    """
    Loads a schema YAML file.
    
    Args:
        schema_name: Name of the schema file (e.g., 'skill-manifest.schema.yaml')
        
    Returns:
        Parsed schema dict
    """
    schema_path = OMNISKILL_ROOT / "schemas" / schema_name
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_manifest_field(field_name: str, field_value, field_schema: Dict, result: ValidationResult):
    """
    Validates a single manifest field against its schema.
    
    Args:
        field_name: Name of the field
        field_value: Value to validate
        field_schema: Schema for this field
        result: ValidationResult to append errors to
    """
    field_type = field_schema.get('type')
    
    # Check type
    if field_type == 'string':
        if not isinstance(field_value, str):
            result.add_error(f"{field_name}: Expected string, got {type(field_value).__name__}")
            return
        
        # Check pattern
        if 'pattern' in field_schema:
            pattern = field_schema['pattern']
            if not re.match(pattern, field_value):
                result.add_error(f"{field_name}: Value '{field_value}' does not match pattern {pattern}")
        
        # Check length
        if 'min_length' in field_schema and len(field_value) < field_schema['min_length']:
            result.add_error(f"{field_name}: Length {len(field_value)} < minimum {field_schema['min_length']}")
        
        if 'max_length' in field_schema and len(field_value) > field_schema['max_length']:
            result.add_error(f"{field_name}: Length {len(field_value)} > maximum {field_schema['max_length']}")
    
    elif field_type == 'list':
        if not isinstance(field_value, list):
            result.add_error(f"{field_name}: Expected list, got {type(field_value).__name__}")
            return
        
        # Check min items
        if 'min_items' in field_schema and len(field_value) < field_schema['min_items']:
            result.add_error(f"{field_name}: List has {len(field_value)} items, minimum is {field_schema['min_items']}")
        
        # Check allowed values
        if 'allowed_values' in field_schema:
            allowed = field_schema['allowed_values']
            for item in field_value:
                if item not in allowed:
                    result.add_error(f"{field_name}: Value '{item}' not in allowed values {allowed}")
    
    elif field_type == 'object':
        if not isinstance(field_value, dict):
            result.add_error(f"{field_name}: Expected object, got {type(field_value).__name__}")
            return
        
        # Check required children
        if 'required_children' in field_schema:
            for child_name, child_schema in field_schema['required_children'].items():
                if child_name not in field_value:
                    result.add_error(f"{field_name}.{child_name}: Required field missing")
                else:
                    validate_manifest_field(f"{field_name}.{child_name}", field_value[child_name], child_schema, result)


def validate_skill_manifest(manifest_path: Path) -> ValidationResult:
    """
    Validates a skill manifest.yaml file.
    
    Args:
        manifest_path: Path to manifest.yaml
        
    Returns:
        ValidationResult
    """
    result = ValidationResult(str(manifest_path.parent))
    
    # Check if file exists
    if not manifest_path.exists():
        result.add_error("manifest.yaml not found")
        return result
    
    # Load manifest
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
    except Exception as e:
        result.add_error(f"Failed to parse YAML: {e}")
        return result
    
    # Load schema
    try:
        schema = load_schema("skill-manifest.schema.yaml")
    except Exception as e:
        result.add_error(f"Failed to load schema: {e}")
        return result
    
    # Validate required fields
    required_fields = schema.get('required_fields', {})
    for field_name, field_schema in required_fields.items():
        if field_name not in manifest:
            result.add_error(f"Required field missing: {field_name}")
        else:
            validate_manifest_field(field_name, manifest[field_name], field_schema, result)
    
    # Check for SKILL.md
    skill_md_path = manifest_path.parent / "SKILL.md"
    if not skill_md_path.exists():
        result.add_error("SKILL.md not found")
    else:
        # Validate SKILL.md sections
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = schema.get('skill_md_required_sections', [])
        for section in required_sections:
            # Check if section header exists (flexible matching)
            pattern = rf'(?i)^#+\s*{re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE):
                result.add_warning(f"SKILL.md: Missing recommended section '{section}'")
    
    return result


def validate_bundle_manifest(manifest_path: Path) -> ValidationResult:
    """
    Validates a bundle.yaml file.
    
    Args:
        manifest_path: Path to bundle.yaml
        
    Returns:
        ValidationResult
    """
    result = ValidationResult(str(manifest_path.parent))
    
    # Check if file exists
    if not manifest_path.exists():
        result.add_error("bundle.yaml not found")
        return result
    
    # Load manifest
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
    except Exception as e:
        result.add_error(f"Failed to parse YAML: {e}")
        return result
    
    # Load schema
    try:
        schema = load_schema("bundle-manifest.schema.yaml")
    except Exception as e:
        result.add_error(f"Failed to load schema: {e}")
        return result
    
    # Validate required fields
    required_fields = schema.get('required_fields', {})
    for field_name, field_schema in required_fields.items():
        if field_name not in manifest:
            result.add_error(f"Required field missing: {field_name}")
        else:
            validate_manifest_field(field_name, manifest[field_name], field_schema, result)
    
    # Check that skills exist
    skills = manifest.get('skills', [])
    skills_dir = OMNISKILL_ROOT / "skills"
    
    for skill_name in skills:
        skill_path = skills_dir / skill_name
        if not skill_path.exists():
            result.add_error(f"Referenced skill not found: {skill_name}")
    
    # Check for meta-skill
    meta_skill_path = manifest_path.parent / "meta-skill"
    if not meta_skill_path.exists():
        result.add_error("meta-skill/ directory not found")
    else:
        if not (meta_skill_path / "SKILL.md").exists():
            result.add_error("meta-skill/SKILL.md not found")
        if not (meta_skill_path / "manifest.yaml").exists():
            result.add_error("meta-skill/manifest.yaml not found")
    
    # Check for circular dependencies
    if 'dependencies' in manifest:
        # This would require a full dependency graph analysis
        # For now, just check if bundle depends on itself
        bundle_name = manifest.get('name', '')
        if bundle_name in manifest['dependencies']:
            result.add_error(f"Circular dependency: Bundle depends on itself")
    
    return result


def check_trigger_uniqueness() -> List[str]:
    """
    Checks for duplicate triggers across all skills.
    
    Returns:
        List of error messages
    """
    errors = []
    trigger_map: Dict[str, List[str]] = {}
    
    skills_dir = OMNISKILL_ROOT / "skills"
    if not skills_dir.exists():
        return errors
    
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
    
    # Find duplicates
    for trigger, skills in trigger_map.items():
        if len(skills) > 1:
            errors.append(f"Trigger '{trigger}' is used by multiple skills: {', '.join(skills)}")
    
    return errors


def validate_all_skills() -> List[ValidationResult]:
    """
    Validates all skills in the skills/ directory.
    
    Returns:
        List of ValidationResult objects
    """
    results = []
    skills_dir = OMNISKILL_ROOT / "skills"
    
    if not skills_dir.exists():
        return results
    
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        
        manifest_path = skill_dir / "manifest.yaml"
        result = validate_skill_manifest(manifest_path)
        results.append(result)
    
    return results


def validate_all_bundles() -> List[ValidationResult]:
    """
    Validates all bundles in the bundles/ directory.
    
    Returns:
        List of ValidationResult objects
    """
    results = []
    bundles_dir = OMNISKILL_ROOT / "bundles"
    
    if not bundles_dir.exists():
        return results
    
    for bundle_dir in sorted(bundles_dir.iterdir()):
        if not bundle_dir.is_dir():
            continue
        
        manifest_path = bundle_dir / "bundle.yaml"
        result = validate_bundle_manifest(manifest_path)
        results.append(result)
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate OMNISKILL skills and bundles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate.py --all                    # Validate everything
  python validate.py skills/godot-gdscript    # Validate specific skill
  python validate.py --skills                 # Validate all skills
  python validate.py --bundles                # Validate all bundles
        """
    )
    
    parser.add_argument('path', nargs='?', help='Path to validate (skill or bundle directory)')
    parser.add_argument('--all', action='store_true', help='Validate everything')
    parser.add_argument('--skills', action='store_true', help='Validate all skills')
    parser.add_argument('--bundles', action='store_true', help='Validate all bundles')
    parser.add_argument('--check-triggers', action='store_true', help='Check for duplicate triggers')
    
    args = parser.parse_args()
    
    results = []
    
    if args.all:
        print("🔍 Validating all skills and bundles...\n")
        results.extend(validate_all_skills())
        results.extend(validate_all_bundles())
        
        # Check trigger uniqueness
        trigger_errors = check_trigger_uniqueness()
        if trigger_errors:
            print("\n⚠️  Trigger Conflicts:")
            for error in trigger_errors:
                print(f"   • {error}")
    
    elif args.skills:
        print("🔍 Validating all skills...\n")
        results.extend(validate_all_skills())
    
    elif args.bundles:
        print("🔍 Validating all bundles...\n")
        results.extend(validate_all_bundles())
    
    elif args.check_triggers:
        trigger_errors = check_trigger_uniqueness()
        if trigger_errors:
            print("⚠️  Trigger Conflicts Found:")
            for error in trigger_errors:
                print(f"   • {error}")
            return 1
        else:
            print("✅ No trigger conflicts found")
            return 0
    
    elif args.path:
        path = Path(args.path)
        
        if not path.is_absolute():
            path = OMNISKILL_ROOT / path
        
        if not path.exists():
            print(f"❌ Path not found: {path}")
            return 1
        
        # Determine what to validate
        if (path / "manifest.yaml").exists():
            results.append(validate_skill_manifest(path / "manifest.yaml"))
        elif (path / "bundle.yaml").exists():
            results.append(validate_bundle_manifest(path / "bundle.yaml"))
        else:
            print(f"❌ Not a valid skill or bundle directory: {path}")
            return 1
    
    else:
        parser.print_help()
        return 1
    
    # Print results
    for result in results:
        result.print_report()
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    warnings = sum(1 for r in results if r.warnings)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"📊 Total: {len(results)}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
