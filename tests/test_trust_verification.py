"""Test suite for trust_verification synapse."""

import pytest
from archon.synapses import trust_verification


class TestTrustVerification:
    """Test cases for evidence requirement enforcement."""
    
    def test_critical_without_evidence(self):
        result = trust_verification.validate({
            "reasoning": "This always works",
            "evidence": []
        })
        assert result["action"] == "halt"
    
    def test_with_evidence(self):
        result = trust_verification.validate({
            "reasoning": "This approach works",
            "evidence": ["test1", "test2", "test3"]
        })
        assert result["action"] == "allow"
    
    def test_empty(self):
        result = trust_verification.validate({
            "reasoning": "",
            "evidence": []
        })
        assert result["action"] == "allow"
