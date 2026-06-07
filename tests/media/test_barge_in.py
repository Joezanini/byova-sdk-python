"""Barge-in playback cancellation tests."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from webex_byova.media._internal.turn_manager import PlaybackState, TurnManager
from webex_byova.media.config import MediaServerConfig
from webex_byova.media.events import BargeInEvent
from webex_byova.media.server import BYOVAMediaServer
from webex_byova.media.session import MediaSession, TurnContext


@pytest.mark.asyncio
async def test_barge_in_cancels_playback_loop() -> None:
    """PC-002: cancelled playback stops sending remaining chunks."""
    config = MediaServerConfig(verify_tokens=False)
    server = BYOVAMediaServer(config)
    session = MediaSession(conversation_id="c1", config=config, server=server)
    sent: list[bytes] = []

    async def send_response(response: object) -> None:
        _ = response
        sent.append(b"x")

    turn = TurnContext(
        session=session,
        config=config,
        send_response=send_response,
        close_stream=AsyncMock(),
        turn_number=1,
    )
    turn._runtime.playback_state = PlaybackState.PLAYING

    async def play_and_cancel() -> None:
        task = asyncio.create_task(turn.play_prompt(audio=b"\xff" * 800))
        await asyncio.sleep(0)
        turn._runtime.playback_state = PlaybackState.CANCELLED
        await task

    await play_and_cancel()
    assert len(sent) < 5


@pytest.mark.asyncio
async def test_barge_in_dispatches_event() -> None:
    """PC-002: barge-in emits handler event and clears queue."""
    events: list[BargeInEvent] = []

    async def dispatch(name: str, event: object, session: MediaSession, turn: TurnContext) -> None:
        if name == "barge_in":
            events.append(event)  # type: ignore[arg-type]

    manager = TurnManager(MediaServerConfig(barge_in_enabled=True), dispatch=dispatch)
    server = BYOVAMediaServer(MediaServerConfig(verify_tokens=False))
    session = MediaSession(conversation_id="c1", config=server.config, server=server)
    turn = TurnContext(
        session=session,
        config=server.config,
        send_response=AsyncMock(),
        close_stream=AsyncMock(),
        turn_number=1,
    )
    turn._runtime.playback_state = PlaybackState.PLAYING
    turn._runtime.current_prompt_id = "prompt-1"
    turn._runtime.outbound_queue.append(object())  # type: ignore[arg-type]

    await manager.handle_barge_in(session, turn)

    assert len(events) == 1
    assert events[0].cancelled_prompt_id == "prompt-1"
    assert turn._runtime.playback_state == PlaybackState.CANCELLED
    assert len(turn._runtime.outbound_queue) == 0
