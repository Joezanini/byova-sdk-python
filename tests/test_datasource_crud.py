"""Tests for DataSource CRUD."""

import httpx
import pytest
import respx

from webex_byova.models.auth import OAuthTokens, ServiceAppTokens
from webex_byova.models.datasource import DataSourceCreate


@respx.mock
@pytest.mark.asyncio
async def test_datasource_crud(sdk) -> None:
    org_id = "org-test-1"
    await sdk._storage.set_integration_tokens(OAuthTokens(access_token="int", expires_in=3600))
    await sdk._storage.set_service_app_tokens(
        org_id,
        ServiceAppTokens(access_token="sa-token", expires_in=3600, refresh_token="sr"),
    )

    respx.get("https://webexapis.com/v1/dataSources/").mock(
        return_value=httpx.Response(
            200,
            json={
                "items": [
                    {
                        "applicationId": "app1",
                        "orgId": org_id,
                        "jwsToken": "eyJhbGciOiJSUzI1NiJ9.test",
                    }
                ]
            },
        )
    )
    respx.post("https://webexapis.com/v1/dataSources").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "ds-new",
                "audience": "MyApp",
                "subject": "callAudioData",
                "nonce": "nonce1",
                "schemaId": "schema-1",
                "url": "https://dap.example.com",
                "tokenLifetimeMinutes": 60,
                "status": "active",
            },
        )
    )
    respx.get("https://webexapis.com/v1/dataSources/ds-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "ds-1", "status": "active", "url": "https://dap.example.com"},
        )
    )
    respx.put("https://webexapis.com/v1/dataSources/ds-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "ds-1", "status": "disabled", "errorMessage": "maintenance"},
        )
    )
    respx.delete("https://webexapis.com/v1/dataSources/ds-1").mock(return_value=httpx.Response(204))

    client = await sdk.aget_client_for_org(org_id)
    items = await client.data_sources.alist()
    assert len(items) == 1

    created = await client.data_sources.acreate(
        DataSourceCreate(
            audience="MyApp",
            subject="callAudioData",
            nonce="nonce1",
            schema_id="schema-1",
            url="https://dap.example.com",
            token_lifetime_minutes=60,
        )
    )
    assert created.id == "ds-new"

    got = await client.data_sources.aget("ds-1")
    assert got.id == "ds-1"

    updated = await client.data_sources.aupdate(
        "ds-1", {"status": "disabled", "errorMessage": "maintenance"}
    )
    assert updated.status == "disabled"

    await client.data_sources.adelete("ds-1")
