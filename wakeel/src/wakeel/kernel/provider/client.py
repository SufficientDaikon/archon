from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Raised when a provider call fails after one retry."""

    def __init__(self, provider: str, reason: str) -> None:
        self.provider = provider
        self.reason = reason
        super().__init__(f"Provider '{provider}' failed: {reason}")


class OpenAICompatClient:
    """Single async client for all OpenAI-compatible providers.

    Retries once on any HTTP error / non-2xx / 429 with a short backoff.
    Raises ProviderError after both attempts fail.
    Base URL must have no trailing slash; the client appends /chat/completions.
    """

    def __init__(self, timeout: float = 60.0) -> None:
        self._timeout = timeout

    async def complete(self, cfg: Any, messages: list[dict[str, str]]) -> str:
        """Send a chat-completion request. Returns the reply content string."""
        url = f"{cfg.base_url}/chat/completions"
        payload = {"model": cfg.model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None
        for attempt in range(2):
            if attempt > 0:
                await asyncio.sleep(1.5)
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 429 or not resp.is_success:
                    last_error = httpx.HTTPStatusError(
                        f"HTTP {resp.status_code}",
                        request=resp.request,
                        response=resp,
                    )
                    logger.warning(
                        "Provider %s returned %s (attempt %d/2)",
                        getattr(cfg, "name", "?"),
                        resp.status_code,
                        attempt + 1,
                    )
                    continue
                return resp.json()["choices"][0]["message"]["content"]
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "Provider %s HTTP error (attempt %d/2): %s",
                    getattr(cfg, "name", "?"),
                    attempt + 1,
                    exc,
                )

        raise ProviderError(
            provider=getattr(cfg, "name", str(cfg)),
            reason=str(last_error),
        )
