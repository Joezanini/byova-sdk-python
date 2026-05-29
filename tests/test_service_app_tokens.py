"""Tests for Service App token management."""

import httpx
import pytest
import respx

from webex_byova._http import HttpClient
from webex_byova.auth.integration import IntegrationTokenManager
from webex_byova.auth.service_app import ServiceAppTokenManager
from webex_byova.auth.storage import InMemoryTokenStorage
from webex_byova.auth.utils import derive_application_id
from webex_byova.config import BYOVAConfig
from webex_byova.models.auth import IntegrationCredentials, OAuthTokens, ServiceAppCredentials


@pytest.fixture
def sa_manager() -> ServiceAppTokenManager:
    config = BYOVAConfig()
    http = HttpClient(config)
    storage = InMemoryTokenStorage()
    integration = IntegrationTokenManager(
        IntegrationCredentials(
            client_id="int-id",
            client_secret="int-secret",
        ),
        http,
        storage,
        config,
    )
    import asyncio

    asyncio.run(
        storage.set_integration_tokens(
            OAuthTokens(access_token="int-token", expires_in=3600, refresh_token="ir")
        )
    )
    return ServiceAppTokenManager(
        ServiceAppCredentials(client_id="sa-id", client_secret="sa-secret"),
        integration,
        http,
        storage,
    )


@respx.mock
@pytest.mark.asyncio
async def test_fetch_token_for_org(sa_manager: ServiceAppTokenManager) -> None:
    app_id = derive_application_id("sa-id")
    respx.post(f"https://webexapis.com/v1/applications/{app_id}/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "sa-access",
                "expires_in": 3600,
                "refresh_token": "sa-refresh",
                "token_type": "Bearer",
            },
        )
    )
    tokens = await sa_manager.afetch_token_for_org("org-uuid-123")
    assert tokens.access_token == "sa-access"
    stored = await sa_manager._storage.get_service_app_tokens("org-uuid-123")
    assert stored is not None
    assert stored.refresh_token == "sa-refresh"
