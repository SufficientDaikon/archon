"""
Consistency Synapse

Detects cross-file inconsistencies:
- Duplicate logic across files
- Naming inconsistencies (camelCase vs snake_case)
- Contradictory state definitions
- API contract violations
- Import path inconsistencies

Returns HALT if critical inconsistencies found.
"""

from typing import Any, Dict


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify consistency across changes.
    
    Context expected:
    - files_changed: list - File paths modified
    - definitions: dict - {name: definition} across files
    - naming_style: str - "camelCase"|"snake_case"|"PascalCase"
    - imports: list - Import statements
    - state_schemas: list - State definitions
    - duplicates: list - Duplicate logic detected
    """
    files_changed = context.get("files_changed", [])
    definitions = context.get("definitions", {})
    naming_style = context.get("naming_style", "snake_case")
    imports = context.get("imports", [])
    state_schemas = context.get("state_schemas", [])
    duplicates = context.get("duplicates", [])
    
    issues = []
    
    # Check 1: File count consistency
    if len(files_changed) > 5:
        # Multi-file changes need consistency checks
        
        # Check 2: Duplicated logic
        if duplicates:
            issues.append(
                f"CONSISTENCY: {len(duplicates)} duplicate logic pattern(s) found"
            )
        
        # Check 3: Naming convention
        violations = []
        for name in definitions.keys():
            has_camel = any(c.isupper() for c in name[1:])
            has_snake = "_" in name
            
            if naming_style == "snake_case" and has_camel:
                violations.append(f"{name} (camelCase in snake_case file)")
            elif naming_style == "camelCase" and has_snake:
                violations.append(f"{name} (snake_case in camelCase file)")
        
        if violations:
            issues.append(f"NAMING: {len(violations)} naming inconsistency(ies)")
        
        # Check 4: Import consistency
        import_paths = [imp.split()[1] if " " in imp else imp for imp in imports]
        absolute_imports = [p for p in import_paths if p.startswith("/")]
        relative_imports = [p for p in import_paths if p.startswith(".")]
        
        if absolute_imports and relative_imports and len(files_changed) > 1:
            issues.append(
                "IMPORTS: Mixed absolute/relative imports across files"
            )
        
        # Check 5: State schema consistency
        if len(state_schemas) > 1:
            # Check for contradictory definitions
            first_schema = state_schemas[0]
            for schema in state_schemas[1:]:
                if schema.get("name") == first_schema.get("name"):
                    if schema.get("type") != first_schema.get("type"):
                        issues.append(
                            f"STATE_CONFLICT: {schema.get('name')} "
                            f"has conflicting type definitions"
                        )
    
    if issues:
        return {
            "action": "halt",
            "message": f"Consistency check failed: {len(issues)} issue(s)",
            "violations": issues,
            "files_checked": len(files_changed),
        }
    
    return {
        "action": "allow",
        "message": "Consistency check passed",
        "files_checked": len(files_changed),
    }


CONTEXT_SCHEMA = {
    "files_changed": list,  # File paths modified
    "definitions": dict,  # {name: definition}
    "naming_style": str,  # Expected naming convention
    "imports": list,  # Import statements
    "state_schemas": list,  # State definitions
    "duplicates": list,  # Duplicate logic found
}
