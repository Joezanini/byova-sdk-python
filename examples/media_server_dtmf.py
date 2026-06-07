"""DTMF collection example."""

import asyncio

from webex_byova.media import BYOVAMediaServer, MediaServerConfig


async def main() -> None:
    config = MediaServerConfig(input_mode="dtmf", verify_tokens=False)
    server = BYOVAMediaServer(config)

    @server.on("session_start")
    async def collect(session, turn) -> None:
        await turn.play_prompt(text="Enter your account number followed by pound.")

    @server.on("dtmf_input")
    async def on_dtmf(event, session, turn) -> None:
        await turn.play_prompt(text=f"You entered {event.digits}")
        await turn.end_turn()

    async with server:
        await server._grpc_server.wait_for_termination()  # noqa: SLF001


if __name__ == "__main__":
    asyncio.run(main())
