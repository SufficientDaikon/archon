#!/usr/bin/env python3
"""
Archon Validator
Validates skills, bundles, agents, pipelines, synapses, and hooks against schemas.

Usage:
    python validate.py --all                      # Validate everything
    python validate.py skills/godot-gdscript      # Validate specific skill
    python validate.py bundles/godot-kit          # Validate specific bundle
    python validate.py --skills                   # Validate all skills
    python validate.py --bundles                  # Validate all bundles
    python validate.py --pipelines                # Validate all pipelines
    python validate.py --agents                   # Validate agent guardrails
    python validate.py --synapses                 # Validate all synapses
    python validate.py --hooks                    # Validate hook system
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import yaml


ARCHON_ROOT = Path(__file__).parent.parent


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
    schema_path = ARCHON_ROOT / "schemas" / schema_name
    
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
    skills_dir = ARCHON_ROOT / "skills"
    
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
    
    skills_dir = ARCHON_ROOT / "skills"
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
    skills_dir = ARCHON_ROOT / "skills"
    
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
    bundles_dir = ARCHON_ROOT / "bundles"
    
    if not bundles_dir.exists():
        return results
    
    for bundle_dir in sorted(bundles_dir.iterdir()):
        if not bundle_dir.is_dir():
            continue
        
        manifest_path = bundle_dir / "bundle.yaml"
        result = validate_bundle_manifest(manifest_path)
        results.append(result)
    
    return results


def validate_pipelines() -> List[ValidationResult]:
    """
    Validates all pipelines in the pipelines/ directory.

    Checks:
      - Each YAML has required fields: name, steps
      - Each step has: name, agent
      - on-failure is one of: halt, skip, loop
      - If loop, must have loop-target and max-iterations

    Returns:
        List of ValidationResult objects
    """
    results = []
    pipelines_dir = ARCHON_ROOT / "pipelines"

    if not pipelines_dir.exists():
        return results

    valid_on_failure = {"halt", "skip", "loop"}

    for pipeline_file in sorted(pipelines_dir.glob("*.yaml")):
        result = ValidationResult(str(pipeline_file))

        try:
            with open(pipeline_file, 'r', encoding='utf-8') as f:
                pipeline = yaml.safe_load(f)
        except Exception as e:
            result.add_error(f"Failed to parse YAML: {e}")
            results.append(result)
            continue

        if not isinstance(pipeline, dict):
            result.add_error("Pipeline file is not a valid YAML mapping")
            results.append(result)
            continue

        # Required top-level fields
        if 'name' not in pipeline:
            result.add_error("Required field missing: name")
        if 'steps' not in pipeline:
            result.add_error("Required field missing: steps")
            results.append(result)
            continue

        steps = pipeline.get('steps', [])
        if not isinstance(steps, list) or len(steps) == 0:
            result.add_error("steps must be a non-empty list")
            results.append(result)
            continue

        for i, step in enumerate(steps):
            step_label = f"steps[{i}]"
            if not isinstance(step, dict):
                result.add_error(f"{step_label}: step must be a mapping")
                continue

            if 'name' not in step:
                result.add_error(f"{step_label}: Required field missing: name")
            else:
                step_label = f"steps[{i}] ({step['name']})"

            if 'agent' not in step:
                result.add_error(f"{step_label}: Required field missing: agent")

            on_failure = step.get('on-failure')
            if on_failure is not None:
                if on_failure not in valid_on_failure:
                    result.add_error(
                        f"{step_label}: on-failure '{on_failure}' not in {valid_on_failure}"
                    )
                elif on_failure == 'loop':
                    if 'loop-target' not in step:
                        result.add_error(f"{step_label}: on-failure is 'loop' but missing loop-target")
                    if 'max-iterations' not in step:
                        result.add_error(f"{step_label}: on-failure is 'loop' but missing max-iterations")
            else:
                result.add_warning(f"{step_label}: No on-failure strategy defined")

        results.append(result)

    return results


def validate_agent_guardrails() -> List[ValidationResult]:
    """
    Validates agent guardrail structure for all agents.

    Checks:
      - Each agent (except _template) has guardrail-enforcement key
      - guardrails has must-not and must-do
      - Each rule has rule, severity, on-violation
      - severity is one of: critical, major, minor
      - on-violation is one of: halt, warn, log

    Returns:
        List of ValidationResult objects
    """
    results = []
    agents_dir = ARCHON_ROOT / "agents"

    if not agents_dir.exists():
        return results

    valid_severity = {"critical", "major", "minor"}
    valid_on_violation = {"halt", "warn", "log"}

    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.startswith('_'):
            continue

        manifest_path = agent_dir / "agent-manifest.yaml"
        result = ValidationResult(str(agent_dir))

        if not manifest_path.exists():
            result.add_error("agent-manifest.yaml not found")
            results.append(result)
            continue

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            result.add_error(f"Failed to parse YAML: {e}")
            results.append(result)
            continue

        if not isinstance(manifest, dict):
            result.add_error("Agent manifest is not a valid YAML mapping")
            results.append(result)
            continue

        # guardrail-enforcement key
        if 'guardrail-enforcement' not in manifest:
            result.add_error("Missing required key: guardrail-enforcement")

        guardrails = manifest.get('guardrails')
        if guardrails is None:
            result.add_error("Missing required key: guardrails")
            results.append(result)
            continue

        if not isinstance(guardrails, dict):
            result.add_error("guardrails must be a mapping")
            results.append(result)
            continue

        for section_name in ('must-not', 'must-do'):
            section = guardrails.get(section_name)
            if section is None:
                result.add_error(f"guardrails missing required section: {section_name}")
                continue

            if not isinstance(section, list):
                result.add_error(f"guardrails.{section_name} must be a list")
                continue

            for j, rule_entry in enumerate(section):
                rule_label = f"guardrails.{section_name}[{j}]"
                if not isinstance(rule_entry, dict):
                    result.add_error(f"{rule_label}: must be a mapping")
                    continue

                if 'rule' not in rule_entry:
                    result.add_error(f"{rule_label}: Missing required field: rule")
                if 'severity' not in rule_entry:
                    result.add_error(f"{rule_label}: Missing required field: severity")
                elif rule_entry['severity'] not in valid_severity:
                    result.add_error(
                        f"{rule_label}: severity '{rule_entry['severity']}' not in {valid_severity}"
                    )
                if 'on-violation' not in rule_entry:
                    result.add_error(f"{rule_label}: Missing required field: on-violation")
                elif rule_entry['on-violation'] not in valid_on_violation:
                    result.add_error(
                        f"{rule_label}: on-violation '{rule_entry['on-violation']}' not in {valid_on_violation}"
                    )

        results.append(result)

    return results


def validate_synapses() -> List[ValidationResult]:
    """
    Validates synapse structure in the synapses/ directory.

    Checks:
      - Each synapse dir has SYNAPSE.md and manifest.yaml
      - manifest.yaml has name, version, synapse-type
      - Core synapses are registered in archon.yaml

    Returns:
        List of ValidationResult objects
    """
    results = []
    synapses_dir = ARCHON_ROOT / "synapses"

    if not synapses_dir.exists():
        return results

    # Load archon.yaml to check registration
    registered_synapses: Set[str] = set()
    archon_path = ARCHON_ROOT / "archon.yaml"
    if archon_path.exists():
        try:
            with open(archon_path, 'r', encoding='utf-8') as f:
                root_manifest = yaml.safe_load(f)
            for entry in root_manifest.get('synapses', []):
                if isinstance(entry, dict) and 'name' in entry:
                    registered_synapses.add(entry['name'])
        except Exception:
            pass

    for synapse_dir in sorted(synapses_dir.iterdir()):
        if not synapse_dir.is_dir() or synapse_dir.name.startswith('_'):
            continue

        result = ValidationResult(str(synapse_dir))

        # Check required files
        synapse_md = synapse_dir / "SYNAPSE.md"
        manifest_path = synapse_dir / "manifest.yaml"

        if not synapse_md.exists():
            result.add_error("SYNAPSE.md not found")
        if not manifest_path.exists():
            result.add_error("manifest.yaml not found")
            results.append(result)
            continue

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            result.add_error(f"Failed to parse manifest.yaml: {e}")
            results.append(result)
            continue

        if not isinstance(manifest, dict):
            result.add_error("manifest.yaml is not a valid YAML mapping")
            results.append(result)
            continue

        # Required fields
        for field in ('name', 'version', 'synapse-type'):
            if field not in manifest:
                result.add_error(f"Required field missing: {field}")

        # Core synapses must be registered in archon.yaml
        synapse_name = manifest.get('name')
        synapse_type = manifest.get('synapse-type')
        if synapse_type == 'core' and synapse_name and synapse_name not in registered_synapses:
            result.add_error(
                f"Core synapse '{synapse_name}' is not registered in archon.yaml"
            )

        results.append(result)

    return results


def validate_hooks() -> List[ValidationResult]:
    """
    Validates the hook system.

    Checks:
      - hooks.yaml exists and is valid YAML
      - Each referenced hook .py file exists
      - Each hook file has an execute() function

    Returns:
        List of ValidationResult objects
    """
    results = []
    hooks_yaml_path = ARCHON_ROOT / "hooks" / "hooks.yaml"
    result = ValidationResult(str(hooks_yaml_path))

    if not hooks_yaml_path.exists():
        result.add_error("hooks/hooks.yaml not found")
        results.append(result)
        return results

    try:
        with open(hooks_yaml_path, 'r', encoding='utf-8') as f:
            hooks_config = yaml.safe_load(f)
    except Exception as e:
        result.add_error(f"Failed to parse hooks.yaml: {e}")
        results.append(result)
        return results

    if not isinstance(hooks_config, dict):
        result.add_error("hooks.yaml is not a valid YAML mapping")
        results.append(result)
        return results

    hooks = hooks_config.get('hooks', {})
    if not isinstance(hooks, dict):
        result.add_error("hooks.yaml 'hooks' key must be a mapping")
        results.append(result)
        return results

    import ast

    for hook_name, hook_def in hooks.items():
        if not isinstance(hook_def, dict):
            result.add_error(f"Hook '{hook_name}': definition must be a mapping")
            continue

        handler_path_str = hook_def.get('handler')
        if not handler_path_str:
            result.add_error(f"Hook '{hook_name}': missing 'handler' field")
            continue

        handler_path = ARCHON_ROOT / handler_path_str
        if not handler_path.exists():
            result.add_error(f"Hook '{hook_name}': handler file not found: {handler_path_str}")
            continue

        # Check for execute() function via AST parsing
        try:
            source = handler_path.read_text(encoding='utf-8')
            tree = ast.parse(source)
            func_names = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ]
            if 'execute' not in func_names:
                result.add_error(
                    f"Hook '{hook_name}': handler {handler_path_str} missing execute() function"
                )
        except SyntaxError as e:
            result.add_error(f"Hook '{hook_name}': syntax error in {handler_path_str}: {e}")

    results.append(result)
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Archon skills, bundles, pipelines, agents, synapses, and hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate.py --all                    # Validate everything
  python validate.py skills/godot-gdscript    # Validate specific skill
  python validate.py --skills                 # Validate all skills
  python validate.py --bundles                # Validate all bundles
  python validate.py --pipelines              # Validate all pipelines
  python validate.py --agents                 # Validate agent guardrails
  python validate.py --synapses               # Validate all synapses
  python validate.py --hooks                  # Validate hook system
        """
    )
    
    parser.add_argument('path', nargs='?', help='Path to validate (skill or bundle directory)')
    parser.add_argument('--all', action='store_true', help='Validate everything')
    parser.add_argument('--skills', action='store_true', help='Validate all skills')
    parser.add_argument('--bundles', action='store_true', help='Validate all bundles')
    parser.add_argument('--pipelines', action='store_true', help='Validate all pipelines')
    parser.add_argument('--agents', action='store_true', help='Validate agent guardrails')
    parser.add_argument('--synapses', action='store_true', help='Validate all synapses')
    parser.add_argument('--hooks', action='store_true', help='Validate hook system')
    parser.add_argument('--check-triggers', action='store_true', help='Check for duplicate triggers')
    parser.add_argument('--check-llms-txt', action='store_true', help='Check if llms.txt files are up to date')
    
    args = parser.parse_args()
    
    results = []
    
    if args.all:
        print("🔍 Validating all skills, bundles, pipelines, agents, synapses, and hooks...\n")
        results.extend(validate_all_skills())
        results.extend(validate_all_bundles())
        results.extend(validate_pipelines())
        results.extend(validate_agent_guardrails())
        results.extend(validate_synapses())
        results.extend(validate_hooks())
        
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
    
    elif args.pipelines:
        print("🔍 Validating all pipelines...\n")
        results.extend(validate_pipelines())
    
    elif args.agents:
        print("🔍 Validating agent guardrails...\n")
        results.extend(validate_agent_guardrails())
    
    elif args.synapses:
        print("🔍 Validating all synapses...\n")
        results.extend(validate_synapses())
    
    elif args.hooks:
        print("🔍 Validating hook system...\n")
        results.extend(validate_hooks())
    
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
    
    elif args.check_llms_txt and not args.path:
        # Standalone llms.txt check (no other validation)
        return check_llms_txt_freshness()
    
    elif args.path:
        path = Path(args.path)
        
        if not path.is_absolute():
            path = ARCHON_ROOT / path
        
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
    
    # llms.txt freshness check
    if args.check_llms_txt:
        print("\n" + "=" * 60)
        print("llms.txt FRESHNESS CHECK")
        print("=" * 60)
        llms_result = check_llms_txt_freshness()
        if llms_result != 0:
            return llms_result
    
    return 0 if failed == 0 else 1


