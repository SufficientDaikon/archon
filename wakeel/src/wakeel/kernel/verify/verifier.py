from __future__ import annotations

import logging
from typing import Any

from ..provider.client import OpenAICompatClient

logger = logging.getLogger(__name__)

_VERIFY_SYSTEM = """\
You are a disciplined verifier enforcing Iron Law #7: VERIFY, DON'T TRUST.

Review the draft response below. Check:
1. Is it factually accurate (no hallucinated claims)?
2. Is it honest about uncertainty?
3. Is it responsive to the user's question?

If the draft is acceptable, output it verbatim.
If you find a specific factual error, produce a corrected version.
Do NOT add new content, expand scope, or change the style.
Return the final response text only — no preamble, no explanation."""


async def verify(
    draft: str,
    question: str,
    cfg: Any,
    client: OpenAICompatClient,
) -> str:
    """Audit draft against Iron Law #7. Degrades to draft on any failure."""
    messages = [
        {"role": "system", "content": _VERIFY_SYSTEM},
        {
            "role": "user",
            "content": f"User question: {question}\n\nDraft response:\n{draft}",
        },
    ]
    try:
        return await client.complete(cfg, messages)
    except Exception as exc:
        logger.warning("Verify degraded to draft: %s", exc)
        return draft
