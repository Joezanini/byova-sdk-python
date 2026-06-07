"""Prompt request and response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class PromptRequest(BaseModel):
    """Developer request to play audio or TTS to the caller."""

    text: str | None = None
    ssml: str | None = None
    audio: bytes | None = None
    audio_path: str | None = None
    barge_in: bool | None = None

    model_config = {"arbitrary_types_allowed": True}


class PromptResponse(BaseModel):
    """Result of a ``play_prompt`` operation."""

    prompt_id: str
    status: Literal["queued", "playing", "completed", "cancelled"] = "queued"
    chunks_sent: int = 0
