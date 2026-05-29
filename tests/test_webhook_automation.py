"""Tests for webhook handling."""

import httpx
import pytest
import respx

from webex_byova.auth.utils import derive_application_id


@respx.mock
@pytest.mark.asyncio
async def test_handle_authorized_webhook(sdk) -> None:
    app_id = derive_application_id("test-sa-client-id")
    respx.post(f"https://webexapis.com/v1/applications/{app_id}/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "sa-access",
                "expires_in": 3600,
                "refresh_token": "sa-refresh",
            },
        )
    )
    import base64

    org_uuid = "63b02f90-9cc6-43b8-aa6d-cad425ac554c"
    encoded_org = base64.urlsafe_b64encode(
        f"ciscospark://us/ORGANIZATION/{org_uuid}".encode()
    ).decode().rstrip("=")

    result = await sdk.ahandle_service_app_webhook(
        {
            "resource": "serviceApp",
            "event": "authorized",
            "orgId": encoded_org,
        }
    )
    assert result.org_id == org_uuid
    assert result.event == "authorized"

    client = await sdk.aget_client_for_org(org_uuid)
    assert client.org_id == org_uuid


@respx.mock
@pytest.mark.asyncio
async def test_handle_deauthorized_webhook(sdk) -> None:
    org_uuid = "63b02f90-9cc6-43b8-aa6d-cad425ac554c"
    from webex_byova.models.auth import ServiceAppTokens

    await sdk._storage.set_service_app_tokens(
        org_uuid,
        ServiceAppTokens(access_token="x", expires_in=3600),
    )
    result = await sdk.ahandle_service_app_webhook(
        {
            "resource": "serviceApp",
            "event": "deauthorized",
            "orgId": org_uuid,
        }
    )
    assert result.event == "deauthorized"
    stored = await sdk._storage.get_service_app_tokens(org_uuid)
    assert stored is None


@respx.mock
@pytest.mark.asyncio
async def test_ensure_webhooks(sdk) -> None:
    respx.get("https://webexapis.com/v1/webhooks").mock(
        return_value=httpx.Response(200, json={"items": []})
    )
    route = respx.post("https://webexapis.com/v1/webhooks")
    route.mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "id": "wh-1",
                    "targetUrl": "https://example.com/hook",
                    "resource": "serviceApp",
                    "event": "authorized",
                },
            ),
            httpx.Response(
                200,
                json={
                    "id": "wh-2",
                    "targetUrl": "https://example.com/hook",
                    "resource": "serviceApp",
                    "event": "deauthorized",
                },
            ),
        ]
    )
    created = await sdk.webhooks.aensure_service_app_webhooks("https://example.com/hook")
    assert len(created) == 2
    assert route.call_count == 2
