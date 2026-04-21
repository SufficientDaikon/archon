"""
Security-Awareness Synapse (MCP-Integrated)

Validates security by scanning real files via MCP.
Detects: exec/eval, hardcoded credentials, dangerous patterns.
"""

from typing import Any, Dict
from .mcp_client import get_mcp_client


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate security on real files.
    
    Context expected:
    - file_path: str - Path to file to scan
    - strict_mode: bool (default False) - Halt on any issue
    """
    file_path = context.get("file_path")
    strict_mode = context.get("strict_mode", False)
    
    if not file_path:
        return {
            "action": "allow",
            "message": "No file path provided",
        }
    
    client = get_mcp_client()
    scan = client.scan_security(file_path)
    
    if "error" in scan:
        return {
            "action": "halt",
            "message": f"Cannot scan file: {scan['error']}",
        }
    
    issues = scan.get("issues", [])
    
    if issues:
        return {
            "action": "halt" if strict_mode else "warn",
            "message": f"Security issues detected: {len(issues)} issue(s)",
            "vulnerabilities": issues,
            "file_path": file_path,
        }
    
    return {
        "action": "allow",
        "message": "No security issues detected (MCP scan)",
        "file_path": file_path,
    }
