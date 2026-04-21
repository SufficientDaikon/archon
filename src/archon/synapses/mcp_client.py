"""MCP client for file-ops integration into synapses."""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class MCPFileOpsClient:
    """Client for file-ops MCP server."""
    
    def __init__(self, server_path: str = "C:/Users/tahaa/omniskill/servers/file-ops/server.py"):
        self.server_path = server_path
        self.process = None
    
    def read_file(self, path: str) -> Optional[Dict[str, Any]]:
        """Read file via MCP."""
        try:
            if not Path(path).exists():
                return {"error": "File not found", "path": path}
            
            lines = Path(path).read_text().splitlines()
            return {
                "path": path,
                "content": "\n".join(lines),
                "lines": len(lines),
                "language": self._detect_language(path)
            }
        except Exception as e:
            return {"error": str(e), "path": path}
    
    def analyze_code_quality(self, path: str) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        file_info = self.read_file(path)
        if "error" in file_info:
            return file_info
        
        content = file_info.get("content", "")
        
        return {
            "path": path,
            "metrics": {
                "has_type_hints": ":" in content and "->" in content,
                "has_docstrings": "def " in content and "\n    " in content,
                "line_count": file_info.get("lines", 0),
                "complexity": self._estimate_complexity(content),
                "has_imports": "import " in content
            }
        }
    
    def scan_security(self, path: str) -> Dict[str, Any]:
        """Scan for security issues."""
        file_info = self.read_file(path)
        if "error" in file_info:
            return file_info
        
        content = file_info.get("content", "").lower()
        issues = []
        
        dangerous_patterns = [
            ("exec(", "Code execution via exec()"),
            ("eval(", "Code execution via eval()"),
            ("__import__", "Dynamic imports"),
            ("password =", "Hardcoded password"),
            ("api_key =", "Hardcoded API key"),
        ]
        
        for pattern, issue in dangerous_patterns:
            if pattern in content:
                issues.append(issue)
        
        return {
            "path": path,
            "secure": len(issues) == 0,
            "issues": issues
        }
    
    def _detect_language(self, path: str) -> str:
        """Detect language from extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go"
        }
        return ext_map.get(Path(path).suffix, "unknown")
    
    def _estimate_complexity(self, content: str) -> int:
        """Estimate cyclomatic complexity."""
        keywords = ["if ", "elif ", "except ", "for ", "while "]
        return sum(content.count(kw) for kw in keywords) + 1


# Global singleton
_client = None


def get_mcp_client() -> MCPFileOpsClient:
    """Get or create MCP client."""
    global _client
    if _client is None:
        _client = MCPFileOpsClient()
    return _client
