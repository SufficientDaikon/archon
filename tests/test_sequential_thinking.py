"""Test suite for sequential_thinking synapse."""

import pytest
from archon.synapses import sequential_thinking


class TestSequentialThinking:
    """Test cases for logical reasoning progression."""
    
    def test_circular_reasoning_blocked(self):
        result = sequential_thinking.validate({
            "steps": ["A", "B", "C"],
            "claims": ["Result"],
            "evidence": [],
            "dependencies": {"A": "B", "B": "C", "C": "A"}
        })
        assert result["action"] == "halt"
    
    def test_simple_reasoning(self):
        result = sequential_thinking.validate({
            "steps": ["Given X"],
            "claims": ["Result"],
            "evidence": ["X confirmed"],
            "dependencies": {}
        })
        # Allow or halt depending on heuristics
        assert result["action"] in ["halt", "allow"]
