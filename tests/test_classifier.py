"""Unit tests for hooks/claude/shared/classifier.py — pure functions, no I/O."""

import sys
from pathlib import Path

ARCHON_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ARCHON_ROOT / "hooks" / "claude"))

from shared.classifier import (  # noqa: E402
    active_synapses,
    build_synapse_context,
    classify_complexity,
    match_skills,
    strip_noise,
)


class TestStripNoise:
    def test_fenced_code_removed(self):
        prompt = "fix this\n```python\n" + "x = 1\n" * 200 + "```"
        assert len(strip_noise(prompt).split()) < 10

    def test_tracebacks_removed(self):
        prompt = (
            "why does this fail\n"
            "Traceback (most recent call last):\n"
            '  File "app.py", line 10, in main\n'
            "ValueError: boom"
        )
        stripped = strip_noise(prompt)
        assert "Traceback" not in stripped
        assert 'File "app.py"' not in stripped

    def test_log_lines_removed(self):
        lines = "\n".join(f"2026-01-01T00:00:{i:02d} ERROR module {i}" for i in range(50))
        stripped = strip_noise(f"investigate\n{lines}")
        assert len(stripped.split()) < 5

    def test_plain_text_untouched(self):
        prompt = "refactor the payment module to use the new API"
        assert strip_noise(prompt).split() == prompt.split()


class TestClassifyComplexity:
    def test_greeting_trivial(self):
        assert classify_complexity("hi") == "TRIVIAL"

    def test_log_stuffed_prompt_stays_low(self):
        # Regression: pasted logs must not inflate a terse request to EXPERT
        logs = "\n".join(f"2026-01-01T00:00:{i:02d} ERROR something {i}" for i in range(80))
        prompt = f"fix this error\n```\n{logs}\n```"
        assert classify_complexity(prompt) in ("TRIVIAL", "SIMPLE")

    def test_pure_question_deescalates(self):
        question = (
            "what does the security architecture of the authentication pipeline look like "
            "and how does the authorization flow work in this distributed system today?"
        )
        statement = (
            "refactor the security architecture of the authentication pipeline "
            "and rework the authorization flow in this distributed system now please"
        )
        tiers = ["TRIVIAL", "SIMPLE", "MODERATE", "COMPLEX", "EXPERT"]
        assert tiers.index(classify_complexity(question)) < tiers.index(
            classify_complexity(statement)
        )

    def test_question_with_imperative_not_deescalated(self):
        prompt = "can you fix the login bug and add a regression test for it"
        assert classify_complexity(prompt) != "TRIVIAL"

    def test_keyword_escalation(self):
        assert classify_complexity("rebuild this from scratch end to end") in (
            "MODERATE",
            "COMPLEX",
            "EXPERT",
        )

    def test_multi_file_escalates(self):
        base = "update the config in these files"
        with_files = f"{base} app.py settings.py urls.py"
        tiers = ["TRIVIAL", "SIMPLE", "MODERATE", "COMPLEX", "EXPERT"]
        assert tiers.index(classify_complexity(with_files)) > tiers.index(classify_complexity(base))

    def test_numbered_steps_escalate(self):
        prompt = "do this:\n1. add the model\n2. add the view\n3. add the tests"
        tiers = ["TRIVIAL", "SIMPLE", "MODERATE", "COMPLEX", "EXPERT"]
        assert tiers.index(classify_complexity(prompt)) > 0


class TestSkillMatching:
    def test_no_pruned_skills_referenced(self):
        # Every skill the classifier can emit must exist on disk
        from shared.classifier import SKILL_MATCHERS

        skills_dir = ARCHON_ROOT / "skills"
        for _, skills in SKILL_MATCHERS:
            for skill in skills:
                assert (skills_dir / skill).is_dir(), f"classifier references missing skill {skill}"

    def test_django_maps_to_expert(self):
        assert "django-expert" in match_skills("help with my django app")
        assert "django-framework" not in match_skills("help with my django app")


