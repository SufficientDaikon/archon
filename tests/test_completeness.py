"""Test suite for completeness synapse."""

import pytest
from archon.synapses import completeness


class TestCompletenessAcceptanceCriteria:
    """Test cases for acceptance criteria enforcement."""
    
    def test_all_critical_met(self):
        result = completeness.validate({
            "acceptance_criteria": [
                {"name": "Feature", "met": True, "critical": True},
                {"name": "Tests", "met": True, "critical": True}
            ],
            "todos_remaining": 0,
            "tests_passed": 5
        })
        assert result["action"] == "allow"
    
    def test_critical_unmet(self):
        result = completeness.validate({
            "acceptance_criteria": [
                {"name": "Feature", "met": True, "critical": True},
                {"name": "Tests", "met": False, "critical": True}
            ],
            "todos_remaining": 0
        })
        assert result["action"] == "halt"
    
    def test_todos_remaining(self):
        result = completeness.validate({
            "acceptance_criteria": [
                {"name": "Feature", "met": True, "critical": True}
            ],
            "todos_remaining": 3
        })
        assert result["action"] == "halt"
    
    def test_low_completion_rate(self):
        result = completeness.validate({
            "acceptance_criteria": [
                {"name": "A", "met": True, "critical": False},
                {"name": "B", "met": False, "critical": False},
                {"name": "C", "met": False, "critical": False},
                {"name": "D", "met": False, "critical": False},
                {"name": "E", "met": False, "critical": False}
            ]
        })
        assert result["action"] == "halt"
