"""Gate 1: TF-IDF router routes dev Q to a skill, non-dev Q to None."""
from __future__ import annotations

import pytest
from wakeel.kernel.router.skill_router import SkillRouter
from wakeel.paths import SKILLS_DIR


@pytest.fixture(scope="module")
def router() -> SkillRouter:
    return SkillRouter.build(SKILLS_DIR)


def test_dev_question_routes_to_skill(router: SkillRouter) -> None:
    entry = router.select_skill("how do I design a REST API in Python")
    assert entry is not None, (
        "Expected a skill match for a dev question about REST APIs — "
        "check SKILLS_DIR and threshold in skill_router.py"
    )


def test_non_dev_question_returns_none(router: SkillRouter) -> None:
    entry = router.select_skill("recipe for pasta with tomato sauce")
    assert entry is None, (
        f"Expected no skill match for a non-dev question, got: {entry}"
    )


def test_skills_indexed(router: SkillRouter) -> None:
    assert len(router._index.skills) > 0, "No skills were indexed — check SKILLS_DIR"
