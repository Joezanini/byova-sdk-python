"""Minimal BYOVA media server hello-world example."""

import asyncio

from webex_byova.media import BYOVAMediaServer, MediaServerConfig


async def main() -> None:
    config = MediaServerConfig(host="0.0.0.0", port=50051, verify_tokens=False)
    server = BYOVAMediaServer(config)

    @server.on("session_start")
    async def greet(session, turn) -> None:
        await turn.play_prompt(text="Hello from webex-byova media server")

    async with server:
        print(f"Media server listening on {config.host}:{config.port}")
        await server._grpc_server.wait_for_termination()  # noqa: SLF001


if __name__ == "__main__":
    asyncio.run(main())
