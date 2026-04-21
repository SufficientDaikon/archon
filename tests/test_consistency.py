"""Test suite for consistency synapse."""

import pytest
from archon.synapses import consistency


class TestConsistencyNames:
    """Test cases for consistency checking."""
    
    def test_consistent_names(self):
        result = consistency.validate({
            "files_changed": ["a.py", "b.py", "c.py", "d.py", "e.py", "f.py"],
            "definitions": {"my_var": "x", "another_var": "y"},
            "naming_style": "snake_case"
        })
        assert result["action"] == "allow"
    
    def test_inconsistent_names(self):
        result = consistency.validate({
            "files_changed": ["a.py", "b.py", "c.py", "d.py", "e.py", "f.py"],
            "definitions": {"myVar": "x", "another_var": "y"},
            "naming_style": "snake_case"
        })
        assert result["action"] == "halt"
    
    def test_mixed_imports(self):
        result = consistency.validate({
            "files_changed": ["a.py", "b.py", "c.py", "d.py", "e.py", "f.py"],
            "imports": ["/absolute/path", "./relative/path"],
            "naming_style": "snake_case"
        })
        assert result["action"] == "halt"
