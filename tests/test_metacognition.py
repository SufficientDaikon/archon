"""Test suite for metacognition synapse."""

import pytest
from archon.synapses import metacognition


class TestMetacognitionPlanning:
    """Test cases for planning requirement."""
    
    @pytest.mark.parametrize("complexity", ["SIMPLE", "TRIVIAL"])
    def test_simple_without_plan(self, complexity):
        result = metacognition.validate({
            "complexity": complexity,
            "has_plan": False
        })
        assert result["action"] == "allow"
    
    @pytest.mark.parametrize("complexity", ["MODERATE", "COMPLEX", "EXPERT"])
    def test_complex_without_plan(self, complexity):
        result = metacognition.validate({
            "complexity": complexity,
            "has_plan": False
        })
        assert result["action"] == "halt"
    
    @pytest.mark.parametrize("complexity", ["SIMPLE", "MODERATE", "COMPLEX", "EXPERT"])
    def test_with_plan(self, complexity):
        result = metacognition.validate({
            "complexity": complexity,
            "has_plan": True
        })
        assert result["action"] == "allow"
