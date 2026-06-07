"""Inbound token verification tests."""

from __future__ import annotations

import uuid
from unittest.mock import patch

import grpc
import pytest
from helpers import FakeWebexClient, session_start_request

from webex_byova.media.config import MediaServerConfig
from webex_byova.media.server import BYOVAMediaServer


@pytest.mark.asyncio
async def test_rejects_missing_token() -> None:
    config = MediaServerConfig(host="127.0.0.1", port=0, verify_tokens=True)
    server = BYOVAMediaServer(config)
    await server.start()
    port = server.config.port

    client = FakeWebexClient("127.0.0.1", port)
    await client.connect()
    try:
        with pytest.raises(grpc.aio.AioRpcError) as exc_info:
            await client.run_turn([session_start_request(str(uuid.uuid4()))])
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        await client.close()
        await server.stop()


@pytest.mark.asyncio
async def test_accepts_valid_token() -> None:
    import asyncio

    config = MediaServerConfig(host="127.0.0.1", port=0, verify_tokens=True)
    server = BYOVAMediaServer(config)
    done = asyncio.Event()

    @server.on("session_start")
    async def on_start(session, turn) -> None:  # noqa: ANN001
        await turn.end_turn()
        done.set()

    await server.start()
    port = server.config.port

    with patch("webex_byova.media._internal.grpc_service.JWSVerifier.verify", return_value={}):
        channel = grpc.aio.insecure_channel(f"127.0.0.1:{port}")
        stub = __import__(
            "webex_byova.media._internal.generated.voicevirtualagent_pb2_grpc",
            fromlist=["VoiceVirtualAgentStub"],
        ).VoiceVirtualAgentStub(channel)

        async def req_iter():
            yield session_start_request(str(uuid.uuid4()))

        metadata = (("authorization", "Bearer valid-token"),)
        call = stub.ProcessCallerInput(req_iter(), metadata=metadata)
        async for _ in call:
            pass
        await channel.close()

    await server.stop()
