"""WebSocket proxy bridge example."""

import asyncio

from webex_byova.media import BYOVAMediaServer, MediaServerConfig, WebSocketProxyConnector


async def main() -> None:
    server = BYOVAMediaServer(MediaServerConfig(verify_tokens=False))
    server.use_proxy(WebSocketProxyConnector(url="wss://your-ai-backend.example/ws"))

    async with server:
        await server._grpc_server.wait_for_termination()  # noqa: SLF001


if __name__ == "__main__":
    asyncio.run(main())
