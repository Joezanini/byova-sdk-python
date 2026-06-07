"""Media session and turn context."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Callable, Coroutine
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from webex_byova.media._internal.audio import build_mulaw_wav, chunk_audio, ensure_raw_mulaw
from webex_byova.media._internal.protocol import build_audio_chunk_response, close_turn
from webex_byova.media._internal.turn_manager import PlaybackState, TurnRuntime, TurnState
from webex_byova.media.events import AudioInputEvent, DtmfInputEvent, TurnEndedEvent
from webex_byova.media.exceptions import PromptValidationError
from webex_byova.media.prompts import PromptResponse

if TYPE_CHECKING:
    from webex_byova.media.config import MediaServerConfig
    from webex_byova.media.server import BYOVAMediaServer


class SessionState(str, Enum):
    """Long-lived session lifecycle."""

    ACTIVE = "active"
    ENDING = "ending"
    ENDED = "ended"


class MediaSession:
    """Long-lived call state keyed by ``conversation_id``."""

    def __init__(
        self,
        *,
        conversation_id: str,
        config: MediaServerConfig,
        server: BYOVAMediaServer,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.conversation_id = conversation_id
        self.session_id = str(uuid.uuid4())
        self.metadata = metadata or {}
        self.started_at = datetime.now(timezone.utc)
        self.state = SessionState.ACTIVE
        self.turn_count = 0
        self._config = config
        self._server = server
        self._active_turn: TurnContext | None = None
        self._input_futures: list[asyncio.Future[AudioInputEvent | DtmfInputEvent]] = []

    @property
    def active_turn(self) -> TurnContext | None:
        """Currently active turn, if any."""
        return self._active_turn

    def bind_turn(self, turn: TurnContext) -> None:
        """Attach active turn context."""
        self.turn_count += 1
        self._active_turn = turn

    async def play_prompt(
        self,
        *,
        text: str | None = None,
        audio: bytes | None = None,
        ssml: str | None = None,
        barge_in: bool | None = None,
    ) -> PromptResponse:
        """Play prompt on the active turn."""
        if self._active_turn is None:
            raise PromptValidationError("No active turn for play_prompt")
        return await self._active_turn.play_prompt(
            text=text, audio=audio, ssml=ssml, barge_in=barge_in
        )

    async def collect_input(
        self,
        *,
        mode: str | None = None,
        timeout: float | None = None,
    ) -> AudioInputEvent | DtmfInputEvent:
        """Await caller input on the active turn."""
        if self._active_turn is None:
            raise PromptValidationError("No active turn for collect_input")
        return await self._active_turn.collect_input(mode=mode, timeout=timeout)

    async def end_session(self, reason: str = "completed") -> None:
        """Mark session ending and release resources."""
        self.state = SessionState.ENDING
        await self._server._release_session(self.conversation_id, reason)  # noqa: SLF001

    def _resolve_input(self, event: AudioInputEvent | DtmfInputEvent) -> None:
        for fut in list(self._input_futures):
            if not fut.done():
                fut.set_result(event)
        self._input_futures.clear()

    async def _wait_for_input(
        self,
        *,
        timeout: float | None,
    ) -> AudioInputEvent | DtmfInputEvent:
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[AudioInputEvent | DtmfInputEvent] = loop.create_future()
        self._input_futures.append(fut)
        try:
            if timeout is None:
                return await fut
            return await asyncio.wait_for(fut, timeout=timeout)
        finally:
            if fut in self._input_futures:
                self._input_futures.remove(fut)


class TurnContext:
    """Per-turn view during one bidirectional stream."""

    def __init__(
        self,
        *,
        session: MediaSession,
        config: MediaServerConfig,
        send_response: Callable[[Any], Coroutine[Any, Any, None]],
        close_stream: Callable[[], Coroutine[Any, Any, None]],
        turn_number: int,
    ) -> None:
        self.session = session
        self._config = config
        self._send_response = send_response
        self._close_stream_cb = close_stream
        self._runtime = TurnRuntime(turn_number=turn_number)

    @property
    def turn_id(self) -> str:
        """Unique turn identifier."""
        return self._runtime.turn_id

    @property
    def turn_number(self) -> int:
        """1-based turn index within the session."""
        return self._runtime.turn_number

    @property
    def is_active(self) -> bool:
        """Whether the turn stream is still open."""
        return self._runtime.is_active

    @property
    def is_final(self) -> bool:
        """Whether the turn closed with RESPONSE_FINAL."""
        return self._runtime.is_final

    async def play_prompt(
        self,
        *,
        text: str | None = None,
        audio: bytes | None = None,
        ssml: str | None = None,
        barge_in: bool | None = None,
    ) -> PromptResponse:
        """Encode, chunk, and send outbound prompt audio."""
        prompt_id = str(uuid.uuid4())
        self._runtime.current_prompt_id = prompt_id
        self._runtime.state = TurnState.RESPONDING
        barge = barge_in if barge_in is not None else self._config.barge_in_enabled

        raw = audio or b""
        if self._config.audio_mode == "full" and raw and not raw.startswith(b"RIFF"):
            raw = build_mulaw_wav(raw, sample_rate=self._config.sample_rate)
        elif self._config.audio_mode == "chunked" and raw:
            raw = ensure_raw_mulaw(raw, audio_mode=self._config.audio_mode)

        chunks = list(chunk_audio(raw, self._config.chunk_bytes)) if raw else []
        if not chunks and (text or ssml):
            chunks = [b""]

        self._runtime.playback_state = PlaybackState.PLAYING
        sent = 0
        for index, chunk in enumerate(chunks):
            if self._runtime.playback_state == PlaybackState.CANCELLED:
                return PromptResponse(prompt_id=prompt_id, status="cancelled", chunks_sent=sent)
            response = build_audio_chunk_response(
                chunk,
                config=self._config,
                is_final_chunk=False,
                barge_in=barge,
                text=text if index == 0 else None,
            )
            await self._send_response(response)
            sent += 1
            await asyncio.sleep(0)
            if self._runtime.playback_state == PlaybackState.CANCELLED:  # type: ignore[comparison-overlap]
                return PromptResponse(prompt_id=prompt_id, status="cancelled", chunks_sent=sent)

        self._runtime.playback_state = PlaybackState.COMPLETED
        await close_turn(self._send_response, config=self._config)
        await self._close_stream_cb()
        self._runtime.is_final = True
        self._runtime.is_active = False
        await self._emit_turn_ended("completed")
        return PromptResponse(prompt_id=prompt_id, status="completed", chunks_sent=sent)

    async def collect_input(
        self,
        *,
        mode: str | None = None,
        timeout: float | None = None,
    ) -> AudioInputEvent | DtmfInputEvent:
        """Wait for normalized caller input."""
        effective_timeout = timeout if timeout is not None else self._config.no_input_timeout
        _ = mode or self._config.input_mode
        return await self.session._wait_for_input(timeout=effective_timeout)

    async def end_turn(self) -> None:
        """Send RESPONSE_FINAL and close the turn stream."""
        await close_turn(self._send_response, config=self._config)
        await self._close_stream_cb()
        self._runtime.is_final = True
        self._runtime.is_active = False
        await self._emit_turn_ended("completed")

    async def _emit_turn_ended(self, reason: str) -> None:
        await self.session._server._dispatch_event(  # noqa: SLF001
            "turn_ended",
            TurnEndedEvent(turn_id=self.turn_id, reason=reason),
            self.session,
            self,
        )

    async def _send_platform(self, response: Any) -> None:
        await self._send_response(response)

    async def _close_stream(self) -> None:
        await self._close_stream_cb()
