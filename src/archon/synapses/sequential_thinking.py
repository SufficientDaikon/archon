"""
Sequential-Thinking Synapse

Ensures reasoning follows logical progression:
- No logical gaps
- Proper step ordering
- Evidence-to-claim linkage
- No circular reasoning

Returns HALT if reasoning has critical gaps.
"""

from typing import Any, Dict, List


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify sequential thinking integrity.
    
    Context expected:
    - steps: list - Reasoning steps in order
    - claims: list - Claims made during reasoning
    - evidence: list - Evidence provided
    - dependencies: dict - Step dependencies
    """
    steps = context.get("steps", [])
    claims = context.get("claims", [])
    evidence = context.get("evidence", [])
    dependencies = context.get("dependencies", {})
    
    issues = []
    
    # Check 1: Logical gaps
    if steps:
        for i, step in enumerate(steps):
            if i > 0 and ("because" not in str(step).lower() and 
                         "thus" not in str(step).lower()):
                issues.append(f"LOGIC_GAP: Step {i} not connected to prior reasoning")
    
    # Check 2: Step ordering via dependencies
    processed = set()
    for step_id, depends_on in dependencies.items():
        if depends_on and depends_on not in processed:
            issues.append(
                f"ORDERING: Step {step_id} requires {depends_on} but processed in wrong order"
            )
        processed.add(step_id)
    
    # Check 3: Circular reasoning detection
    visited = set()
    
    def has_cycle(node, path):
        if node in path:
            return True
        if node in visited:
            return False
        visited.add(node)
        deps = dependencies.get(node, [])
        if isinstance(deps, str):
            deps = [deps]
        for dep in deps:
            if has_cycle(dep, path + [node]):
                return True
        return False
    
    for step_id in dependencies:
        if has_cycle(step_id, []):
            issues.append(f"CIRCULAR: Circular reasoning detected involving {step_id}")
            break
    
    # Check 4: Claim-evidence linkage
    if claims and not evidence:
        issues.append("UNSUPPORTED: Claims made without supporting evidence")
    
    if issues:
        return {
            "action": "halt",
            "message": f"Sequential thinking check failed: {len(issues)} issue(s)",
            "violations": issues,
            "steps_analyzed": len(steps),
        }
    
    return {
        "action": "allow",
        "message": "Sequential thinking verified",
        "steps_analyzed": len(steps),
    }


CONTEXT_SCHEMA = {
    "steps": list,  # Reasoning steps in order
    "claims": list,  # Claims made
    "evidence": list,  # Supporting evidence
    "dependencies": dict,  # {step_id: required_prior_step}
}
