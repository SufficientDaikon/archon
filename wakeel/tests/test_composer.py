"""Gate 2: Composer assembles prompt with synapses + Iron Laws sentinel."""
from __future__ import annotations

import pytest
from wakeel.kernel.composer.composer import build_system_prompt
from wakeel.kernel.router.indexer import SkillEntry


def _make_entry(name: str = "backend-development") -> SkillEntry:
    return SkillEntry(
        filename=name,
        name=name,
        description="Test skill",
        category="backend",
        priority="P1",
        tags=["backend"],
        triggers={},
        size_bytes=1000,
        size_category="S",
    )


def test_prompt_contains_discipline_sentinel() -> None:
    prompt = build_system_prompt()
    assert "VERIFY, DON'T TRUST" in prompt, (
        "Iron Law #7 sentinel missing from system prompt — "
        "composer is shipping without the discipline layer"
    )


def test_prompt_without_skill_has_sentinel() -> None:
    prompt = build_system_prompt(None, "")
    assert "VERIFY, DON'T TRUST" in prompt


def test_prompt_contains_skill_name_when_provided() -> None:
    entry = _make_entry("backend-development")
    prompt = build_system_prompt(entry, "# Backend Dev\nContent here.")
    assert "backend-development" in prompt


def test_prompt_does_not_contain_skill_when_none() -> None:
    prompt = build_system_prompt(None, "")
    assert "DOMAIN SKILL" not in prompt


def test_synapses_block_present() -> None:
    prompt = build_system_prompt()
    assert "metacognition" in prompt.lower()
    assert "anti-rationalization" in prompt.lower()
