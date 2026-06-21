from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request, Response

from ...config import WakeelConfig, load_config
from ...kernel.harness import Harness
from .inbound import parse_inbound
from .outbound import send_reply

logger = logging.getLogger(__name__)

_harness: Harness | None = None
_cfg: WakeelConfig | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _harness, _cfg
    _cfg = load_config()
    _harness = Harness.create(_cfg)
    logger.info("Wakeel harness ready (draft=%s verify=%s)", _cfg.draft.name, _cfg.verify.name)
    yield
    _harness = None
    _cfg = None


app = FastAPI(title="Wakeel WhatsApp Gateway", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "harness": _harness is not None}


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks) -> Response:
    """Receive Twilio inbound, return 200 immediately, reply via BackgroundTask."""
    form = await request.form()
    form_data = dict(form)

    from_, body = parse_inbound(request, form_data, _cfg)

    background_tasks.add_task(_process_and_reply, from_, body)

    return Response(content="<Response/>", media_type="text/xml")


async def _process_and_reply(from_: str, body: str) -> None:
    try:
        reply = await _harness.respond(from_, body)
        await send_reply(from_, reply, _cfg)
    except Exception as exc:
        logger.error("Unhandled error in background reply to %s: %s", from_, exc)
