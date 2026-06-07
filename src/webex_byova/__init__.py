"""Webex BYOVA / BYODS Python SDK."""

from webex_byova._version import __version__
from webex_byova.client import BYOVA
from webex_byova.config import BYOVAConfig
from webex_byova.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    WebexBYOVAError,
)

try:
    from webex_byova.media import BYOVAMediaServer, MediaServerConfig
except ImportError:  # pragma: no cover - media extra not installed
    BYOVAMediaServer = None  # type: ignore[misc, assignment]
    MediaServerConfig = None  # type: ignore[misc, assignment]

__all__ = [
    "BYOVA",
    "BYOVAConfig",
    "WebexBYOVAError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "__version__",
    "BYOVAMediaServer",
    "MediaServerConfig",
]
