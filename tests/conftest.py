"""pytest configuration and fixtures for Archon synapses."""

import pytest
import sys

sys.path.insert(0, "C:/Users/tahaa/omniskill/src")

from archon.synapses import (
    anti_rationalization,
    security_awareness,
    metacognition,
    trust_verification,
    completeness,
    code_quality,
    consistency,
    sequential_thinking,
    pattern_recognition
)


@pytest.fixture
def all_synapses():
    """Fixture providing all 9 synapses."""
    return {
        "anti_rationalization": anti_rationalization,
        "security_awareness": security_awareness,
        "metacognition": metacognition,
        "trust_verification": trust_verification,
        "completeness": completeness,
        "code_quality": code_quality,
        "consistency": consistency,
        "sequential_thinking": sequential_thinking,
        "pattern_recognition": pattern_recognition
    }


@pytest.fixture
def halt_expected():
    """Marker for test cases that should result in HALT."""
    return "halt"


@pytest.fixture
def allow_expected():
    """Marker for test cases that should result in ALLOW."""
    return "allow"
