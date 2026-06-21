"""Gate 6: POST /webhook returns 200 + <Response/> immediately; reply via BackgroundTask."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from wakeel.channels.whatsapp.app import app


def test_webhook_returns_200_and_twiml() -> None:
    """Webhook returns HTTP 200 + empty TwiML immediately — no blocking on LLM or Twilio."""
    mock_harness = MagicMock()
    mock_harness.respond = AsyncMock(return_value="test reply")

    with (
        patch.dict(os.environ, {"DEV_SKIP_VALIDATION": "1"}),
        patch("wakeel.channels.whatsapp.app.Harness") as MockHarness,
        patch("wakeel.channels.whatsapp.app.send_reply", new_callable=AsyncMock),
    ):
        MockHarness.create.return_value = mock_harness
        with TestClient(app) as client:
            response = client.post(
                "/webhook",
                data={"From": "whatsapp:+201234567890", "Body": "how do I build a REST API?"},
            )

    assert response.status_code == 200
    assert response.text == "<Response/>"
    assert response.headers["content-type"].startswith("text/xml")


def test_webhook_health_after_startup() -> None:
    """GET /health returns harness=true after lifespan initialization."""
    mock_harness = MagicMock()

    with (
        patch.dict(os.environ, {"DEV_SKIP_VALIDATION": "1"}),
        patch("wakeel.channels.whatsapp.app.Harness") as MockHarness,
        patch("wakeel.channels.whatsapp.app.send_reply", new_callable=AsyncMock),
    ):
        MockHarness.create.return_value = mock_harness
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["harness"] is True


def test_webhook_background_task_calls_harness() -> None:
    """Background task actually invokes harness.respond with correct args."""
    mock_harness = MagicMock()
    mock_harness.respond = AsyncMock(return_value="response text")
    mock_send = AsyncMock()

    with (
        patch.dict(os.environ, {"DEV_SKIP_VALIDATION": "1"}),
        patch("wakeel.channels.whatsapp.app.Harness") as MockHarness,
        patch("wakeel.channels.whatsapp.app.send_reply", mock_send),
    ):
        MockHarness.create.return_value = mock_harness
        with TestClient(app) as client:
            client.post(
                "/webhook",
                data={"From": "whatsapp:+201234567890", "Body": "hello"},
            )

    mock_harness.respond.assert_awaited_once_with("whatsapp:+201234567890", "hello")
    mock_send.assert_awaited_once()
