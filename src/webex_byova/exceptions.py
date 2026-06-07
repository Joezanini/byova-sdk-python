"""Exception hierarchy for Webex BYOVA SDK."""

from __future__ import annotations

from typing import Any


class WebexBYOVAError(Exception):
    """Base exception for all SDK errors.

    Attributes:
        status_code: HTTP status code from the Webex API, if applicable.
        body: Raw response body from the Webex API, if available.
    """

    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code from the failed request.
            body: Parsed or raw response body from the failed request.
        """
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(WebexBYOVAError):
    """Raised when authentication fails (HTTP 401 or 403)."""


class NotFoundError(WebexBYOVAError):
    """Raised when a requested resource is not found (HTTP 404)."""


class ValidationError(WebexBYOVAError):
    """Raised when a request is invalid (HTTP 400, 409, or 415)."""


class RateLimitError(WebexBYOVAError):
    """Raised when the Webex API rate limit is exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying, from the ``Retry-After`` header.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 429,
        body: Any = None,
        retry_after: int | None = None,
    ) -> None:
        """Initialize the rate limit exception.

        Args:
            message: Human-readable error description.
            status_code: HTTP status code (defaults to 429).
            body: Raw response body from the failed request.
            retry_after: Recommended retry delay in seconds.
        """
        super().__init__(message, status_code=status_code, body=body)
        self.retry_after = retry_after


class OAuthRedirectError(WebexBYOVAError):
    """Raised when the OAuth redirect fails or the user denies access."""


class OAuthRedirectTimeout(WebexBYOVAError):
    """Raised when the local OAuth redirect listener times out."""


class OrgNotRegisteredError(WebexBYOVAError):
    """Raised when no Service App tokens exist for the requested organization."""
