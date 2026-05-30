"""Tests for Integration OAuth."""

import httpx
import pytest
import respx

from webex_byova._http import HttpClient
from webex_byova.auth.integration import DEFAULT_INTEGRATION_SCOPES, IntegrationTokenManager
from webex_byova.auth.storage import InMemoryTokenStorage
from webex_byova.config import BYOVAConfig
from webex_byova.models.auth import IntegrationCredentials, OAuthTokens


@pytest.fixture
def integration_manager() -> IntegrationTokenManager:
    config = BYOVAConfig()
    http = HttpClient(config)
    creds = IntegrationCredentials(
        client_id="int-id",
        client_secret="int-secret",
        redirect_uri="http://127.0.0.1:8765/callback",
    )
    return IntegrationTokenManager(creds, http, InMemoryTokenStorage(), config)


@respx.mock
def test_get_authorization_url(integration_manager: IntegrationTokenManager) -> None:
    url, state = integration_manager.get_authorization_url(
        ["spark:applications_token", "application:webhooks_write"]
    )
    assert "webexapis.com" in url
    assert "client_id=int-id" in url
    assert state


@respx.mock
def test_get_authorization_url_default_scopes(
    integration_manager: IntegrationTokenManager,
) -> None:
    url, state = integration_manager.get_authorization_url()
    assert "webexapis.com" in url
    assert state
    for scope in DEFAULT_INTEGRATION_SCOPES:
        assert scope.replace(":", "%3A") in url


@respx.mock
@pytest.mark.asyncio
async def test_exchange_code(integration_manager: IntegrationTokenManager) -> None:
    respx.post("https://webexapis.com/v1/access_token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "access123",
                "expires_in": 3600,
                "refresh_token": "refresh123",
                "token_type": "Bearer",
            },
        )
    )
    tokens = await integration_manager.aexchange_code("auth-code")
    assert tokens.access_token == "access123"
    assert tokens.refresh_token == "refresh123"


@respx.mock
@pytest.mark.asyncio
async def test_refresh_integration_token(integration_manager: IntegrationTokenManager) -> None:
    storage = InMemoryTokenStorage()
    integration_manager._storage = storage
    await storage.set_integration_tokens(
        OAuthTokens(
            access_token="old",
            expires_in=0,
            refresh_token="refresh123",
        )
    )
    respx.post("https://webexapis.com/v1/access_token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "new-access",
                "expires_in": 3600,
                "token_type": "Bearer",
            },
        )
    )
    tokens = await integration_manager.arefresh()
    assert tokens.access_token == "new-access"
