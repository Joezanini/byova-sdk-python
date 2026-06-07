"""Multi-turn dialog example."""

import asyncio

from webex_byova.media import BYOVAMediaServer, MediaServerConfig


async def main() -> None:
    server = BYOVAMediaServer(MediaServerConfig(verify_tokens=False))

    @server.on("session_start")
    async def dialog(session, turn) -> None:
        await turn.play_prompt(text=f"Welcome. Turn {turn.turn_number}.")

    @server.on("audio_input")
    async def on_audio(event, session, turn) -> None:
        await turn.play_prompt(text="Thanks, goodbye.")
        await session.end_session()

    async with server:
        await server._grpc_server.wait_for_termination()  # noqa: SLF001


if __name__ == "__main__":
    asyncio.run(main())
