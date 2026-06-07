"""BYOVA media server lifecycle and handler registry."""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

import grpc

from webex_byova.media._internal.conversation_store import ConversationStore
from webex_byova.media._internal.grpc_service import register_service
from webex_byova.media.config import MediaServerConfig
from webex_byova.media.events import ErrorEvent, MediaEvent, SessionEndEvent
from webex_byova.media.session import MediaSession, TurnContext

Handler = Callable[..., Awaitable[None] | None]

logger = logging.getLogger(__name__)


class BYOVAMediaServer:
    """Developer-hosted BYOVA gRPC media server."""

    def __init__(self, config: MediaServerConfig | None = None) -> None:
        self.config = config or MediaServerConfig()
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._grpc_server: grpc.aio.Server | None = None
        self._conversation_store = ConversationStore(
            ttl_seconds=self.config.max_session_duration or 3600.0
        )
        self._proxy = None
        self._running = False

    @classmethod
    def from_env(cls) -> BYOVAMediaServer:
        """Construct server from ``WEBEX_MEDIA_*`` environment variables."""
        return cls(MediaServerConfig.from_env())

    def on(self, event: str) -> Callable[[Handler], Handler]:
        """Decorator to register an async or sync event handler."""

        def decorator(fn: Handler) -> Handler:
            self._handlers[event].append(fn)
            return fn

        return decorator

    def handler(self, event: str) -> Callable[[Handler], Handler]:
        """Alias for :meth:`on`."""
        return self.on(event)

    def use_proxy(self, connector: Any) -> None:
        """Attach a WebSocket proxy connector."""
        self._proxy = connector
        connector.attach(self)

    async def start(self) -> None:
        """Bind and start the gRPC server."""
        if self._running:
            return
        self._grpc_server = grpc.aio.server()
        register_service(self._grpc_server, self)
        address = f"{self.config.host}:{self.config.port}"
        if self.config.tls_cert and self.config.tls_key:
            with open(self.config.tls_cert, "rb") as cert, open(self.config.tls_key, "rb") as key:
                credentials = grpc.ssl_server_credentials([(key.read(), cert.read())])
            bound_port = self._grpc_server.add_secure_port(address, credentials)
        else:
            bound_port = self._grpc_server.add_insecure_port(address)
        if self.config.port == 0 and bound_port:
            self.config = self.config.model_copy(update={"port": bound_port})
        await self._grpc_server.start()
        self._running = True
        logging.getLogger(__name__).info(
            "BYOVA media server listening on %s:%s", self.config.host, self.config.port
        )

    async def stop(self, grace: float = 5.0) -> None:
        """Gracefully stop the server."""
        if self._grpc_server is not None:
            await self._grpc_server.stop(grace)
            self._grpc_server = None
        self._running = False

    async def serve(self) -> None:
        """Start the server and wait until interrupted."""
        await self.start()
        try:
            await self._grpc_server.wait_for_termination()  # type: ignore[union-attr]
        except asyncio.CancelledError:
            await self.stop()

    async def __aenter__(self) -> BYOVAMediaServer:
        await self.start()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.stop()

    async def _dispatch_event(
        self,
        event_name: str,
        event: MediaEvent,
        session: MediaSession,
        turn: TurnContext | None,
    ) -> None:
        handlers = self._handlers.get(event_name, [])
        for fn in handlers:
            try:
                await self._invoke_handler(fn, event, session, turn)
            except Exception as exc:
                await self._handle_handler_error(exc, session, turn)
                raise

        if self._proxy is not None:
            await self._proxy.forward_event(event, session)

    async def _invoke_handler(
        self,
        fn: Handler,
        event: MediaEvent,
        session: MediaSession,
        turn: TurnContext | None,
    ) -> None:
        sig = inspect.signature(fn)
        kwargs: dict[str, Any] = {}
        for name in sig.parameters:
            if name in {"event", "evt"}:
                kwargs[name] = event
            elif name == "session":
                kwargs[name] = session
            elif name in {"turn", "ctx"}:
                kwargs[name] = turn

        if inspect.iscoroutinefunction(fn):
            await fn(**kwargs)
        else:
            await asyncio.to_thread(fn, **kwargs)

    async def _handle_handler_error(
        self,
        exc: Exception,
        session: MediaSession,
        turn: TurnContext | None,
    ) -> None:
        error = ErrorEvent(code=type(exc).__name__, message=str(exc), recoverable=False)
        for fn in self._handlers.get("error", []):
            try:
                await self._invoke_handler(fn, error, session, turn)
            except Exception:
                logger.exception("Error handler failed")
        from webex_byova.media.session import SessionState

        session.state = SessionState.ENDING
        await self._release_session(session.conversation_id, str(exc))

    async def _release_session(self, conversation_id: str, reason: str) -> None:
        session = await self._conversation_store.get(conversation_id)
        if session is None:
            return
        turn = session.active_turn
        if turn is not None:
            await self._dispatch_event(
                "session_end",
                SessionEndEvent(reason=reason),
                session,
                turn,
            )
        await self._conversation_store.release_session(conversation_id)
