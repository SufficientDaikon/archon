"""Test suite for security_awareness synapse."""

import pytest
from archon.synapses import security_awareness


class TestSecurityAwareness:
    """Test cases for security vulnerability detection."""
    
    def test_exec_blocked(self):
        result = security_awareness.validate({"code": "exec(user_input)"})
        assert result["action"] == "halt"
    
    def test_eval_blocked(self):
        result = security_awareness.validate({"code": "eval(expression)"})
        assert result["action"] == "halt"
    
    def test_password_hardcoded(self):
        result = security_awareness.validate({"code": "password = 'admin123'"})
        assert result["action"] == "halt"
    
    def test_safe_code(self):
        result = security_awareness.validate({"code": "x = get_config()"})
        assert result["action"] == "allow"
    
    def test_empty(self):
        result = security_awareness.validate({"code": ""})
        assert result["action"] == "allow"
