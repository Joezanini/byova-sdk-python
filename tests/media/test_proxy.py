"""WebSocket proxy connector tests."""

from __future__ import annotations

import asyncio
import json

import pytest

from webex_byova.media.config import MediaServerConfig
from webex_byova.media.events import SessionStartEvent
from webex_byova.media.proxy.adapter import DefaultProxyAdapter
from webex_byova.media.proxy.connector import WebSocketProxyConnector
from webex_byova.media.server import BYOVAMediaServer
from webex_byova.media.session import MediaSession


@pytest.mark.asyncio
async def test_default_adapter_session_start() -> None:
    adapter = DefaultProxyAdapter()
    server = BYOVAMediaServer(MediaServerConfig(verify_tokens=False))
    session = MediaSession(conversation_id="conv-1", config=server.config, server=server)
    message = adapter.to_backend(
        SessionStartEvent(conversation_id="conv-1", metadata={"key": "val"}),
        session,
    )
    data = json.loads(message)
    assert data["type"] == "session_start"
    assert data["conversation_id"] == "conv-1"


@pytest.mark.asyncio
async def test_minimal_proxy_dialog() -> None:
    websockets = pytest.importorskip("websockets")
    received: asyncio.Queue[str] = asyncio.Queue()

    async def handler(websocket):  # noqa: ANN001
        msg = await websocket.recv()
        await received.put(msg)
        await websocket.send(json.dumps({"type": "prompt", "payload": {"text": "Hi"}}))

    server_ws = await websockets.serve(handler, "127.0.0.1", 0)
    port = server_ws.sockets[0].getsockname()[1]
    try:
        connector = WebSocketProxyConnector(url=f"ws://127.0.0.1:{port}")
        media = BYOVAMediaServer(MediaServerConfig(verify_tokens=False))
        media.use_proxy(connector)
        session = MediaSession(conversation_id="c1", config=media.config, server=media)
        await connector.forward_event(
            SessionStartEvent(conversation_id="c1"),
            session,
        )
        msg = await asyncio.wait_for(received.get(), timeout=3.0)
        assert "session_start" in msg
    finally:
        server_ws.close()
        await server_ws.wait_closed()


@pytest.mark.asyncio
async def test_buffer_overflow_disconnect() -> None:
    config = MediaServerConfig(
        verify_tokens=False,
        proxy_buffer_limit=10,
        proxy_overflow_policy="disconnect",
    )
    connector = WebSocketProxyConnector(url="ws://127.0.0.1:1")
    media = BYOVAMediaServer(config)
    media.use_proxy(connector)
    session = MediaSession(conversation_id="c1", config=config, server=media)

    with pytest.raises(Exception):
        await connector.forward_event(
            SessionStartEvent(conversation_id="c1"),
            session,
        )
