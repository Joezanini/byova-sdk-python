"""Service App token management."""

from __future__ import annotations

from webex_byova._http import HttpClient
from webex_byova.auth.integration import IntegrationTokenManager
from webex_byova.auth.storage import TokenStorage
from webex_byova.auth.utils import decode_org_id, derive_application_id
from webex_byova.exceptions import AuthenticationError
from webex_byova.models.auth import ServiceAppCredentials, ServiceAppTokens


class ServiceAppTokenManager:
    """Fetch, refresh, and store per-organization Service App tokens.

    Service App tokens are scoped to a customer organization and are obtained
    after a customer admin authorizes your Service App in Control Hub.
    """

    def __init__(
        self,
        credentials: ServiceAppCredentials,
        integration: IntegrationTokenManager,
        http: HttpClient,
        storage: TokenStorage,
    ) -> None:
        """Initialize the Service App token manager.

        Args:
            credentials: Service App OAuth client credentials.
            integration: Integration token manager for bearer authentication.
            http: Shared HTTP client for API requests.
            storage: Token storage backend.
        """
        self._credentials = credentials
        self._integration = integration
        self._http = http
        self._storage = storage
        self._application_id = derive_application_id(credentials.client_id)

    @property
    def application_id(self) -> str:
        """Base64url-encoded Service App application ID derived from client ID."""
        return self._application_id

    @property
    def credentials(self) -> ServiceAppCredentials:
        """Service App OAuth client credentials."""
        return self._credentials

    def _parse_token_response(self, data: dict) -> ServiceAppTokens:
        return ServiceAppTokens(
            access_token=data["access_token"],
            expires_in=int(data.get("expires_in", 3600)),
            token_type=data.get("token_type", "Bearer"),
            refresh_token=data.get("refresh_token"),
            refresh_token_expires_in=data.get("refresh_token_expires_in"),
        )

    async def afetch_token_for_org(self, org_id: str) -> ServiceAppTokens:
        """Fetch Service App tokens for an organization using Integration bearer auth.

        Args:
            org_id: Target organization UUID.

        Returns:
            Service App tokens, persisted to storage.

        Raises:
            AuthenticationError: If the token fetch fails.
        """
        integration_token = await self._integration.aget_access_token()
        path = f"/applications/{self._application_id}/token"
        data = await self._http.ajson_request(
            "POST",
            path,
            bearer=integration_token,
            json={
                "clientId": self._credentials.client_id,
                "clientSecret": self._credentials.client_secret,
                "targetOrgId": org_id,
            },
        )
        tokens = self._parse_token_response(data)
        await self._storage.set_service_app_tokens(org_id, tokens)
        return tokens

    def fetch_token_for_org(self, org_id: str) -> ServiceAppTokens:
        """Fetch Service App tokens for an organization (sync wrapper).

        Args:
            org_id: Target organization UUID.

        Returns:
            Service App tokens, persisted to storage.
        """
        import asyncio

        return asyncio.run(self.afetch_token_for_org(org_id))

    async def afetch_token_from_webhook_org(
        self, encoded_org_id: str
    ) -> tuple[str, ServiceAppTokens]:
        """Decode org ID from a webhook payload and fetch Service App tokens.

        Args:
            encoded_org_id: Base64url-encoded org ID from the webhook ``orgId``.

        Returns:
            Tuple of ``(decoded_org_id, tokens)``.
        """
        org_id = decode_org_id(encoded_org_id)
        tokens = await self.afetch_token_for_org(org_id)
        return org_id, tokens

    def save_registration(self, org_id: str, refresh_token: str) -> ServiceAppTokens:
        """Store tokens when a refresh token is already available (sync).

        Use this sandbox path when you already have a Service App refresh token
        without waiting for a production webhook.

        Args:
            org_id: Organization UUID.
            refresh_token: Existing Service App refresh token.

        Returns:
            Refreshed Service App tokens.
        """
        import asyncio

        return asyncio.run(self.asave_registration(org_id, refresh_token))

    async def asave_registration(self, org_id: str, refresh_token: str) -> ServiceAppTokens:
        """Store tokens when a refresh token is already available.

        Use this sandbox path when you already have a Service App refresh token
        without waiting for a production webhook.

        Args:
            org_id: Organization UUID.
            refresh_token: Existing Service App refresh token.

        Returns:
            Refreshed Service App tokens.
        """
        tokens = ServiceAppTokens(
            access_token="",
            expires_in=0,
            refresh_token=refresh_token,
        )
        await self._storage.set_service_app_tokens(org_id, tokens)
        return await self.arefresh_for_org(org_id)

    async def arefresh_for_org(self, org_id: str) -> ServiceAppTokens:
        """Refresh the Service App access token for an organization.

        If no refresh token is stored, falls back to fetching new tokens
        via the Integration bearer.

        Args:
            org_id: Organization UUID.

        Returns:
            Refreshed Service App tokens, persisted to storage.
        """
        stored = await self._storage.get_service_app_tokens(org_id)
        if stored is None or not stored.refresh_token:
            return await self.afetch_token_for_org(org_id)

        integration_token = await self._integration.aget_access_token()
        data = await self._http.ajson_request(
            "POST",
            self._http.config.token_url,
            bearer=integration_token,
            data={
                "grant_type": "refresh_token",
                "refresh_token": stored.refresh_token,
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tokens = self._parse_token_response(data)
        if not tokens.refresh_token:
            tokens.refresh_token = stored.refresh_token
        await self._storage.set_service_app_tokens(org_id, tokens)
        return tokens

    async def aget_access_token(self, org_id: str) -> str:
        """Return a valid Service App access token for an organization.

        Refreshes automatically if the token is missing or expired.

        Args:
            org_id: Organization UUID.

        Returns:
            Valid bearer access token for org-scoped API calls.

        Raises:
            AuthenticationError: If the org is not registered.
        """
        tokens = await self._storage.get_service_app_tokens(org_id)
        if tokens is None:
            raise AuthenticationError(
                f"No Service App registration for org {org_id}. "
                "Wait for authorized webhook or call save_registration()."
            )
        if not tokens.access_token or tokens.is_expired():
            tokens = await self.arefresh_for_org(org_id)
        return tokens.access_token
