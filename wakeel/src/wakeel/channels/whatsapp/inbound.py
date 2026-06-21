from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from twilio.request_validator import RequestValidator


def parse_inbound(
    request: Request,
    form_data: dict[str, str],
    cfg: Any,
) -> tuple[str, str]:
    """Validate Twilio signature and extract (from_, body) from the form payload.

    Raises HTTP 403 if signature is invalid and DEV_SKIP_VALIDATION is not set.
    """
    from_ = form_data.get("From", "")
    body = form_data.get("Body", "")

    if not (cfg and cfg.dev_skip_validation):
        _validate_signature(request, form_data, cfg)

    return from_, body


def _validate_signature(
    request: Request,
    form_data: dict[str, str],
    cfg: Any,
) -> None:
    if not cfg or not cfg.twilio_auth_token:
        raise HTTPException(status_code=403, detail="Twilio auth not configured")

    validator = RequestValidator(cfg.twilio_auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not validator.validate(url, form_data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
