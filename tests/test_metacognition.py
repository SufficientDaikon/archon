"""Test suite for metacognition synapse."""

import pytest
from archon.synapses import metacognition


class TestMetacognitionPlanning:
    def test_trivial_allows(self):
        result = metacognition.validate({
            'complexity': 'TRIVIAL',
            'has_plan': False,
            'confidence': 0.5
        })
        assert result['action'] == 'allow'

    def test_simple_with_reasoning(self):
        result = metacognition.validate({
            'complexity': 'SIMPLE',
            'has_plan': False,
            'reasoning': 'This is sufficient reasoning over 30 chars',
            'confidence': 0.5
        })
        assert result['action'] == 'allow'

    def test_moderate_without_plan(self):
        result = metacognition.validate({
            'complexity': 'MODERATE',
            'has_plan': False,
            'reasoning': 'x' * 100,
            'confidence': 0.5
        })
        assert result['action'] == 'halt'

    def test_complex_without_plan(self):
        result = metacognition.validate({
            'complexity': 'COMPLEX',
            'has_plan': False,
        })
        assert result['action'] == 'halt'

    def test_complex_with_full_context(self):
        result = metacognition.validate({
            'complexity': 'COMPLEX',
            'has_plan': True,
            'reasoning': 'I considered the trade-offs and alternatives because this is a complex problem. However, the risk is manageable. The assumption is that we have test coverage. I verified the approach against alternatives and the trade-off analysis shows this is optimal. We should investigate edge cases.',
            'confidence': 0.7,
            'evidence_count': 3
        })
        assert result['action'] == 'allow'

    def test_overconfident_without_evidence(self):
        result = metacognition.validate({
            'complexity': 'SIMPLE',
            'has_plan': False,
            'reasoning': 'This is sufficient reasoning for the test case here',
            'confidence': 1.0,
            'evidence_count': 0
        })
        assert result['action'] == 'halt'
