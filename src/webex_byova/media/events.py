"""Normalized media events surfaced to developer handlers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class SessionStartEvent(BaseModel):
    """Fired when a new call session begins."""

    type: Literal["session_start"] = "session_start"
    conversation_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AudioInputEvent(BaseModel):
    """Inbound caller audio chunk."""

    type: Literal["audio_input"] = "audio_input"
    audio: bytes
    encoding: str = "mulaw"
    sample_rate: int = 8000
    is_final: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DtmfInputEvent(BaseModel):
    """Inbound DTMF digits."""

    type: Literal["dtmf_input"] = "dtmf_input"
    digits: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BargeInEvent(BaseModel):
    """Caller interrupted bot playback."""

    type: Literal["barge_in"] = "barge_in"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cancelled_prompt_id: str | None = None


class NoInputEvent(BaseModel):
    """Caller did not provide input within the timeout."""

    type: Literal["no_input"] = "no_input"
    timeout_seconds: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TurnStartedEvent(BaseModel):
    """A new turn stream opened."""

    type: Literal["turn_started"] = "turn_started"
    turn_id: str
    turn_number: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TurnEndedEvent(BaseModel):
    """Turn stream closed."""

    type: Literal["turn_ended"] = "turn_ended"
    turn_id: str
    reason: str = "completed"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionEndEvent(BaseModel):
    """Session terminated."""

    type: Literal["session_end"] = "session_end"
    reason: str = "completed"
    duration_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorEvent(BaseModel):
    """Recoverable or fatal handler/server error."""

    type: Literal["error"] = "error"
    code: str
    message: str
    recoverable: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


MediaEvent = (
    SessionStartEvent
    | AudioInputEvent
    | DtmfInputEvent
    | BargeInEvent
    | NoInputEvent
    | TurnStartedEvent
    | TurnEndedEvent
    | SessionEndEvent
    | ErrorEvent
)
