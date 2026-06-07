"""In-memory session index keyed by conversation_id."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

from webex_byova.media.exceptions import DuplicateTurnStreamError

if TYPE_CHECKING:
    from webex_byova.media.config import MediaServerConfig
    from webex_byova.media.server import BYOVAMediaServer
    from webex_byova.media.session import MediaSession


class ConversationStore:
    """Track active sessions and reject duplicate turn streams."""

    def __init__(self, *, ttl_seconds: float = 3600.0) -> None:
        self._sessions: dict[str, MediaSession] = {}
        self._active_streams: dict[str, str] = {}
        self._ttl_seconds = ttl_seconds
        self._last_access: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(
        self,
        conversation_id: str,
        factory: type[MediaSession],
        *,
        config: MediaServerConfig,
        server: BYOVAMediaServer,
        metadata: dict[str, Any] | None = None,
    ) -> MediaSession:
        """Return existing session or create via factory."""
        async with self._lock:
            self._cleanup_expired_unlocked()
            session = self._sessions.get(conversation_id)
            if session is None:
                session = factory(
                    conversation_id=conversation_id,
                    config=config,
                    server=server,
                    metadata=metadata,
                )
                self._sessions[conversation_id] = session
            self._last_access[conversation_id] = time.monotonic()
            return session

    async def get(self, conversation_id: str) -> MediaSession | None:
        """Return session if present."""
        async with self._lock:
            self._last_access[conversation_id] = time.monotonic()
            return self._sessions.get(conversation_id)

    async def register_stream(self, conversation_id: str, stream_id: str) -> None:
        """Register an active turn stream; reject duplicates."""
        async with self._lock:
            existing = self._active_streams.get(conversation_id)
            if existing is not None and existing != stream_id:
                raise DuplicateTurnStreamError(
                    f"Duplicate turn stream for conversation {conversation_id}"
                )
            self._active_streams[conversation_id] = stream_id

    async def unregister_stream(self, conversation_id: str, stream_id: str) -> None:
        """Remove stream registration when turn closes."""
        async with self._lock:
            if self._active_streams.get(conversation_id) == stream_id:
                del self._active_streams[conversation_id]

    async def release_session(self, conversation_id: str) -> None:
        """Remove session and stream tracking."""
        async with self._lock:
            self._sessions.pop(conversation_id, None)
            self._active_streams.pop(conversation_id, None)
            self._last_access.pop(conversation_id, None)

    def _cleanup_expired_unlocked(self) -> None:
        now = time.monotonic()
        expired = [cid for cid, last in self._last_access.items() if now - last > self._ttl_seconds]
        for cid in expired:
            self._sessions.pop(cid, None)
            self._active_streams.pop(cid, None)
            self._last_access.pop(cid, None)
