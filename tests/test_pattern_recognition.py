"""Test suite for pattern_recognition synapse."""

import pytest
from archon.synapses import pattern_recognition


class TestPatternRecognition:
    """Test cases for error pattern detection."""
    
    def test_repeated_error_pattern(self):
        result = pattern_recognition.validate({
            "execution_history": [
                {"action": "deploy", "error": "timeout"},
                {"action": "deploy", "error": "timeout"},
                {"action": "deploy", "error": "timeout"}
            ],
            "current_action": "deploy",
            "error_patterns": ["timeout"],
            "failure_threshold": 3
        })
        assert result["action"] == "halt"
    
    def test_no_repeated_pattern(self):
        result = pattern_recognition.validate({
            "execution_history": [
                {"action": "deploy", "error": "timeout"},
                {"action": "retry", "error": "connection"}
            ],
            "current_action": "deploy",
            "error_patterns": ["timeout"],
            "failure_threshold": 3
        })
        assert result["action"] == "allow"
    
    def test_empty_history(self):
        result = pattern_recognition.validate({
            "execution_history": [],
            "current_action": "execute",
            "error_patterns": []
        })
        assert result["action"] == "allow"
    
    @pytest.mark.parametrize("count", [2, 3, 4, 5])
    def test_threshold_exceeded(self, count):
        result = pattern_recognition.validate({
            "execution_history": [
                {"action": "retry", "error": "timeout"}
                for _ in range(count)
            ],
            "current_action": "retry",
            "error_patterns": ["timeout"],
            "failure_threshold": 3
        })
        if count >= 3:
            assert result["action"] == "halt"
