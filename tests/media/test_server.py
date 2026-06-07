"""Minimal session flow tests."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from helpers import FakeWebexClient, audio_request, session_start_request

from webex_byova.media.config import MediaServerConfig
from webex_byova.media.server import BYOVAMediaServer


@pytest.mark.asyncio
async def test_minimal_session_flow(media_server: BYOVAMediaServer) -> None:
    """Verify SESSION_START, prompt playback, and turn closure."""
    events: list[str] = []
    prompt_done = asyncio.Event()

    @media_server.on("session_start")
    async def on_start(session, turn) -> None:  # noqa: ANN001
        events.append("session_start")
        await turn.play_prompt(text="Hello", audio=b"\xff" * 160)

    @media_server.on("turn_started")
    async def on_turn_started(event, session, turn) -> None:  # noqa: ANN001
        events.append("turn_started")

    @media_server.on("turn_ended")
    async def on_turn_ended(event, session, turn) -> None:  # noqa: ANN001
        events.append("turn_ended")
        prompt_done.set()

    conv_id = str(uuid.uuid4())
    client = FakeWebexClient("127.0.0.1", media_server.config.port)
    await client.connect()
    try:
        responses = await client.run_turn(
            [
                session_start_request(conv_id),
                audio_request(conv_id, b"\x00" * 80),
            ]
        )
    finally:
        await client.close()

    await asyncio.wait_for(prompt_done.wait(), timeout=5.0)
    assert "session_start" in events
    assert "turn_started" in events
    assert "turn_ended" in events
    assert FakeWebexClient.has_response_final(responses)
    assert any(r.prompts for r in responses)


@pytest.mark.asyncio
async def test_server_context_manager() -> None:
    config = MediaServerConfig(host="127.0.0.1", port=0, verify_tokens=False)
    async with BYOVAMediaServer(config) as server:
        assert server._running  # noqa: SLF001
