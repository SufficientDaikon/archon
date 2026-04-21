"""Test suite for anti_rationalization synapse."""

import pytest
from archon.synapses import anti_rationalization


class TestAntiRationalization:
    """Test cases for forbidden phrase detection."""
    
    def test_should_blocked(self):
        result = anti_rationalization.validate({
            "reasoning": "I should implement this later",
            "task": "build feature"
        })
        assert result["action"] == "halt"
    
    def test_probably_blocked(self):
        result = anti_rationalization.validate({
            "reasoning": "This probably works",
            "task": "build"
        })
        assert result["action"] == "halt"
    
    def test_clean_reasoning(self):
        result = anti_rationalization.validate({
            "reasoning": "I verified this implementation",
            "task": "build feature"
        })
        assert result["action"] == "allow"
    
    def test_empty(self):
        result = anti_rationalization.validate({
            "reasoning": "",
            "task": ""
        })
        assert result["action"] == "allow"
