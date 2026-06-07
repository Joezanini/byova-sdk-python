"""gRPC VoiceVirtualAgent service implementation."""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

import grpc

from webex_byova.exceptions import AuthenticationError
from webex_byova.jws.verifier import JWSVerifier
from webex_byova.media._internal.generated import byova_common_pb2, voicevirtualagent_pb2
from webex_byova.media._internal.generated.voicevirtualagent_pb2_grpc import (
    VoiceVirtualAgentServicer,
    add_VoiceVirtualAgentServicer_to_server,
)
from webex_byova.media._internal.turn_manager import TurnManager
from webex_byova.media.events import (
    AudioInputEvent,
    DtmfInputEvent,
    SessionEndEvent,
    SessionStartEvent,
)
from webex_byova.media.exceptions import DuplicateTurnStreamError
from webex_byova.media.session import MediaSession, TurnContext

if TYPE_CHECKING:
    from webex_byova.media.server import BYOVAMediaServer

logger = logging.getLogger(__name__)

_DTMF_MAP = {
    byova_common_pb2.DTMF_DIGIT_ZERO: "0",
    byova_common_pb2.DTMF_DIGIT_ONE: "1",
    byova_common_pb2.DTMF_DIGIT_TWO: "2",
    byova_common_pb2.DTMF_DIGIT_THREE: "3",
    byova_common_pb2.DTMF_DIGIT_FOUR: "4",
    byova_common_pb2.DTMF_DIGIT_FIVE: "5",
    byova_common_pb2.DTMF_DIGIT_SIX: "6",
    byova_common_pb2.DTMF_DIGIT_SEVEN: "7",
    byova_common_pb2.DTMF_DIGIT_EIGHT: "8",
    byova_common_pb2.DTMF_DIGIT_NINE: "9",
    byova_common_pb2.DTMF_DIGIT_STAR: "*",
    byova_common_pb2.DTMF_DIGIT_POUND: "#",
}


