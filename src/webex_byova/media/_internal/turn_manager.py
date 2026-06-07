"""Turn and playback state machine."""

from __future__ import annotations

import asyncio
import uuid
from collections import deque
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from webex_byova.media.events import BargeInEvent, NoInputEvent, TurnEndedEvent, TurnStartedEvent

if TYPE_CHECKING:
    from webex_byova.media.config import MediaServerConfig
    from webex_byova.media.session import MediaSession, TurnContext


class PlaybackState(str, Enum):
    """Prompt playback lifecycle."""

    IDLE = "idle"
    PLAYING = "playing"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class TurnState(str, Enum):
    """Turn stream lifecycle."""

    OPEN = "open"
    COLLECTING = "collecting"
    RESPONDING = "responding"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class AudioChunk:
    """Internal outbound audio chunk."""

    data: bytes
    encoding: str = "mulaw"
    sample_rate: int = 8000
    channels: int = 1
    index: int = 0
    is_final: bool = False


@dataclass
class TurnRuntime:
    """Mutable turn runtime state."""

    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_number: int = 1
    state: TurnState = TurnState.OPEN
    playback_state: PlaybackState = PlaybackState.IDLE
    outbound_queue: deque[AudioChunk] = field(default_factory=deque)
    is_final: bool = False
    is_active: bool = True
    current_prompt_id: str | None = None
    playback_task: asyncio.Task[None] | None = None
    input_started: bool = False
    no_input_task: asyncio.Task[None] | None = None


class TurnManager:
    """Manage turn boundaries, timeouts, and barge-in."""

    def __init__(
        self,
        config: MediaServerConfig,
        *,
        dispatch: Callable[[str, Any, MediaSession, TurnContext], Coroutine[Any, Any, None]],
    ) -> None:
        self._config = config
        self._dispatch = dispatch

    async def start_turn(self, session: MediaSession, turn: TurnContext) -> None:
        """Initialize turn and emit turn_started."""
        runtime = turn._runtime
        runtime.state = TurnState.OPEN
        runtime.is_active = True
        await self._dispatch(
            "turn_started",
            TurnStartedEvent(turn_id=runtime.turn_id, turn_number=runtime.turn_number),
            session,
            turn,
        )
        await self._arm_no_input_timer(session, turn)

    async def on_inbound_audio(
        self,
        session: MediaSession,
        turn: TurnContext,
        *,
        is_first: bool,
    ) -> None:
        """Handle inbound audio; trigger barge-in and input boundaries."""
        runtime = turn._runtime
        if is_first and not runtime.input_started:
            runtime.input_started = True
            runtime.state = TurnState.COLLECTING
            await turn._send_platform(build_start_of_input())  # noqa: SLF001
        if self._config.barge_in_enabled and runtime.playback_state == PlaybackState.PLAYING:
            await self.handle_barge_in(session, turn)

    async def handle_barge_in(self, session: MediaSession, turn: TurnContext) -> None:
        """Cancel playback and flush outbound queue (PC-002)."""
        runtime = turn._runtime
        if runtime.playback_state != PlaybackState.PLAYING:
            return
        runtime.playback_state = PlaybackState.CANCELLED
        runtime.outbound_queue.clear()
        cancelled_id = runtime.current_prompt_id
        runtime.current_prompt_id = None
        await self._dispatch(
            "barge_in",
            BargeInEvent(cancelled_prompt_id=cancelled_id),
            session,
            turn,
        )

    async def mark_input_complete(self, session: MediaSession, turn: TurnContext) -> None:
        """Send END_OF_INPUT when utterance ends."""
        await turn._send_platform(build_end_of_input())  # noqa: SLF001

    async def end_turn(
        self, session: MediaSession, turn: TurnContext, *, reason: str = "completed"
    ) -> None:
        """Close turn and emit turn_ended."""
        runtime = turn._runtime
        if runtime.state == TurnState.CLOSED:
            return
        runtime.state = TurnState.CLOSING
        runtime.is_active = False
        runtime.is_final = True
        if runtime.no_input_task and not runtime.no_input_task.done():
            runtime.no_input_task.cancel()
        await turn._close_stream()  # noqa: SLF001
        runtime.state = TurnState.CLOSED
        await self._dispatch(
            "turn_ended",
            TurnEndedEvent(turn_id=runtime.turn_id, reason=reason),
            session,
            turn,
        )

    async def _arm_no_input_timer(self, session: MediaSession, turn: TurnContext) -> None:
        runtime = turn._runtime
        timeout = self._config.turn_disconnect_timeout or self._config.no_input_timeout

        async def _fire() -> None:
            await asyncio.sleep(timeout)
            if runtime.state in {TurnState.CLOSED, TurnState.CLOSING}:
                return
            await self._dispatch(
                "no_input",
                NoInputEvent(timeout_seconds=timeout),
                session,
                turn,
            )
            await turn._send_platform(build_no_input_event())  # noqa: SLF001

        runtime.no_input_task = asyncio.create_task(_fire())

    def cancel_no_input_timer(self, turn: TurnContext) -> None:
        """Cancel pending no-input timer when input arrives."""
        task = turn._runtime.no_input_task
        if task and not task.done():
            task.cancel()


def build_start_of_input() -> Any:
    from webex_byova.media._internal.protocol import build_start_of_input as _build

    return _build()


def build_end_of_input() -> Any:
    from webex_byova.media._internal.protocol import build_end_of_input as _build

    return _build()


def build_no_input_event() -> Any:
    from webex_byova.media._internal.protocol import build_no_input_event as _build

    return _build()
