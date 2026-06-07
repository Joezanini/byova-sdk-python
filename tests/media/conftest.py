"""Shared fixtures for media server tests."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from webex_byova.media.config import MediaServerConfig
from webex_byova.media.server import BYOVAMediaServer


@pytest.fixture
def media_config() -> MediaServerConfig:
    """Ephemeral port, token verification disabled for unit tests."""
    return MediaServerConfig(host="127.0.0.1", port=0, verify_tokens=False)


@pytest.fixture
async def media_server(media_config: MediaServerConfig) -> AsyncIterator[BYOVAMediaServer]:
    """Start media server on ephemeral port."""
    server = BYOVAMediaServer(media_config)
    await server.start()
    try:
        yield server
    finally:
        await server.stop()
