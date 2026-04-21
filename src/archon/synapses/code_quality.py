"""
Code-Quality Synapse

Enforces code quality standards:
- Type hints present
- Docstrings complete
- Style adherence (PEP 8)
- Cyclomatic complexity acceptable
- No deprecated patterns

Returns HALT if critical quality thresholds breached.
"""

from typing import Any, Dict


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify code meets quality standards.
    
    Context expected:
    - code: str - Code to validate
    - has_type_hints: bool - Type hints present
    - has_docstrings: bool - Docstrings present
    - pylint_score: float - Pylint score (0-10)
    - cyclomatic_complexity: int - CC metric
    - deprecated_patterns: list - Found deprecated usage
    - min_score: float - Minimum acceptable (default 7.0)
    """
    code = context.get("code", "")
    has_type_hints = context.get("has_type_hints", False)
    has_docstrings = context.get("has_docstrings", False)
    pylint_score = context.get("pylint_score", 10.0)
    cyclomatic_complexity = context.get("cyclomatic_complexity", 0)
    deprecated_patterns = context.get("deprecated_patterns", [])
    min_score = context.get("min_score", 7.0)
    
    issues = []
    
    # Check 1: Type hints
    if not has_type_hints and code:
        issues.append("QUALITY: Missing type hints on public functions")
    
    # Check 2: Docstrings
    if not has_docstrings and code and len(code) > 100:
        issues.append("QUALITY: Missing docstrings on complex functions")
    
    # Check 3: Pylint score
    if pylint_score < min_score:
        issues.append(
            f"QUALITY: Pylint score {pylint_score:.1f} below minimum {min_score:.1f}"
        )
    
    # Check 4: Cyclomatic complexity
    if cyclomatic_complexity > 10:
        issues.append(
            f"COMPLEXITY: Cyclomatic complexity {cyclomatic_complexity} exceeds threshold (10)"
        )
    
    # Check 5: Deprecated patterns
    if deprecated_patterns:
        issues.append(
            f"DEPRECATED: {len(deprecated_patterns)} deprecated pattern(s) found"
        )
    
    if issues:
        return {
            "action": "halt",
            "message": f"Code quality check failed: {len(issues)} issue(s)",
            "violations": issues,
            "score": pylint_score,
        }
    
    return {
        "action": "allow",
        "message": "Code quality standards met",
        "score": pylint_score,
    }


CONTEXT_SCHEMA = {
    "code": str,  # Code content to validate
    "has_type_hints": bool,  # Type hints present
    "has_docstrings": bool,  # Docstrings present
    "pylint_score": float,  # Quality score 0-10
    "cyclomatic_complexity": int,  # CC metric
    "deprecated_patterns": list,  # Deprecated usage found
    "min_score": float,  # Minimum acceptable score
}