class VoiceVirtualAgentService(VoiceVirtualAgentServicer):
    """Async bidirectional ``ProcessCallerInput`` handler."""

    def __init__(self, server: BYOVAMediaServer) -> None:
        self._server = server
        self._config = server.config
        self._store = server._conversation_store  # noqa: SLF001
        self._turn_manager = TurnManager(server.config, dispatch=server._dispatch_event)  # noqa: SLF001
        self._verifier = JWSVerifier()

    async def ProcessCallerInput(  # noqa: N802
        self,
        request_iterator: AsyncIterator[voicevirtualagent_pb2.VoiceVARequest],
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[voicevirtualagent_pb2.VoiceVAResponse]:
        """Handle one turn bidirectional stream."""
        stream_id = str(uuid.uuid4())
        conversation_id = ""
        turn: TurnContext | None = None
        session: MediaSession | None = None
        response_queue: asyncio.Queue[voicevirtualagent_pb2.VoiceVAResponse | None] = (
            asyncio.Queue()
        )
        stream_closed = asyncio.Event()

        async def send_response(response: voicevirtualagent_pb2.VoiceVAResponse) -> None:
            await response_queue.put(response)

        async def close_stream() -> None:
            stream_closed.set()
            await response_queue.put(None)

        async def request_reader() -> None:
            nonlocal conversation_id, turn, session
            first_audio = True
            try:
                if self._config.verify_tokens:
                    await self._verify_context(context)

                async for request in request_iterator:
                    conversation_id = request.conversation_id or conversation_id
                    if not conversation_id:
                        continue

                    await self._store.register_stream(conversation_id, stream_id)

                    if request.HasField("event_input"):
                        event = request.event_input
                        if event.event_type == byova_common_pb2.EventInput.SESSION_START:
                            metadata = _struct_to_dict(event.parameters)
                            session = await self._store.get_or_create(
                                conversation_id,
                                MediaSession,
                                config=self._config,
                                server=self._server,
                                metadata=metadata,
                            )
                            turn_number = session.turn_count + 1
                            turn = TurnContext(
                                session=session,
                                config=self._config,
                                send_response=send_response,
                                close_stream=close_stream,
                                turn_number=turn_number,
                            )
                            session.bind_turn(turn)
                            await self._turn_manager.start_turn(session, turn)
                            await self._server._dispatch_event(  # noqa: SLF001
                                "session_start",
                                SessionStartEvent(
                                    conversation_id=conversation_id,
                                    metadata=metadata,
                                ),
                                session,
                                turn,
                            )
                        elif event.event_type == byova_common_pb2.EventInput.SESSION_END:
                            if session and turn:
                                await self._server._dispatch_event(  # noqa: SLF001
                                    "session_end",
                                    SessionEndEvent(reason="webex_terminate"),
                                    session,
                                    turn,
                                )
                            await self._store.release_session(conversation_id)
                            return
                        elif event.event_type == byova_common_pb2.EventInput.NO_INPUT:
                            self._turn_manager.cancel_no_input_timer(turn) if turn else None

                    elif request.HasField("audio_input") and session and turn:
                        audio = request.audio_input
                        self._turn_manager.cancel_no_input_timer(turn)
                        await self._turn_manager.on_inbound_audio(
                            session, turn, is_first=first_audio
                        )
                        first_audio = False
                        event = AudioInputEvent(
                            audio=audio.caller_audio,
                            encoding="mulaw",
                            sample_rate=audio.sample_rate_hertz or self._config.sample_rate,
                        )
                        await self._server._dispatch_event("audio_input", event, session, turn)  # noqa: SLF001
                        session._resolve_input(event)

                    elif request.HasField("dtmf_input") and session and turn:
                        digits = "".join(
                            _DTMF_MAP.get(d, "") for d in request.dtmf_input.dtmf_events
                        )
                        if digits:
                            event = DtmfInputEvent(digits=digits)
                            await self._server._dispatch_event("dtmf_input", event, session, turn)  # noqa: SLF001
                            session._resolve_input(event)

            except DuplicateTurnStreamError:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Duplicate turn stream")
            except AuthenticationError:
                context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                context.set_details("Invalid token")
            except Exception as exc:
                logger.exception("ProcessCallerInput failed")
                if session and turn:
                    await self._server._handle_handler_error(exc, session, turn)  # noqa: SLF001
            finally:
                if conversation_id:
                    await self._store.unregister_stream(conversation_id, stream_id)
                stream_closed.set()
                await response_queue.put(None)

        reader_task = asyncio.create_task(request_reader())

        try:
            while True:
                response = await response_queue.get()
                if response is None:
                    break
                yield response
        finally:
            reader_task.cancel()
            try:
                await reader_task
            except asyncio.CancelledError:
                pass

    async def ListVirtualAgents(  # noqa: N802
        self,
        request: byova_common_pb2.ListVARequest,
        context: grpc.aio.ServicerContext,
    ) -> byova_common_pb2.ListVAResponse:
        """Return empty agent list by default."""
        _ = request
        _ = context
        return byova_common_pb2.ListVAResponse()

    async def _verify_context(self, context: grpc.aio.ServicerContext) -> None:
        metadata = dict(context.invocation_metadata())
        token = metadata.get("authorization", "")
        if token.lower().startswith("bearer "):
            token = token[7:]
        if not token:
            raise AuthenticationError("Missing authorization token")
        try:
            self._verifier.verify(token)
        except ValueError as exc:
            raise AuthenticationError(str(exc)) from exc


def _struct_to_dict(struct: Any) -> dict[str, Any]:
    if struct is None:
        return {}
    from google.protobuf.json_format import MessageToDict

    return MessageToDict(struct)  # type: ignore[no-any-return]


def register_service(grpc_server: grpc.aio.Server, media_server: BYOVAMediaServer) -> None:
    """Register the VoiceVirtualAgent servicer."""
    add_VoiceVirtualAgentServicer_to_server(  # type: ignore[no-untyped-call]
        VoiceVirtualAgentService(media_server),
        grpc_server,
    )
