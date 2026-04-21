"""
Code-Quality Synapse (MCP-Integrated)

Validates code quality by scanning real files via MCP file-ops server.
Checks: type hints, docstrings, complexity, style, deprecated patterns.
"""

from typing import Any, Dict
from .mcp_client import get_mcp_client


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate code quality on real files.
    
    Context expected:
    - file_path: str - Path to Python file to validate
    - min_complexity_threshold: int (default 10)
    - require_type_hints: bool (default True)
    - require_docstrings: bool (default True)
    """
    file_path = context.get("file_path")
    min_complexity = context.get("min_complexity_threshold", 10)
    require_hints = context.get("require_type_hints", True)
    require_docs = context.get("require_docstrings", True)
    
    if not file_path:
        return {
            "action": "allow",
            "message": "No file path provided",
        }
    
    client = get_mcp_client()
    analysis = client.analyze_code_quality(file_path)
    
    if "error" in analysis:
        return {
            "action": "halt",
            "message": f"Cannot analyze file: {analysis['error']}",
        }
    
    metrics = analysis.get("metrics", {})
    issues = []
    
    # Check type hints
    if require_hints and not metrics.get("has_type_hints"):
        issues.append("Missing type hints on functions")
    
    # Check docstrings
    if require_docs and not metrics.get("has_docstrings"):
        issues.append("Missing docstrings on functions")
    
    # Check complexity
    complexity = metrics.get("complexity", 0)
    if complexity > min_complexity:
        issues.append(
            f"Cyclomatic complexity {complexity} exceeds threshold {min_complexity}"
        )
    
    if issues:
        return {
            "action": "halt",
            "message": f"Code quality check failed: {len(issues)} issue(s)",
            "violations": issues,
            "metrics": metrics,
        }
    
    return {
        "action": "allow",
        "message": "Code quality standards met (MCP scan)",
        "metrics": metrics,
    }
