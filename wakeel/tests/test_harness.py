"""Gate 4 (mocked): Harness.respond returns non-empty string end-to-end."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wakeel.kernel.harness import Harness, FALLBACK_REPLY
from wakeel.kernel.provider.client import OpenAICompatClient, ProviderError
from wakeel.kernel.router.skill_router import SkillRouter
from wakeel.kernel.sessions import InMemorySessionStore


def _make_harness(
    draft_response: str = "This is the response.",
    draft_raises: Exception | None = None,
) -> Harness:
    mock_client = MagicMock(spec=OpenAICompatClient)
    if draft_raises:
        mock_client.complete = AsyncMock(side_effect=draft_raises)
    else:
        mock_client.complete = AsyncMock(return_value=draft_response)

    mock_router = MagicMock(spec=SkillRouter)
    mock_router.select_skill.return_value = None

    mock_cfg = MagicMock()
    mock_cfg.draft = MagicMock(name="gemini")
    mock_cfg.verify = MagicMock(name="groq")

    return Harness(cfg=mock_cfg, router=mock_router, client=mock_client)


async def test_respond_returns_non_empty() -> None:
    harness = _make_harness()
    result = await harness.respond("session-1", "Hello!")
    assert isinstance(result, str)
    assert len(result) > 0


async def test_draft_failure_returns_fallback() -> None:
    harness = _make_harness(draft_raises=ProviderError("gemini", "timeout"))
    result = await harness.respond("session-2", "What is Python?")
    assert result == FALLBACK_REPLY


async def test_session_history_accumulates() -> None:
    harness = _make_harness()
    store = InMemorySessionStore()
    harness._store = store

    await harness.respond("sess", "first message")
    history = store.get_history("sess")
    assert len(history) == 2  # user + assistant turn
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


async def test_draft_malformed_response_returns_fallback() -> None:
    harness = _make_harness(draft_raises=KeyError("choices"))
    result = await harness.respond("session-err", "What is Python?")
    assert result == FALLBACK_REPLY


async def test_skill_matched_content_in_messages() -> None:
    mock_entry = MagicMock()
    mock_entry.name = "backend-development"

    mock_client = MagicMock(spec=OpenAICompatClient)
    mock_client.complete = AsyncMock(return_value="skill response")

    mock_router = MagicMock(spec=SkillRouter)
    mock_router.select_skill.return_value = mock_entry
    mock_router.get_skill_content.return_value = "# Backend Dev\nContent."

    mock_cfg = MagicMock()
    mock_cfg.draft = MagicMock()
    mock_cfg.verify = MagicMock()

    harness = Harness(cfg=mock_cfg, router=mock_router, client=mock_client)
    result = await harness.respond("sess", "how do I build a REST API?")
    assert result == "skill response"
    # The system message should reference the skill
    call_args = mock_client.complete.call_args_list[0]
    messages = call_args[0][1]
    system_msg = messages[0]["content"]
    assert "backend-development" in system_msg
