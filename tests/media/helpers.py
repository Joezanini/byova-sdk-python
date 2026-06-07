"""Test helpers for media server integration tests."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator

import grpc

from webex_byova.media._internal.generated import byova_common_pb2, voicevirtualagent_pb2
from webex_byova.media._internal.generated.voicevirtualagent_pb2_grpc import VoiceVirtualAgentStub


def session_start_request(
    conversation_id: str | None = None,
) -> voicevirtualagent_pb2.VoiceVARequest:
    """Build a SESSION_START request."""
    event = byova_common_pb2.EventInput(
        event_type=byova_common_pb2.EventInput.SESSION_START,
        name="call_start",
    )
    return voicevirtualagent_pb2.VoiceVARequest(
        conversation_id=conversation_id or str(uuid.uuid4()),
        customer_org_id="org-test",
        event_input=event,
    )


def audio_request(
    conversation_id: str,
    audio: bytes,
    *,
    sample_rate: int = 8000,
) -> voicevirtualagent_pb2.VoiceVARequest:
    """Build inbound caller audio request."""
    voice = voicevirtualagent_pb2.VoiceInput(
        caller_audio=audio,
        encoding=voicevirtualagent_pb2.VoiceInput.MULAW_FORMAT,
        sample_rate_hertz=sample_rate,
        language_code="en-US",
    )
    return voicevirtualagent_pb2.VoiceVARequest(
        conversation_id=conversation_id,
        customer_org_id="org-test",
        audio_input=voice,
    )


class FakeWebexClient:
    """In-memory gRPC client simulating Webex turn streams."""

    def __init__(self, host: str, port: int) -> None:
        self._target = f"{host}:{port}"
        self._channel: grpc.aio.Channel | None = None
        self._stub: VoiceVirtualAgentStub | None = None
        self.responses: list[voicevirtualagent_pb2.VoiceVAResponse] = []

    async def connect(self) -> None:
        self._channel = grpc.aio.insecure_channel(self._target)
        self._stub = VoiceVirtualAgentStub(self._channel)

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()

    async def run_turn(
        self,
        requests: list[voicevirtualagent_pb2.VoiceVARequest],
        *,
        metadata: tuple[tuple[str, str], ...] | None = None,
    ) -> list[voicevirtualagent_pb2.VoiceVAResponse]:
        """Execute one bidirectional turn and collect responses."""
        assert self._stub is not None

        async def request_iter() -> AsyncIterator[voicevirtualagent_pb2.VoiceVARequest]:
            for index, req in enumerate(requests):
                yield req
                if index == 0 and len(requests) > 1:
                    await asyncio.sleep(0.05)
                await asyncio.sleep(0)

        responses: list[voicevirtualagent_pb2.VoiceVAResponse] = []
        call = self._stub.ProcessCallerInput(request_iter(), metadata=metadata)
        async for response in call:
            responses.append(response)
        self.responses.extend(responses)
        return responses

    @staticmethod
    def has_response_final(responses: list[voicevirtualagent_pb2.VoiceVAResponse]) -> bool:
        return any(
            r.response_type == voicevirtualagent_pb2.VoiceVAResponse.FINAL for r in responses
        )

    @staticmethod
    def output_events(
        responses: list[voicevirtualagent_pb2.VoiceVAResponse],
    ) -> list[byova_common_pb2.OutputEvent.EventType]:
        events: list[byova_common_pb2.OutputEvent.EventType] = []
        for response in responses:
            for event in response.output_events:
                events.append(event.event_type)
        return events
