"""Media server configuration."""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from webex_byova.media.exceptions import MediaConfigError

AudioMode = Literal["chunked", "full"]
InputMode = Literal["voice", "dtmf", "mixed"]
OverflowPolicy = Literal["disconnect", "drop_oldest"]


class MediaServerConfig(BaseModel):
    """Validated server-wide settings for the BYOVA media server."""

    host: str = "0.0.0.0"
    port: int = Field(default=50051, ge=0, le=65535)
    tls_cert: str | None = None
    tls_key: str | None = None
    audio_mode: AudioMode = "chunked"
    encoding: Literal["mulaw"] = "mulaw"
    sample_rate: Literal[8000, 16000] = 8000
    channels: int = Field(default=1, ge=1, le=1)
    chunk_size_ms: int = Field(default=20, ge=10, le=100)
    input_mode: InputMode = "voice"
    barge_in_enabled: bool = False
    no_input_timeout: float = Field(default=5.0, gt=0)
    turn_disconnect_timeout: float | None = None
    end_of_input_silence_ms: int = Field(default=500, ge=0)
    max_session_duration: float | None = Field(default=3600.0, gt=0)
    verify_tokens: bool = True
    proxy_buffer_limit: int = Field(default=65536, gt=0)
    proxy_overflow_policy: OverflowPolicy = "disconnect"
    log_level: str = "INFO"

    @model_validator(mode="after")
    def _validate_tls_pair(self) -> MediaServerConfig:
        if (self.tls_cert is None) ^ (self.tls_key is None):
            raise MediaConfigError("tls_cert and tls_key must both be set or both omitted")
        return self

    @property
    def chunk_bytes(self) -> int:
        """Raw μ-law bytes per outbound chunk."""
        samples = int(self.sample_rate * self.chunk_size_ms / 1000)
        return samples * self.channels

    @classmethod
    def from_env(cls) -> MediaServerConfig:
        """Build configuration from ``WEBEX_MEDIA_*`` environment variables."""
        env = os.environ

        def _bool(key: str, default: bool) -> bool:
            raw = env.get(key)
            if raw is None:
                return default
            return raw.strip().lower() in {"1", "true", "yes", "on"}

        def _float(key: str, default: float | None) -> float | None:
            raw = env.get(key)
            if raw is None or raw == "":
                return default
            return float(raw)

        def _int(key: str, default: int) -> int:
            raw = env.get(key)
            return int(raw) if raw is not None else default

        turn_timeout = env.get("WEBEX_MEDIA_TURN_DISCONNECT_TIMEOUT")
        max_duration = env.get("WEBEX_MEDIA_MAX_SESSION_DURATION")

        return cls(
            host=env.get("WEBEX_MEDIA_HOST", "0.0.0.0"),
            port=_int("WEBEX_MEDIA_PORT", 50051),
            tls_cert=env.get("WEBEX_MEDIA_TLS_CERT"),
            tls_key=env.get("WEBEX_MEDIA_TLS_KEY"),
            audio_mode=env.get("WEBEX_MEDIA_AUDIO_MODE", "chunked"),  # type: ignore[arg-type]
            sample_rate=_int("WEBEX_MEDIA_SAMPLE_RATE", 8000),  # type: ignore[arg-type]
            input_mode=env.get("WEBEX_MEDIA_INPUT_MODE", "voice"),  # type: ignore[arg-type]
            barge_in_enabled=_bool("WEBEX_MEDIA_BARGE_IN_ENABLED", False),
            no_input_timeout=_float("WEBEX_MEDIA_NO_INPUT_TIMEOUT", 5.0) or 5.0,
            turn_disconnect_timeout=float(turn_timeout) if turn_timeout else None,
            end_of_input_silence_ms=_int("WEBEX_MEDIA_END_OF_INPUT_SILENCE_MS", 500),
            max_session_duration=(
                None
                if max_duration == "none"
                else _float("WEBEX_MEDIA_MAX_SESSION_DURATION", 3600.0)
            ),
            verify_tokens=_bool("WEBEX_MEDIA_VERIFY_TOKENS", True),
            proxy_buffer_limit=_int("WEBEX_MEDIA_PROXY_BUFFER_LIMIT", 65536),
            proxy_overflow_policy=env.get("WEBEX_MEDIA_PROXY_OVERFLOW_POLICY", "disconnect"),  # type: ignore[arg-type]
            log_level=env.get("WEBEX_MEDIA_LOG_LEVEL", "INFO"),
        )
