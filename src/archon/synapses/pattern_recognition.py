"""
Pattern-Recognition Synapse

Identifies recurrent issues across executions:
- Repeated error patterns
- Similar decision points
- Common failure modes
- Reusable solutions

Returns HALT if dangerous pattern detected.
"""

from typing import Any, Dict, List


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect dangerous or inefficient patterns.
    
    Context expected:
    - execution_history: list - Prior executions
    - current_action: str - Proposed action
    - error_patterns: list - Known error patterns
    - failure_threshold: int - Max repeats before halt (default 3)
    """
    execution_history = context.get("execution_history", [])
    current_action = context.get("current_action", "")
    error_patterns = context.get("error_patterns", [])
    failure_threshold = context.get("failure_threshold", 3)
    
    issues = []
    
    # Check 1: Repeated error pattern
    if execution_history and error_patterns:
        similar_errors = 0
        for error_pattern in error_patterns:
            pattern_str = str(error_pattern).lower()
            matches = sum(
                1 for exec_record in execution_history
                if pattern_str in str(exec_record).lower()
            )
            if matches >= failure_threshold:
                issues.append(
                    f"PATTERN: Error pattern repeated {matches} times "
                    f"(threshold: {failure_threshold})"
                )
                similar_errors += 1
    
    # Check 2: Same action attempted too many times
    if execution_history and current_action:
        action_count = sum(
            1 for record in execution_history
            if pd_normalize_action(record.get("action", "")) 
            == pd_normalize_action(current_action)
        )
        if action_count >= failure_threshold:
            issues.append(
                f"LOOP_DETECTION: Attempting same action {action_count} times "
                "(retry limit exceeded)"
            )
    
    if issues:
        return {
            "action": "halt",
            "message": f"Pattern detection halted: {len(issues)} issue(s)",
            "violations": issues,
            "history_depth": len(execution_history),
        }
    
    return {
        "action": "allow",
        "message": "Pattern check passed",
        "history_depth": len(execution_history),
    }


def pd_normalize_action(action: str) -> str:
    """Normalize action string for comparison."""
    return str(action).lower().strip()


CONTEXT_SCHEMA = {
    "execution_history": list,  # Prior executions
    "current_action": str,  # Proposed action
    "error_patterns": list,  # Known error patterns
    "failure_threshold": int,  # Max repeats before halt
}
