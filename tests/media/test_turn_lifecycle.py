"""Multi-turn session lifecycle tests."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from helpers import FakeWebexClient, session_start_request

from webex_byova.media.server import BYOVAMediaServer


@pytest.mark.asyncio
async def test_five_turn_session(media_server: BYOVAMediaServer) -> None:
    """Verify same conversation_id across multiple turns."""
    turn_numbers: list[int] = []
    conversation_ids: list[str] = []
    lock = asyncio.Lock()
    turns_done = asyncio.Event()
    expected_turns = 5
    completed = 0

    @media_server.on("session_start")
    async def on_start(session, turn) -> None:  # noqa: ANN001
        async with lock:
            conversation_ids.append(session.conversation_id)
        await turn.end_turn()

    @media_server.on("turn_started")
    async def on_turn(event, session, turn) -> None:  # noqa: ANN001
        turn_numbers.append(event.turn_number)

    @media_server.on("turn_ended")
    async def on_turn_end(event, session, turn) -> None:  # noqa: ANN001
        nonlocal completed
        completed += 1
        if completed >= expected_turns:
            turns_done.set()

    conv_id = str(uuid.uuid4())
    client = FakeWebexClient("127.0.0.1", media_server.config.port)
    await client.connect()
    try:
        for _ in range(expected_turns):
            await client.run_turn([session_start_request(conv_id)])
    finally:
        await client.close()

    await asyncio.wait_for(turns_done.wait(), timeout=10.0)
    assert len(set(conversation_ids)) == 1
    assert conversation_ids[0] == conv_id
    assert turn_numbers == list(range(1, expected_turns + 1))
