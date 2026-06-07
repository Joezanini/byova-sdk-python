"""BYOVA SDK client facade."""

from __future__ import annotations

from typing import Any

from webex_byova._http import HttpClient
from webex_byova.auth.credentials import load_credentials_from_env
from webex_byova.auth.integration import IntegrationTokenManager
from webex_byova.auth.service_app import ServiceAppTokenManager
from webex_byova.auth.storage import InMemoryTokenStorage, TokenStorage
from webex_byova.config import BYOVAConfig
from webex_byova.exceptions import OrgNotRegisteredError, ValidationError
from webex_byova.jws.verifier import JWSVerifier
from webex_byova.models.auth import IntegrationCredentials, ServiceAppCredentials
from webex_byova.models.webhook import (
    ServiceAppAuthorizedResult,
    ServiceAppDeauthorizedResult,
    ServiceAppWebhookEvent,
)
from webex_byova.resources.datasource import OrgClient
from webex_byova.webhooks.manager import WebhookManager


class BYOVA:
    """Webex BYOVA / BYODS Python SDK facade.

    Central entry point that wires Integration OAuth, Service App token
    management, webhook registration, per-org API clients, and JWS verification.

    Example:
        ```python
        sdk = BYOVA(integration=..., service_app=...)
        await sdk.integration.aauthorize()
        client = await sdk.aget_client_for_org(org_id)
        ```
    """

    def __init__(
        self,
        integration: IntegrationCredentials,
        service_app: ServiceAppCredentials,
        *,
        config: BYOVAConfig | None = None,
        token_storage: TokenStorage | None = None,
    ) -> None:
        """Initialize the BYOVA SDK client.

        Args:
            integration: Integration OAuth credentials.
            service_app: Service App OAuth credentials.
            config: Optional global SDK configuration.
            token_storage: Token persistence backend; defaults to in-memory storage.
        """
        self._config = config or BYOVAConfig()
        self._storage: TokenStorage = token_storage or InMemoryTokenStorage()
        self._http = HttpClient(self._config)
        self._integration = IntegrationTokenManager(
            integration, self._http, self._storage, self._config
        )
        self._service_app = ServiceAppTokenManager(
            service_app, self._integration, self._http, self._storage
        )
        self._webhooks = WebhookManager(self._integration, self._http)
        self._jws = JWSVerifier(self._config)

    @classmethod
    def from_env(cls, *, config: BYOVAConfig | None = None) -> BYOVA:
        """Construct a client from ``WEBEX_*`` environment variables.

        Args:
            config: Optional global SDK configuration.

        Returns:
            Configured ``BYOVA`` instance.

        Raises:
            ValueError: If required environment variables are missing.
        """
        integration, service_app = load_credentials_from_env()
        return cls(integration, service_app, config=config)

    @property
    def config(self) -> BYOVAConfig:
        """Global SDK configuration."""
        return self._config

    @property
    def integration(self) -> IntegrationTokenManager:
        """Integration OAuth token manager."""
        return self._integration

    @property
    def service_app(self) -> ServiceAppTokenManager:
        """Service App token manager for per-org tokens."""
        return self._service_app

    @property
    def webhooks(self) -> WebhookManager:
        """Webhook registration and management."""
        return self._webhooks

    def get_client_for_org(self, org_id: str) -> OrgClient:
        """Return a per-org client for DataSource operations (sync).

        Args:
            org_id: Organization UUID.

        Returns:
            ``OrgClient`` scoped to the organization.

        Raises:
            OrgNotRegisteredError: If no Service App tokens exist for the org.
        """
        import asyncio

        registered = asyncio.run(self._storage.list_registered_orgs())
        if org_id not in registered:
            raise OrgNotRegisteredError(
                f"Org {org_id} is not registered. "
                "Handle serviceApp authorized webhook or call service_app.save_registration()."
            )
        return OrgClient(org_id, self._service_app, self._http)

    async def aget_client_for_org(self, org_id: str) -> OrgClient:
        """Return a per-org client for DataSource and Schema operations.

        Args:
            org_id: Organization UUID.

        Returns:
            ``OrgClient`` scoped to the organization.

        Raises:
            OrgNotRegisteredError: If no Service App tokens exist for the org.
        """
        registered = await self._storage.list_registered_orgs()
        if org_id not in registered:
            raise OrgNotRegisteredError(
                f"Org {org_id} is not registered. "
                "Handle serviceApp authorized webhook or call service_app.save_registration()."
            )
        return OrgClient(org_id, self._service_app, self._http)

    async def ahandle_service_app_webhook(
        self, payload: dict[str, Any]
    ) -> ServiceAppAuthorizedResult | ServiceAppDeauthorizedResult:
        """Process a ``serviceApp`` authorized or deauthorized webhook.

        On authorization, fetches and stores Service App tokens for the org.
        On deauthorization, removes stored tokens.

        Args:
            payload: Raw webhook JSON from Webex.

        Returns:
            ``ServiceAppAuthorizedResult`` or ``ServiceAppDeauthorizedResult``.

        Raises:
            ValidationError: If the payload is not a valid serviceApp event.
        """
        event = ServiceAppWebhookEvent.from_payload(payload)
        if event.resource and event.resource != "serviceApp":
            raise ValidationError(f"Unexpected webhook resource: {event.resource}")

        event_name = (event.event or event.name or "").lower()
        encoded_org = event.org_id
        if not encoded_org:
            raise ValidationError("Webhook missing orgId")

        if event_name == "authorized":
            org_id, tokens = await self._service_app.afetch_token_from_webhook_org(encoded_org)
            return ServiceAppAuthorizedResult(org_id=org_id, tokens=tokens, event="authorized")

        if event_name == "deauthorized":
            org_id = encoded_org
            try:
                from webex_byova.auth.utils import decode_org_id

                org_id = decode_org_id(encoded_org)
            except Exception:
                pass
            await self._storage.delete_service_app_tokens(org_id)
            return ServiceAppDeauthorizedResult(org_id=org_id, event="deauthorized")

        raise ValidationError(f"Unexpected serviceApp event: {event_name}")

    def handle_service_app_webhook(
        self, payload: dict[str, Any]
    ) -> ServiceAppAuthorizedResult | ServiceAppDeauthorizedResult:
        """Process a serviceApp webhook (sync wrapper).

        Args:
            payload: Raw webhook JSON from Webex.

        Returns:
            Authorization or deauthorization result.
        """
        import asyncio

        return asyncio.run(self.ahandle_service_app_webhook(payload))

    def verify_jws_token(self, jws_token: str) -> dict[str, Any]:
        """Verify an inbound BYODS JWS token (sync).

        Args:
            jws_token: JWS token string from Webex data delivery.

        Returns:
            Decoded JWT claims dictionary.

        Raises:
            ValueError: If the token is invalid or no matching JWK is found.
        """
        return self._jws.verify(jws_token)

    async def averify_jws_token(self, jws_token: str) -> dict[str, Any]:
        """Verify an inbound BYODS JWS token.

        Args:
            jws_token: JWS token string from Webex data delivery.

        Returns:
            Decoded JWT claims dictionary.

        Raises:
            ValueError: If the token is invalid or no matching JWK is found.
        """
        return await self._jws.averify(jws_token)

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._http.close()

    async def aclose(self) -> None:
        """Close the underlying HTTP client asynchronously."""
        await self._http.aclose()
