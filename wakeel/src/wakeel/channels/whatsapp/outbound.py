from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def send_reply(to: str, body: str, cfg: Any) -> None:
    """Send a WhatsApp message via Twilio REST (runs in executor to avoid blocking)."""
    if not cfg or not cfg.twilio_account_sid:
        logger.error("Twilio credentials not configured; reply not sent to %s", to)
        return

    def _send() -> str:
        from twilio.rest import Client
        client = Client(cfg.twilio_account_sid, cfg.twilio_auth_token)
        msg = client.messages.create(from_=cfg.twilio_from, body=body, to=to)
        return msg.sid

    try:
        loop = asyncio.get_running_loop()
        sid = await loop.run_in_executor(None, _send)
        logger.info("Sent reply %s to %s", sid, to)
    except Exception as exc:
        logger.error("Failed to send reply to %s: %s", to, exc)
