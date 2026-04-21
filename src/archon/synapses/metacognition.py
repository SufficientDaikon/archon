"""
Metacognition Synapse

Enforces self-awareness before execution. Detects:
- Missing plans for complex tasks
- Insufficient reasoning depth for the stated complexity tier
- Premature action without reflection
- Mismatches between stated confidence and actual evidence

Returns HALT when the agent proceeds without appropriate planning or
reasoning for the complexity level declared.
"""

from typing import Any, Dict

# Complexity tiers that require a plan before acting
_PLAN_REQUIRED_TIERS = {"MODERATE", "COMPLEX", "EXPERT"}

# Minimum reasoning length (chars) per tier — below this is shallow
_MIN_REASONING_LENGTH: Dict[str, int] = {
    "TRIVIAL": 0,
    "SIMPLE": 30,
    "MODERATE": 100,
    "COMPLEX": 250,
    "EXPERT": 500,
}

# Reflection markers — at least one should appear in reasoning for COMPLEX+
_REFLECTION_MARKERS = (
    "because", "therefore", "however", "alternatively", "trade-off",
    "consider", "risk", "assumption", "verify", "investigate",
)


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforce metacognitive quality before execution.

    Context expected:
    - complexity: str - Task tier (TRIVIAL|SIMPLE|MODERATE|COMPLEX|EXPERT)
    - has_plan: bool - Whether a structured plan exists before acting
    - reasoning: str - The agent's stated reasoning for the approach
    - confidence: float (0-1) - Agent's stated confidence level
    - evidence_count: int - Number of evidence items supporting the approach
    """
    complexity = context.get("complexity", "SIMPLE").upper()
    has_plan = context.get("has_plan", False)
    reasoning = context.get("reasoning", "")
    confidence = context.get("confidence", 1.0)
    evidence_count = context.get("evidence_count", 0)

    issues = []

    # Check 1: Plan required for non-trivial tasks
    if complexity in _PLAN_REQUIRED_TIERS and not has_plan:
        issues.append(
            f"NO_PLAN: Task tier is {complexity} but no plan was produced. "
            "Decompose the task before executing."
        )

    # Check 2: Reasoning depth matches complexity
    min_length = _MIN_REASONING_LENGTH.get(complexity, 0)
    if len(reasoning) < min_length:
        issues.append(
            f"SHALLOW_REASONING: {complexity} task requires at least "
            f"{min_length} chars of reasoning, got {len(reasoning)}."
        )

    # Check 3: Reflection markers present for COMPLEX/EXPERT
    if complexity in {"COMPLEX", "EXPERT"}:
        has_reflection = any(marker in reasoning.lower() for marker in _REFLECTION_MARKERS)
        if not has_reflection:
            issues.append(
                "NO_REFLECTION: COMPLEX/EXPERT tasks must show trade-off analysis "
                "or explicit consideration of alternatives in reasoning."
            )

    # Check 4: Confidence calibration — high confidence needs evidence
    if confidence > 0.9 and evidence_count == 0:
        issues.append(
            f"OVERCONFIDENT: Stated confidence {confidence:.0%} with no evidence items. "
            "Either lower confidence or supply evidence."
        )

    if issues:
        return {
            "action": "halt",
            "message": f"Metacognition check failed: {len(issues)} issue(s)",
            "violations": issues,
            "complexity": complexity,
            "has_plan": has_plan,
        }

    return {
        "action": "allow",
        "message": "Metacognition check passed",
        "complexity": complexity,
        "has_plan": has_plan,
    }


CONTEXT_SCHEMA = {
    "complexity": str,       # Task tier: TRIVIAL|SIMPLE|MODERATE|COMPLEX|EXPERT
    "has_plan": bool,        # Whether a plan exists before acting
    "reasoning": str,        # Agent's reasoning for the approach
    "confidence": float,     # Agent's stated confidence (0-1)
    "evidence_count": int,   # Supporting evidence items count
}
