"""Combined BYODS API client and media server example."""

import asyncio

from webex_byova import BYOVA, BYOVAConfig
from webex_byova.media import BYOVAMediaServer, MediaServerConfig


async def main() -> None:
    # BYODS client for data source registration (configure credentials separately)
    _byova = BYOVA  # noqa: F841 — illustrate coexistence
    _config = BYOVAConfig()  # noqa: F841

    media = BYOVAMediaServer(MediaServerConfig(verify_tokens=False))

    @media.on("session_start")
    async def handle(session, turn) -> None:
        await turn.play_prompt(text="BYODS and media server running together.")

    async with media:
        await media._grpc_server.wait_for_termination()  # noqa: SLF001


if __name__ == "__main__":
    asyncio.run(main())