def check_llms_txt_freshness() -> int:
    """Check if llms.txt files are up to date. Returns 0 if fresh, 1 if stale."""
    import re
    from datetime import date

    stale = False

    # Try the archon package first
    try:
        from archon.core.llms_txt import generate_concise, generate_full

        for filename, gen_fn in [("llms.txt", generate_concise), ("llms-full.txt", generate_full)]:
            file_path = ARCHON_ROOT / filename
            if not file_path.exists():
                print(f"⚠️  {filename} not found — generate with: archon generate llms-txt")
            else:
                expected = gen_fn(ARCHON_ROOT)
                actual = file_path.read_text(encoding="utf-8")
                if filename == "llms-full.txt":
                    expected_cmp = re.sub(r"^- Generated: .+$", "", expected, count=1, flags=re.MULTILINE)
                    actual_cmp = re.sub(r"^- Generated: .+$", "", actual, count=1, flags=re.MULTILINE)
                else:
                    expected_cmp = expected
                    actual_cmp = actual
                if expected_cmp == actual_cmp:
                    print(f"✅ {filename} is up to date")
                else:
                    print(f"⚠️  {filename} is stale — regenerate with: archon generate llms-txt")
                    stale = True
    except ImportError:
        # Fallback: use the generate script's fallback
        try:
            sys.path.insert(0, str(ARCHON_ROOT / "scripts"))
            from importlib import import_module
            gen_mod_path = ARCHON_ROOT / "scripts" / "generate-llms-txt.py"
            # Can't easily import with hyphens; just check file existence
            for filename in ("llms.txt", "llms-full.txt"):
                file_path = ARCHON_ROOT / filename
                if not file_path.exists():
                    print(f"⚠️  {filename} not found — generate with: python scripts/generate-llms-txt.py")
                else:
                    print(f"ℹ️  {filename} exists (install archon package for full freshness check)")
        except Exception:
            print("⚠️  Could not perform llms.txt freshness check")

    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
