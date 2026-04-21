import re

def validate(context):
    code = context.get("code", "")
    vulns = []
    if "exec(" in code or "eval(" in code:
        vulns.append("CRITICAL: exec/eval")
    if "innerHTML =" in code or "innerHTML=" in code:
        vulns.append("HIGH: innerHTML XSS")
    if "password" in code.lower() and ("=" in code):
        vulns.append("CRITICAL: Hardcoded password")
    if vulns:
        return {"action": "halt", "message": f"Security issues: {len(vulns)}", "vulnerabilities": vulns}
    return {"action": "allow", "message": "Secure", "vulnerabilities": []}
