"""Security awareness synapse — OWASP Top-10 pattern scan.

Returns a plain dict for backwards compatibility with the synapse module interface.
The synapse_engine_v2.py has the SynapseDecision-based version used at runtime.
"""

import re

# OWASP Top-10 patterns (A1-A10), mirroring synapse_engine_v2._OWASP_PATTERNS
_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    # A1 — Injection
    (re.compile(r'\bexec\s*\(|(?<!\w)eval\s*\(', re.I), "CRITICAL", "A1-Injection: exec/eval (RCE risk)"),
    (re.compile(r'subprocess\.(call|run|Popen)\s*\([^,)]*\+', re.I), "HIGH", "A1-Injection: dynamic subprocess call"),
    (re.compile(r'(?:query|execute|cursor\.execute)\s*\([^)]*\+[^)]*\)', re.I), "HIGH", "A1-Injection: possible SQL concatenation"),
    # A2 — Broken Authentication
    (re.compile(r"(?:password|passwd|pwd|secret|token|api_?key)\s*[=:]\s*[\"'][^\"']{6,}[\"']", re.I), "CRITICAL", "A2-Auth: hardcoded credential"),
    (re.compile(r'jwt\.decode\s*\([^)]*verify\s*=\s*False', re.I), "CRITICAL", "A2-Auth: JWT verification disabled"),
    # A3 — XSS
    (re.compile(r'\.innerHTML\s*[+]?=|document\.write\s*\(', re.I), "HIGH", "A3-XSS: raw HTML injection"),
    (re.compile(r'dangerouslySetInnerHTML', re.I), "HIGH", "A3-XSS: React dangerouslySetInnerHTML"),
    # A4 — Path traversal
    (re.compile(r'open\s*\([^)]*\+[^)]*\)|Path\s*\([^)]*\+[^)]*\)', re.I), "HIGH", "A4-IDOR: dynamic path construction"),
    # A5 — Security Misconfiguration
    (re.compile(r'ssl\._create_unverified_context|verify\s*=\s*False.*requests\.|VERIFY_SSL\s*=\s*False', re.I), "HIGH", "A5-Misconfig: SSL verification disabled"),
    (re.compile(r'DEBUG\s*=\s*True|debug\s*=\s*True', re.I), "MEDIUM", "A5-Misconfig: debug mode enabled"),
    # A7 — Broken Access Control
    (re.compile(r'os\.chmod\s*\([^,]+,\s*0o?777\)', re.I), "HIGH", "A7-Access: chmod 777"),
    # A9 — Deserialization
    (re.compile(r'pickle\.loads?\s*\(', re.I), "HIGH", "A9-Deserialization: unsafe pickle"),
    # A10 — SSRF
    (re.compile(r'requests\.(get|post|put|delete)\s*\([^)]*user[_-]?input|fetch\s*\([^)]*req\.(body|params|query)', re.I), "HIGH", "A10-SSRF: user-controlled URL"),
]


def validate(context: dict) -> dict:
    """Scan code/text for OWASP Top-10 security vulnerabilities.

    Args:
        context: dict with a 'code' key (or 'text'/'content' fallback)

    Returns:
        {"action": "halt"|"allow", "message": str, "vulnerabilities": list[str]}
    """
    code = context.get("code") or context.get("text") or context.get("content", "")
    vulns: list[str] = []
    has_critical = False

    for pattern, severity, label in _PATTERNS:
        if pattern.search(code):
            vulns.append(f"{severity}: {label}")
            if severity == "CRITICAL":
                has_critical = True

    if vulns:
        action = "halt" if has_critical else "warn"
        return {
            "action": action,
            "message": f"Security scan: {len(vulns)} issue(s) found ({action.upper()})",
            "vulnerabilities": vulns,
        }

    return {"action": "allow", "message": "Security scan: no issues found", "vulnerabilities": []}
