"""Media server exception hierarchy."""

from __future__ import annotations

from webex_byova.exceptions import WebexBYOVAError


class MediaServerError(WebexBYOVAError):
    """Base exception for media server errors."""


class MediaConfigError(MediaServerError):
    """Raised when ``MediaServerConfig`` validation fails."""


class DuplicateTurnStreamError(MediaServerError):
    """Raised when a duplicate concurrent turn stream is rejected."""


class PromptValidationError(MediaServerError):
    """Raised when prompt audio format or content is invalid."""


class ProxyConnectionError(MediaServerError):
    """Raised when the WebSocket proxy backend is unreachable."""


class ProxyBufferOverflowError(MediaServerError):
    """Raised when the proxy buffer exceeds configured limits."""
