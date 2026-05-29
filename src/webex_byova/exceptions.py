"""Exception hierarchy for Webex BYOVA SDK."""

from __future__ import annotations

from typing import Any


class WebexBYOVAError(Exception):
    """Base exception for all SDK errors."""

    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(WebexBYOVAError):
    """Raised when authentication fails (401/403)."""


class NotFoundError(WebexBYOVAError):
    """Raised when a resource is not found (404)."""


class ValidationError(WebexBYOVAError):
    """Raised when the request is invalid (400/409/415)."""


class RateLimitError(WebexBYOVAError):
    """Raised when rate limited (429)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 429,
        body: Any = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, body=body)
        self.retry_after = retry_after


class OAuthRedirectError(WebexBYOVAError):
    """Raised when OAuth redirect fails or user denies access."""


class OAuthRedirectTimeout(WebexBYOVAError):
    """Raised when OAuth redirect listener times out."""


class OrgNotRegisteredError(WebexBYOVAError):
    """Raised when no Service App tokens exist for the requested org."""
