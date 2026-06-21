"""Gate 3 (mocked): Provider client retries once, then ProviderError; verify degrades."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from wakeel.kernel.provider.client import OpenAICompatClient, ProviderError
from wakeel.kernel.verify.verifier import verify


@pytest.fixture
def cfg() -> MagicMock:
    m = MagicMock()
    m.base_url = "https://api.example.com/v1"
    m.model = "test-model"
    m.api_key = "test-key"
    m.name = "test-provider"
    return m


@pytest.fixture
def client() -> OpenAICompatClient:
    return OpenAICompatClient(timeout=5.0)


async def test_successful_completion(cfg: MagicMock, client: OpenAICompatClient) -> None:
    mock_resp = MagicMock()
    mock_resp.is_success = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "Hello!"}}]}

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    mock_http.post = AsyncMock(return_value=mock_resp)

    with patch("httpx.AsyncClient", return_value=mock_http):
        result = await client.complete(cfg, [{"role": "user", "content": "Hi"}])

    assert result == "Hello!"


async def test_retries_once_then_raises_provider_error(
    cfg: MagicMock, client: OpenAICompatClient
) -> None:
    """Exactly 2 POST calls (initial + 1 retry) before ProviderError."""
    call_count = 0

    async def failing_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise httpx.HTTPError("network failure")

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    mock_http.post = failing_post

    # Patch sleep so the retry backoff doesn't slow the test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        with patch("httpx.AsyncClient", return_value=mock_http):
            with pytest.raises(ProviderError):
                await client.complete(cfg, [{"role": "user", "content": "Hi"}])

    assert call_count == 2, f"Expected 2 attempts (initial + 1 retry), got {call_count}"


async def test_non_2xx_retries_then_raises(cfg: MagicMock, client: OpenAICompatClient) -> None:
    mock_resp = MagicMock()
    mock_resp.is_success = False
    mock_resp.status_code = 500
    mock_resp.request = MagicMock()

    mock_http = AsyncMock()
    mock_http.__aenter__ = AsyncMock(return_value=mock_http)
    mock_http.__aexit__ = AsyncMock(return_value=False)
    mock_http.post = AsyncMock(return_value=mock_resp)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with patch("httpx.AsyncClient", return_value=mock_http):
            with pytest.raises(ProviderError):
                await client.complete(cfg, [{"role": "user", "content": "Hi"}])


async def test_verify_degrades_to_draft_on_failure() -> None:
    failing_client = MagicMock(spec=OpenAICompatClient)
    failing_client.complete = AsyncMock(side_effect=ProviderError("groq", "timeout"))

    result = await verify("the original draft", "user question", MagicMock(), failing_client)
    assert result == "the original draft"


async def test_verify_returns_audited_response() -> None:
    success_client = MagicMock(spec=OpenAICompatClient)
    success_client.complete = AsyncMock(return_value="audited response")

    result = await verify("draft text", "question", MagicMock(), success_client)
    assert result == "audited response"
