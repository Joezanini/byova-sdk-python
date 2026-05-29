"""Pytest fixtures."""

from __future__ import annotations

import pytest

from webex_byova.auth.storage import InMemoryTokenStorage
from webex_byova.client import BYOVA
from webex_byova.config import BYOVAConfig
from webex_byova.models.auth import IntegrationCredentials, ServiceAppCredentials


@pytest.fixture
def config() -> BYOVAConfig:
    return BYOVAConfig(base_url="https://webexapis.com/v1")


@pytest.fixture
def integration_creds() -> IntegrationCredentials:
    return IntegrationCredentials(
        client_id="test-integration-id",
        client_secret="test-integration-secret",
        redirect_uri="http://127.0.0.1:8765/callback",
    )


@pytest.fixture
def service_app_creds() -> ServiceAppCredentials:
    return ServiceAppCredentials(
        client_id="test-sa-client-id",
        client_secret="test-sa-client-secret",
    )


@pytest.fixture
async def sdk(
    integration_creds: IntegrationCredentials,
    service_app_creds: ServiceAppCredentials,
    config: BYOVAConfig,
) -> BYOVA:
    storage = InMemoryTokenStorage()
    client = BYOVA(
        integration_creds,
        service_app_creds,
        config=config,
        token_storage=storage,
    )
    from webex_byova.models.auth import OAuthTokens

    await storage.set_integration_tokens(
        OAuthTokens(access_token="integration-access", expires_in=3600, refresh_token="ir")
    )
    return client
