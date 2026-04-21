"""
Trust-Verification Synapse

Verifies that reasoning claims are backed by evidence. Detects:
- Unsupported assertions
- Contradictions with prior state
- Missing evidence chains

Returns HALT if critical claims lack evidence.
"""

import re
from typing import Any, Dict


# Negation markers used to detect contradictions
_NEGATION_PATTERNS = re.compile(
    r"\b(not|no|never|don'?t|doesn'?t|won'?t|can'?t|cannot|avoid|skip|ignore)\b",
    re.IGNORECASE,
)

# Phrases that signal strong, unqualified commitments
_CRITICAL_PHRASES = ("must", "always", "never", "definitely", "guaranteed")


def _extract_key_terms(text: str) -> set[str]:
    """Return a set of meaningful content words (3+ chars, alpha only)."""
    stopwords = {"the", "and", "for", "that", "this", "with", "from", "are", "was"}
    return {
        w.lower()
        for w in re.findall(r"\b[a-zA-Z]{3,}\b", text)
        if w.lower() not in stopwords
    }


def _contradicts(reasoning: str, prior_text: str) -> bool:
    """
    Return True if current reasoning contradicts a prior decision.

    Heuristic: if the prior decision asserts something and the current
    reasoning negates it (or vice-versa), flag as contradiction.
    """
    reasoning_negated = bool(_NEGATION_PATTERNS.search(reasoning))
    prior_negated = bool(_NEGATION_PATTERNS.search(prior_text))

    if reasoning_negated == prior_negated:
        return False  # Both positive or both negative — no direct contradiction

    # Check for shared key terms — contradiction only matters if they talk about
    # the same subject
    shared_terms = _extract_key_terms(reasoning) & _extract_key_terms(prior_text)
    return len(shared_terms) >= 2  # At least 2 shared terms to avoid false positives


def validate(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify reasoning against available evidence.

    Context expected:
    - reasoning: str - Agent's stated reasoning
    - evidence: list - Available supporting evidence
    - prior_state: dict - Previous decisions/state
    - confidence_threshold: float (0-1, default 0.7)
    """
    reasoning = context.get("reasoning", "").lower()
    evidence = context.get("evidence", [])
    prior_state = context.get("prior_state", {})
    confidence_threshold = context.get("confidence_threshold", 0.7)

    issues = []

    # Check 1: Critical claims without evidence
    has_critical = any(phrase in reasoning for phrase in _CRITICAL_PHRASES)
    if has_critical and not evidence:
        issues.append("CRITICAL: Strong claim made without supporting evidence")

    # Check 2: Contradictions with prior decisions
    if prior_state:
        prior_decisions = prior_state.get("decisions", [])
        for prior in prior_decisions:
            prior_text = str(prior)
            if _contradicts(reasoning, prior_text):
                summary = prior_text[:80].replace("\n", " ")
                issues.append(
                    f"CONTRADICTION: Current reasoning conflicts with prior decision: '{summary}...'"
                )

    # Check 3: Evidence chain completeness
    confidence = len(evidence) / max(1, len(evidence) + 2)
    if confidence < confidence_threshold and has_critical:
        issues.append(
            f"CONFIDENCE_LOW: Assertion confidence {confidence:.1%} below {confidence_threshold:.0%}"
        )

    if issues:
        return {
            "action": "halt",
            "message": f"Trust verification failed: {len(issues)} issue(s)",
            "violations": issues,
            "confidence": confidence,
        }

    return {
        "action": "allow",
        "message": "Trust verification passed",
        "confidence": confidence,
    }


CONTEXT_SCHEMA = {
    "reasoning": str,      # Agent's stated reasoning/claim
    "evidence": list,      # List of supporting evidence items
    "prior_state": dict,   # Prior decisions and state
    "confidence_threshold": float,  # Min confidence required (0-1)
}
