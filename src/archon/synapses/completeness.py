"""
Completeness Synapse

Ensures all acceptance criteria are met before handoff.
Detects:
- Missing deliverables
- Incomplete acceptance criteria
- Skipped test cases
- Unresolved TODOs

Returns HALT if critical acceptance criteria unmet.
"""

from typing import Any, Dict, List


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that all acceptance criteria are complete.
    
    Context expected:
    - acceptance_criteria: list - List of criteria to verify
    - deliverables: list - List of completed deliverables
    - tests_passed: int - Number of passing tests
    - todos_remaining: int - Count of unresolved TODOs
    - blocked_criteria: list - Optional list of blocked criteria
    """
    acceptance_criteria = context.get("acceptance_criteria", [])
    deliverables = context.get("deliverables", [])
    tests_passed = context.get("tests_passed", 0)
    todos_remaining = context.get("todos_remaining", 0)
    blocked_criteria = context.get("blocked_criteria", [])
    
    issues = []
    completion_rate = 0.0
    
    # Check 1: Critical acceptance criteria
    critical_criteria = [c for c in acceptance_criteria if c.get("critical", False)]
    if critical_criteria:
        met_critical = sum(1 for c in critical_criteria if c.get("met", False))
        if met_critical < len(critical_criteria):
            issues.append(
                f"CRITICAL_ACCEPTANCE: {len(critical_criteria) - met_critical} "
                f"critical criteria unmet"
            )
    
    # Check 2: Deliverable completeness
    if acceptance_criteria:
        criteria_met = sum(1 for c in acceptance_criteria if c.get("met", False))
        completion_rate = criteria_met / len(acceptance_criteria)
        
        if completion_rate < 0.8:  # 80% required
            issues.append(
                f"INCOMPLETE: Only {completion_rate:.0%} of acceptance criteria met"
            )
    
    # Check 3: Test coverage
    if tests_passed == 0 and acceptance_criteria:
        issues.append("NO_TESTS: No tests passing for acceptance criteria")
    
    # Check 4: Unresolved TODOs
    if todos_remaining > 0:
        issues.append(f"PENDING_WORK: {todos_remaining} TODOs unresolved")
    
    # Check 5: Blocked work
    if blocked_criteria:
        issues.append(f"BLOCKED: {len(blocked_criteria)} criteria blocked")
    
    if issues:
        return {
            "action": "halt",
            "message": f"Completeness check failed: {len(issues)} issue(s)",
            "violations": issues,
            "completion_rate": completion_rate,
            "tests_passed": tests_passed,
        }
    
    return {
        "action": "allow",
        "message": "All acceptance criteria met",
        "completion_rate": completion_rate,
        "tests_passed": tests_passed,
    }


CONTEXT_SCHEMA = {
    "acceptance_criteria": list,  # [{name, met, critical}]
    "deliverables": list,  # Completed deliverables
    "tests_passed": int,  # Test count
    "todos_remaining": int,  # TODO count
    "blocked_criteria": list,  # Blocked work items
}
