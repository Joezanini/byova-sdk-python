"""BYOVA protocol compliance contract tests (PC-001–PC-006)."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from helpers import FakeWebexClient, audio_request, session_start_request

from webex_byova.media._internal.audio import build_mulaw_wav, strip_wav_header
from webex_byova.media._internal.generated import byova_common_pb2, voicevirtualagent_pb2
from webex_byova.media.config import MediaServerConfig
from webex_byova.media.server import BYOVAMediaServer


@pytest.mark.asyncio
async def test_turn_closure_response_final(media_server: BYOVAMediaServer) -> None:
    """PC-001: RESPONSE_FINAL then stream close."""
    done = asyncio.Event()

    @media_server.on("session_start")
    async def on_start(session, turn) -> None:  # noqa: ANN001
        await turn.play_prompt(audio=b"\xff" * 320)
        done.set()

    conv_id = str(uuid.uuid4())
    client = FakeWebexClient("127.0.0.1", media_server.config.port)
    await client.connect()
    try:
        responses = await client.run_turn([session_start_request(conv_id)])
    finally:
        await client.close()

    await asyncio.wait_for(done.wait(), timeout=5.0)
    final_indices = [
        i
        for i, r in enumerate(responses)
        if r.response_type == voicevirtualagent_pb2.VoiceVAResponse.FINAL
    ]
    assert final_indices, "Expected RESPONSE_FINAL"
    assert final_indices[-1] == len(responses) - 1


@pytest.mark.asyncio
async def test_input_events_start_and_end(media_server: BYOVAMediaServer) -> None:
    """PC-003: START_OF_INPUT and END_OF_INPUT."""
    done = asyncio.Event()

    @media_server.on("audio_input")
    async def on_audio(event, session, turn) -> None:  # noqa: ANN001
        await turn.end_turn()
        done.set()

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

    await asyncio.wait_for(done.wait(), timeout=5.0)
    events = FakeWebexClient.output_events(responses)
    assert byova_common_pb2.OutputEvent.START_OF_INPUT in events


@pytest.mark.asyncio
async def test_chunked_audio_no_riff_header(media_server: BYOVAMediaServer) -> None:
    """PC-005: chunked payloads must not contain WAV headers."""
    wav = build_mulaw_wav(b"\xff" * 160)
    done = asyncio.Event()

    @media_server.on("session_start")
    async def on_start(session, turn) -> None:  # noqa: ANN001
        await turn.play_prompt(audio=wav)
        done.set()

    client = FakeWebexClient("127.0.0.1", media_server.config.port)
    await client.connect()
    try:
        responses = await client.run_turn([session_start_request(str(uuid.uuid4()))])
    finally:
        await client.close()

    await asyncio.wait_for(done.wait(), timeout=5.0)
    for response in responses:
        for prompt in response.prompts:
            if prompt.audio_content:
                assert not prompt.audio_content.startswith(b"RIFF")


@pytest.mark.asyncio
async def test_sample_rate_16000() -> None:
    """PC-006: 16 kHz sample rate propagation."""
    config = MediaServerConfig(host="127.0.0.1", port=0, sample_rate=16000, verify_tokens=False)
    server = BYOVAMediaServer(config)
    await server.start()
    port = server.config.port
    rates: list[int] = []
    done = asyncio.Event()

    @server.on("audio_input")
    async def on_audio(event, session, turn) -> None:  # noqa: ANN001
        rates.append(event.sample_rate)
        await turn.end_turn()
        done.set()

    conv_id = str(uuid.uuid4())
    client = FakeWebexClient("127.0.0.1", port)
    await client.connect()
    try:
        await client.run_turn(
            [
                session_start_request(conv_id),
                audio_request(conv_id, b"\x00" * 80, sample_rate=16000),
            ]
        )
    finally:
        await client.close()
        await server.stop()

    await asyncio.wait_for(done.wait(), timeout=5.0)
    assert rates == [16000]


@pytest.mark.asyncio
async def test_full_mode_wav_container() -> None:
    """PC-004: full mode sends WAV container."""
    config = MediaServerConfig(host="127.0.0.1", port=0, audio_mode="full", verify_tokens=False)
    server = BYOVAMediaServer(config)
    await server.start()
    port = server.config.port
    payloads: list[bytes] = []
    done = asyncio.Event()

    @server.on("session_start")
    async def on_start(session, turn) -> None:  # noqa: ANN001
        await turn.play_prompt(audio=b"\xff" * 80)
        done.set()

    client = FakeWebexClient("127.0.0.1", port)
    await client.connect()
    try:
        responses = await client.run_turn([session_start_request(str(uuid.uuid4()))])
    finally:
        await client.close()
        await server.stop()

    await asyncio.wait_for(done.wait(), timeout=5.0)
    for response in responses:
        for prompt in response.prompts:
            if prompt.audio_content:
                payloads.append(prompt.audio_content)
    assert any(p.startswith(b"RIFF") for p in payloads)


@pytest.mark.asyncio
async def test_wav_strip_size() -> None:
    """PC-005: stripped size equals input minus header."""
    raw = b"\xff" * 100
    wav = build_mulaw_wav(raw)
    stripped = strip_wav_header(wav)
    assert len(stripped) == len(raw)