class TestSynapseContext:
    def test_trivial_silent_without_security(self):
        syn = active_synapses("TRIVIAL", "rename this variable please")
        assert build_synapse_context(syn, "TRIVIAL") == ""

    def test_trivial_security_keyword_injects(self):
        syn = active_synapses("TRIVIAL", "store the password")
        ctx = build_synapse_context(syn, "TRIVIAL")
        assert "security-awareness" in ctx
        # Nothing else leaks in at TRIVIAL
        assert "metacognition" not in ctx

    def test_moderate_has_base_not_escape_hatch(self):
        syn = active_synapses("MODERATE", "refactor the module")
        ctx = build_synapse_context(syn, "MODERATE")
        assert "PLAN before executing" in ctx
        assert "ESCAPE HATCH" not in ctx

    def test_complex_adds_escape_hatch(self):
        syn = active_synapses("COMPLEX", "refactor the module")
        ctx = build_synapse_context(syn, "COMPLEX")
        assert "ESCAPE HATCH" in ctx
        assert "IRON LAWS" in ctx
        assert "STUCK-LOOP" not in ctx

    def test_expert_adds_stuck_loop(self):
        syn = active_synapses("EXPERT", "refactor the module")
        ctx = build_synapse_context(syn, "EXPERT")
        assert "STUCK-LOOP" in ctx

    def test_token_budget(self):
        # EXPERT with everything active must stay under ~600 tokens
        syn = active_synapses("EXPERT", "refactor the authentication implementation")
        ctx = build_synapse_context(syn, "EXPERT")
        assert len(ctx.split()) * 1.4 < 600


class TestStatePlaceholders:
    """ADK-style {state.<key>?} templating — never raises, degrades to empty."""

    def test_tests_failing_notice_renders_when_failing(self):
        from shared.classifier import resolve_state_placeholders

        text = "IRON LAWS.{state.tests_failing_notice?}"
        out = resolve_state_placeholders(text, {"tests_passed": False})
        assert "FAILING" in out

    def test_notice_absent_when_passing_or_unknown(self):
        from shared.classifier import resolve_state_placeholders

        text = "IRON LAWS.{state.tests_failing_notice?}"
        assert resolve_state_placeholders(text, {"tests_passed": True}) == "IRON LAWS."
        assert resolve_state_placeholders(text, {"tests_passed": None}) == "IRON LAWS."
        assert resolve_state_placeholders(text, None) == "IRON LAWS."

    def test_pending_todos_notice(self):
        from shared.classifier import resolve_state_placeholders

        text = "PLAN.{state.pending_todos_notice?}"
        out = resolve_state_placeholders(text, {"todos_pending_titles": ["ship it", "docs"]})
        assert "ship it" in out and "docs" in out

    def test_unknown_key_renders_empty(self):
        from shared.classifier import resolve_state_placeholders

        assert resolve_state_placeholders("x{state.nope?}y", {"a": 1}) == "xy"

    def test_provider_exception_renders_empty(self):
        from shared.classifier import _STATE_PROVIDERS, resolve_state_placeholders

        _STATE_PROVIDERS["boom"] = lambda session: 1 / 0
        try:
            assert resolve_state_placeholders("x{state.boom?}y", {}) == "xy"
        finally:
            del _STATE_PROVIDERS["boom"]

    def test_build_context_without_session_unchanged(self):
        # 2-arg call keeps working; placeholders render empty
        syn = active_synapses("COMPLEX", "refactor the module")
        ctx = build_synapse_context(syn, "COMPLEX")
        assert "IRON LAWS" in ctx
        assert "{state." not in ctx

    def test_build_context_with_failing_session(self):
        syn = active_synapses("COMPLEX", "refactor the module")
        ctx = build_synapse_context(syn, "COMPLEX", {"tests_passed": False})
        assert "Tests are recorded FAILING" in ctx
