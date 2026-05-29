"""Authentication models."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field


class IntegrationCredentials(BaseModel):
    """Developer-supplied Integration OAuth client credentials."""

    client_id: str
    client_secret: str
    redirect_uri: str = "http://127.0.0.1:8765/callback"


class ServiceAppCredentials(BaseModel):
    """Developer-supplied Service App OAuth client credentials."""

    client_id: str
    client_secret: str


class OAuthTokens(BaseModel):
    """OAuth token response from /v1/access_token."""

    access_token: str
    expires_in: int
    token_type: str = "Bearer"
    refresh_token: str | None = None
    refresh_token_expires_in: int | None = None
    obtained_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def expires_at(self) -> datetime:
        return self.obtained_at + timedelta(seconds=self.expires_in)

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        elapsed = (datetime.now(timezone.utc) - self.obtained_at).total_seconds()
        return elapsed >= (self.expires_in - buffer_seconds)


class ServiceAppTokens(BaseModel):
    """Service App token pair from POST /applications/{id}/token."""

    access_token: str
    expires_in: int
    token_type: str = "Bearer"
    refresh_token: str | None = None
    refresh_token_expires_in: int | None = None
    obtained_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        elapsed = (datetime.now(timezone.utc) - self.obtained_at).total_seconds()
        return elapsed >= (self.expires_in - buffer_seconds)
