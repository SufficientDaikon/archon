"""Test suite for code_quality synapse."""

import pytest
from archon.synapses import code_quality


class TestCodeQualityMetrics:
    """Test cases for code quality enforcement."""
    
    def test_good_quality(self):
        result = code_quality.validate({
            "code": "def func() -> None: pass",
            "has_type_hints": True,
            "has_docstrings": True,
            "pylint_score": 9.0,
            "cyclomatic_complexity": 1
        })
        assert result["action"] == "allow"
    
    def test_low_pylint_score(self):
        result = code_quality.validate({
            "code": "x = 1",
            "pylint_score": 3.0,
            "min_score": 7.0
        })
        assert result["action"] == "halt"
    
    def test_high_complexity(self):
        result = code_quality.validate({
            "code": "complex code",
            "cyclomatic_complexity": 15
        })
        assert result["action"] == "halt"
    
    def test_missing_type_hints(self):
        result = code_quality.validate({
            "code": "def func(x): return x",
            "has_type_hints": False
        })
        assert result["action"] == "halt"
    
    def test_missing_docstrings(self):
        result = code_quality.validate({
            "code": "def complex_function(): return calculate_something()",
            "has_docstrings": False
        })
        assert result["action"] == "halt"
