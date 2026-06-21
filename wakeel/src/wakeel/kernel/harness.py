from __future__ import annotations

import logging
from typing import Any

from ..config import WakeelConfig
from ..paths import SKILLS_DIR
from .composer.composer import build_system_prompt
from .provider.client import OpenAICompatClient
from .router.skill_router import SkillRouter
from .sessions import InMemorySessionStore, SessionStore
from .verify.verifier import verify

logger = logging.getLogger(__name__)

FALLBACK_REPLY = "النظام مزحوم دلوقتي، جرّب تاني بعد شوية."


class Harness:
    """The discipline kernel. Orchestrates router → composer → draft → verify."""

    def __init__(
        self,
        cfg: WakeelConfig,
        router: SkillRouter,
        store: SessionStore | None = None,
        client: OpenAICompatClient | None = None,
    ) -> None:
        self._cfg = cfg
        self._router = router
        self._store = store or InMemorySessionStore()
        self._client = client or OpenAICompatClient()

    @classmethod
    def create(cls, cfg: WakeelConfig) -> "Harness":
        router = SkillRouter.build(SKILLS_DIR)
        return cls(cfg=cfg, router=router)

    async def respond(self, session_id: str, text: str) -> str:
        # 1. Route
        skill_entry = self._router.select_skill(text)
        skill_content = ""
        if skill_entry:
            try:
                skill_content = self._router.get_skill_content(skill_entry)
            except Exception as exc:
                logger.warning("Skill load failed, continuing without skill: %s", exc)
                skill_entry = None

        # 2. Compose system prompt
        system_prompt = build_system_prompt(skill_entry, skill_content)

        # 3. Build message list with session history
        history = self._store.get_history(session_id)
        messages = (
            [{"role": "system", "content": system_prompt}]
            + history
            + [{"role": "user", "content": text}]
        )

        # 4. Draft (DRAFT_PROVIDER)
        try:
            draft = await self._client.complete(self._cfg.draft, messages)
        except Exception as exc:
            logger.error("Draft failed after retry: %s", exc)
            return FALLBACK_REPLY

        # 5. Verify (VERIFY_PROVIDER — degrades to draft on any failure)
        final = await verify(draft, text, self._cfg.verify, self._client)

        # 6. Persist turn
        self._store.append(session_id, "user", text)
        self._store.append(session_id, "assistant", final)

        return final
