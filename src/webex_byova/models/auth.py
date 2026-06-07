"""Authentication models."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field


class IntegrationCredentials(BaseModel):
    """Developer-supplied Integration OAuth client credentials.

    Attributes:
        client_id: Integration client ID from Webex Developer portal.
        client_secret: Integration client secret.
        redirect_uri: Registered OAuth redirect URI for the Integration.
    """

    client_id: str = Field(description="Integration client ID from Webex Developer portal.")
    client_secret: str = Field(description="Integration client secret.")
    redirect_uri: str = Field(
        default="http://127.0.0.1:8765/callback",
        description="Registered OAuth redirect URI for the Integration.",
    )


class ServiceAppCredentials(BaseModel):
    """Developer-supplied Service App OAuth client credentials.

    Attributes:
        client_id: Service App client ID from Webex Developer portal.
        client_secret: Service App client secret.
    """

    client_id: str = Field(description="Service App client ID from Webex Developer portal.")
    client_secret: str = Field(description="Service App client secret.")


class OAuthTokens(BaseModel):
    """OAuth token response from ``/v1/access_token``.

    Attributes:
        access_token: Bearer access token for Integration API calls.
        expires_in: Access token lifetime in seconds.
        token_type: Token type (typically ``Bearer``).
        refresh_token: Refresh token for obtaining new access tokens.
        refresh_token_expires_in: Refresh token lifetime in seconds, if provided.
        obtained_at: UTC timestamp when tokens were received.
    """

    access_token: str = Field(description="Bearer access token for Integration API calls.")
    expires_in: int = Field(description="Access token lifetime in seconds.")
    token_type: str = Field(default="Bearer", description="Token type (typically Bearer).")
    refresh_token: str | None = Field(
        default=None, description="Refresh token for obtaining new access tokens."
    )
    refresh_token_expires_in: int | None = Field(
        default=None, description="Refresh token lifetime in seconds, if provided."
    )
    obtained_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when tokens were received.",
    )

    @property
    def expires_at(self) -> datetime:
        """Return the UTC datetime when the access token expires."""
        return self.obtained_at + timedelta(seconds=self.expires_in)

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check whether the access token is expired or near expiry.

        Args:
            buffer_seconds: Refresh this many seconds before actual expiry.

        Returns:
            True if the token should be refreshed.
        """
        elapsed = (datetime.now(timezone.utc) - self.obtained_at).total_seconds()
        return elapsed >= (self.expires_in - buffer_seconds)


class ServiceAppTokens(BaseModel):
    """Service App token pair from ``POST /applications/{id}/token``.

    Attributes:
        access_token: Bearer access token for org-scoped API calls.
        expires_in: Access token lifetime in seconds.
        token_type: Token type (typically ``Bearer``).
        refresh_token: Refresh token for the org registration.
        refresh_token_expires_in: Refresh token lifetime in seconds, if provided.
        obtained_at: UTC timestamp when tokens were received.
    """

    access_token: str = Field(description="Bearer access token for org-scoped API calls.")
    expires_in: int = Field(description="Access token lifetime in seconds.")
    token_type: str = Field(default="Bearer", description="Token type (typically Bearer).")
    refresh_token: str | None = Field(
        default=None, description="Refresh token for the org registration."
    )
    refresh_token_expires_in: int | None = Field(
        default=None, description="Refresh token lifetime in seconds, if provided."
    )
    obtained_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when tokens were received.",
    )

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        """Check whether the access token is expired or near expiry.

        Args:
            buffer_seconds: Refresh this many seconds before actual expiry.

        Returns:
            True if the token should be refreshed.
        """
        elapsed = (datetime.now(timezone.utc) - self.obtained_at).total_seconds()
        return elapsed >= (self.expires_in - buffer_seconds)
