"""Integration OAuth token management."""

from __future__ import annotations

import secrets
from urllib.parse import urlencode

from webex_byova._http import HttpClient
from webex_byova.auth.redirect_listener import wait_for_redirect
from webex_byova.auth.storage import TokenStorage
from webex_byova.config import BYOVAConfig
from webex_byova.exceptions import AuthenticationError
from webex_byova.models.auth import IntegrationCredentials, OAuthTokens

DEFAULT_INTEGRATION_SCOPES: list[str] = [
    "spark:all",
    "spark:applications_token",
    "application:webhooks_write",
    "application:webhooks_read",
]


class IntegrationTokenManager:
    """Manage Integration OAuth tokens (developer-initiated flow)."""

    def __init__(
        self,
        credentials: IntegrationCredentials,
        http: HttpClient,
        storage: TokenStorage,
        config: BYOVAConfig | None = None,
    ) -> None:
        self._credentials = credentials
        self._http = http
        self._storage = storage
        self._config = config or http.config

    @property
    def credentials(self) -> IntegrationCredentials:
        return self._credentials

    def get_authorization_url(
        self,
        scopes: list[str] | None = None,
        *,
        state: str | None = None,
    ) -> tuple[str, str]:
        """Build authorization URL. Returns (url, state)."""
        resolved_scopes = scopes if scopes is not None else DEFAULT_INTEGRATION_SCOPES
        csrf = state or secrets.token_urlsafe(16)
        params = {
            "client_id": self._credentials.client_id,
            "response_type": "code",
            "redirect_uri": self._credentials.redirect_uri,
            "scope": " ".join(resolved_scopes),
            "state": csrf,
        }
        url = f"{self._config.authorize_url}?{urlencode(params)}"
        return url, csrf

    def _parse_token_response(self, data: dict) -> OAuthTokens:
        return OAuthTokens(
            access_token=data["access_token"],
            expires_in=int(data.get("expires_in", 3600)),
            token_type=data.get("token_type", "Bearer"),
            refresh_token=data.get("refresh_token"),
            refresh_token_expires_in=data.get("refresh_token_expires_in"),
        )

    def exchange_code(self, code: str) -> OAuthTokens:
        """Exchange authorization code for tokens."""
        data = self._http.json_request(
            "POST",
            self._config.token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
                "redirect_uri": self._credentials.redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tokens = self._parse_token_response(data)
        return tokens

    async def aexchange_code(self, code: str) -> OAuthTokens:
        data = await self._http.ajson_request(
            "POST",
            self._config.token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
                "redirect_uri": self._credentials.redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return self._parse_token_response(data)

    def refresh(self, refresh_token: str | None = None) -> OAuthTokens:
        """Refresh Integration access token."""
        import asyncio

        return asyncio.run(self.arefresh(refresh_token))

    async def arefresh(self, refresh_token: str | None = None) -> OAuthTokens:
        rt = refresh_token
        if rt is None:
            stored = await self._storage.get_integration_tokens()
            if stored and stored.refresh_token:
                rt = stored.refresh_token
        if not rt:
            raise AuthenticationError("No Integration refresh token available")

        data = await self._http.ajson_request(
            "POST",
            self._config.token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": rt,
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tokens = self._parse_token_response(data)
        stored = await self._storage.get_integration_tokens()
        if not tokens.refresh_token and stored:
            tokens.refresh_token = stored.refresh_token
        await self._storage.set_integration_tokens(tokens)
        return tokens

    def authorize(
        self,
        scopes: list[str] | None = None,
        *,
        open_browser: bool = True,
        timeout: float = 300.0,
        state: str | None = None,
    ) -> OAuthTokens:
        """Run full OAuth flow with local redirect listener."""
        url, csrf = self.get_authorization_url(scopes, state=state)
        code, _ = wait_for_redirect(
            self._credentials.redirect_uri,
            timeout=timeout,
            open_browser=open_browser,
            authorization_url=url,
            expected_state=csrf,
        )
        tokens = self.exchange_code(code)
        import asyncio

        asyncio.run(self._storage.set_integration_tokens(tokens))
        return tokens

    async def aauthorize(
        self,
        scopes: list[str] | None = None,
        *,
        open_browser: bool = True,
        timeout: float = 300.0,
        state: str | None = None,
    ) -> OAuthTokens:
        url, csrf = self.get_authorization_url(scopes, state=state)
        code, _ = wait_for_redirect(
            self._credentials.redirect_uri,
            timeout=timeout,
            open_browser=open_browser,
            authorization_url=url,
            expected_state=csrf,
        )
        tokens = await self.aexchange_code(code)
        await self._storage.set_integration_tokens(tokens)
        return tokens

    def get_access_token(self) -> str:
        """Return valid Integration access token, refreshing if needed."""
        import asyncio

        return asyncio.run(self.aget_access_token())

    async def aget_access_token(self) -> str:
        tokens = await self._storage.get_integration_tokens()
        if tokens is None:
            raise AuthenticationError(
                "Integration not authorized. Call integration.authorize() first."
            )
        if tokens.is_expired():
            tokens = await self.arefresh(tokens.refresh_token)
        return tokens.access_token
