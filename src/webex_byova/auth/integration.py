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
"""Default OAuth scopes required for BYOVA Integration authorization."""


class IntegrationTokenManager:
    """Manage Integration OAuth tokens for the developer-initiated flow.

    Handles authorization URL generation, code exchange, token refresh, and
    the full browser-based OAuth flow with a local redirect listener.
    """

    def __init__(
        self,
        credentials: IntegrationCredentials,
        http: HttpClient,
        storage: TokenStorage,
        config: BYOVAConfig | None = None,
    ) -> None:
        """Initialize the Integration token manager.

        Args:
            credentials: Integration OAuth client credentials.
            http: Shared HTTP client for API requests.
            storage: Token storage backend.
            config: Optional SDK configuration; defaults to ``http.config``.
        """
        self._credentials = credentials
        self._http = http
        self._storage = storage
        self._config = config or http.config

    @property
    def credentials(self) -> IntegrationCredentials:
        """Integration OAuth client credentials."""
        return self._credentials

    def get_authorization_url(
        self,
        scopes: list[str] | None = None,
        *,
        state: str | None = None,
    ) -> tuple[str, str]:
        """Build the OAuth authorization URL.

        Args:
            scopes: OAuth scopes to request; defaults to ``DEFAULT_INTEGRATION_SCOPES``.
            state: CSRF state token; generated automatically if not provided.

        Returns:
            Tuple of ``(authorization_url, state)``.
        """
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
        """Exchange an authorization code for OAuth tokens (sync).

        Args:
            code: Authorization code from the OAuth redirect.

        Returns:
            OAuth tokens from the Webex token endpoint.

        Raises:
            AuthenticationError: If the token exchange fails.
        """
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
        """Exchange an authorization code for OAuth tokens (async).

        Args:
            code: Authorization code from the OAuth redirect.

        Returns:
            OAuth tokens from the Webex token endpoint.

        Raises:
            AuthenticationError: If the token exchange fails.
        """
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
        """Refresh the Integration access token (sync wrapper).

        Args:
            refresh_token: Explicit refresh token; uses stored token if omitted.

        Returns:
            Refreshed OAuth tokens.

        Raises:
            AuthenticationError: If no refresh token is available.
        """
        import asyncio

        return asyncio.run(self.arefresh(refresh_token))

    async def arefresh(self, refresh_token: str | None = None) -> OAuthTokens:
        """Refresh the Integration access token.

        Args:
            refresh_token: Explicit refresh token; uses stored token if omitted.

        Returns:
            Refreshed OAuth tokens, persisted to storage.

        Raises:
            AuthenticationError: If no refresh token is available.
        """
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
        """Run the full OAuth flow with a local redirect listener (sync).

        Opens the authorization URL in a browser, waits for the redirect,
        exchanges the code, and stores tokens.

        Args:
            scopes: OAuth scopes to request.
            open_browser: Whether to open the authorization URL automatically.
            timeout: Maximum seconds to wait for the OAuth redirect.
            state: CSRF state token; generated if not provided.

        Returns:
            OAuth tokens from the completed authorization.

        Raises:
            OAuthRedirectError: If the user denies access.
            OAuthRedirectTimeout: If the redirect listener times out.
            AuthenticationError: If token exchange fails.
        """
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
        """Run the full OAuth flow with a local redirect listener (async).

        Opens the authorization URL in a browser, waits for the redirect,
        exchanges the code, and stores tokens.

        Args:
            scopes: OAuth scopes to request.
            open_browser: Whether to open the authorization URL automatically.
            timeout: Maximum seconds to wait for the OAuth redirect.
            state: CSRF state token; generated if not provided.

        Returns:
            OAuth tokens from the completed authorization.

        Raises:
            OAuthRedirectError: If the user denies access.
            OAuthRedirectTimeout: If the redirect listener times out.
            AuthenticationError: If token exchange fails.
        """
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
        """Return a valid Integration access token, refreshing if needed (sync).

        Returns:
            Valid bearer access token.

        Raises:
            AuthenticationError: If Integration is not yet authorized.
        """
        import asyncio

        return asyncio.run(self.aget_access_token())

    async def aget_access_token(self) -> str:
        """Return a valid Integration access token, refreshing if needed.

        Returns:
            Valid bearer access token.

        Raises:
            AuthenticationError: If Integration is not yet authorized.
        """
        tokens = await self._storage.get_integration_tokens()
        if tokens is None:
            raise AuthenticationError(
                "Integration not authorized. Call integration.authorize() first."
            )
        if tokens.is_expired():
            tokens = await self.arefresh(tokens.refresh_token)
        return tokens.access_token
