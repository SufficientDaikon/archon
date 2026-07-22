"""Synapse validators — the single implementation of every Archon synapse check.

Each module exposes ``validate(context: dict) -> dict`` returning
``{"action": "allow"|"warn"|"halt", "message": str, ...evidence keys}``.
They are wired into the runtime via
:func:`archon.core.synapse_engine_v2.build_default_engine`, which wraps each
one in a SynapseDecision adapter.
"""

from . import (
    anti_rationalization,
    code_quality,
    completeness,
    consistency,
    metacognition,
    pattern_recognition,
    security_awareness,
    sequential_thinking,
    trust_verification,
)

__all__ = [
    "anti_rationalization",
    "code_quality",
    "completeness",
    "consistency",
    "metacognition",
    "pattern_recognition",
    "security_awareness",
    "sequential_thinking",
    "trust_verification",
]
