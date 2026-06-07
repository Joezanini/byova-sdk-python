"""WebSocket proxy connector."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from webex_byova.media.events import MediaEvent
from webex_byova.media.exceptions import ProxyBufferOverflowError, ProxyConnectionError
from webex_byova.media.proxy.adapter import DefaultProxyAdapter, ProxyAdapter

if TYPE_CHECKING:
    from webex_byova.media.server import BYOVAMediaServer
    from webex_byova.media.session import MediaSession

logger = logging.getLogger(__name__)


class WebSocketProxyConnector:
    """Bridge media sessions to an external WebSocket voice AI backend."""

    def __init__(
        self,
        url: str,
        adapter: ProxyAdapter | None = None,
        *,
        reconnect: bool = False,
        connect_timeout: float = 10.0,
    ) -> None:
        self.url = url
        self.adapter = adapter or DefaultProxyAdapter()
        self.reconnect = reconnect
        self.connect_timeout = connect_timeout
        self._server: BYOVAMediaServer | None = None
        self._connections: dict[str, Any] = {}
        self._buffers: dict[str, bytearray] = {}

    def attach(self, server: BYOVAMediaServer) -> None:
        """Attach to a media server instance."""
        self._server = server

    async def forward_event(self, event: MediaEvent, session: MediaSession) -> None:
        """Forward SDK event to backend WebSocket."""
        if self._server is None:
            return
        try:
            import websockets
        except ImportError as exc:
            raise ProxyConnectionError("websockets package required for proxy") from exc

        conv_id = session.conversation_id
        ws = self._connections.get(conv_id)
        if ws is None:
            try:
                ws = await asyncio.wait_for(
                    websockets.connect(self.url),
                    timeout=self.connect_timeout,
                )
            except Exception as exc:
                raise ProxyConnectionError(f"Failed to connect to {self.url}") from exc
            self._connections[conv_id] = ws
            asyncio.create_task(self._read_loop(ws, session))

        message = self.adapter.to_backend(event, session)
        encoded = message.encode() if isinstance(message, str) else message
        buf = self._buffers.setdefault(conv_id, bytearray())
        limit = self._server.config.proxy_buffer_limit
        if len(buf) + len(encoded) > limit:
            if self._server.config.proxy_overflow_policy == "drop_oldest":
                overflow = len(buf) + len(encoded) - limit
                del buf[:overflow]
                logger.warning("Proxy buffer overflow: dropped oldest %d bytes", overflow)
            else:
                await self.disconnect_session(conv_id)
                raise ProxyBufferOverflowError("Proxy buffer limit exceeded")
        buf.extend(encoded)
        if ws is not None:
            await ws.send(message)

    async def _read_loop(self, ws: Any, session: MediaSession) -> None:
        try:
            async for message in ws:
                prompt = self.adapter.from_backend(message, session)
                if prompt is None:
                    await session.end_session(reason="backend_end")
                    continue
                if session.active_turn is not None:
                    await session.active_turn.play_prompt(
                        text=prompt.text,
                        audio=prompt.audio,
                        ssml=prompt.ssml,
                        barge_in=prompt.barge_in,
                    )
        except Exception:
            logger.exception("Proxy read loop failed for %s", session.conversation_id)
        finally:
            await self.disconnect_session(session.conversation_id)

    async def disconnect_session(self, conversation_id: str) -> None:
        """Close backend connection for a session."""
        ws = self._connections.pop(conversation_id, None)
        self._buffers.pop(conversation_id, None)
        if ws is not None:
            await ws.close()
