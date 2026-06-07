"""Handler registration and dispatch tests."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from helpers import FakeWebexClient, session_start_request

from webex_byova.media.events import SessionStartEvent
from webex_byova.media.server import BYOVAMediaServer


@pytest.mark.asyncio
async def test_handler_registration_decorator(media_server: BYOVAMediaServer) -> None:
    received: list[SessionStartEvent] = []
    done = asyncio.Event()

    @media_server.handler("session_start")
    async def handle(session, turn) -> None:  # noqa: ANN001
        received.append(SessionStartEvent(conversation_id=session.conversation_id))
        await turn.end_turn()
        done.set()

    conv_id = str(uuid.uuid4())
    client = FakeWebexClient("127.0.0.1", media_server.config.port)
    await client.connect()
    try:
        await client.run_turn([session_start_request(conv_id)])
    finally:
        await client.close()

    await asyncio.wait_for(done.wait(), timeout=5.0)
    assert len(received) == 1
    assert received[0].conversation_id == conv_id


@pytest.mark.asyncio
async def test_sync_handler_via_to_thread(media_server: BYOVAMediaServer) -> None:
    flag: list[bool] = []
    done = asyncio.Event()

    @media_server.on("session_start")
    def sync_handler(session, turn) -> None:  # noqa: ANN001
        flag.append(True)

    @media_server.on("turn_started")
    async def finish(event, session, turn) -> None:  # noqa: ANN001
        await turn.end_turn()
        done.set()

    client = FakeWebexClient("127.0.0.1", media_server.config.port)
    await client.connect()
    try:
        await client.run_turn([session_start_request(str(uuid.uuid4()))])
    finally:
        await client.close()

    await asyncio.wait_for(done.wait(), timeout=5.0)
    assert flag == [True]
