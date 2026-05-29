"""Webhook registration for Service App events."""

from __future__ import annotations

from webex_byova._http import HttpClient
from webex_byova.auth.integration import IntegrationTokenManager
from webex_byova.models.webhook import WebhookRegistration


class WebhookManager:
    """Register and manage serviceApp webhooks."""

    def __init__(self, integration: IntegrationTokenManager, http: HttpClient) -> None:
        self._integration = integration
        self._http = http

    async def alist(self) -> list[WebhookRegistration]:
        token = await self._integration.aget_access_token()
        data = await self._http.ajson_request("GET", "/webhooks", bearer=token)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [WebhookRegistration.model_validate(w) for w in items]

    async def acreate(
        self,
        name: str,
        target_url: str,
        *,
        resource: str = "serviceApp",
        event: str,
    ) -> WebhookRegistration:
        token = await self._integration.aget_access_token()
        data = await self._http.ajson_request(
            "POST",
            "/webhooks",
            bearer=token,
            json={
                "name": name,
                "targetUrl": target_url,
                "resource": resource,
                "event": event,
            },
        )
        return WebhookRegistration.model_validate(data)

    async def adelete(self, webhook_id: str) -> None:
        token = await self._integration.aget_access_token()
        await self._http.arequest("DELETE", f"/webhooks/{webhook_id}", bearer=token)

    async def aensure_service_app_webhooks(self, target_url: str) -> list[WebhookRegistration]:
        """Create authorized/deauthorized webhooks if not already registered."""
        existing = await self.alist()
        created: list[WebhookRegistration] = []
        for event in ("authorized", "deauthorized"):
            found = any(
                w.resource == "serviceApp"
                and w.event == event
                and w.target_url == target_url
                for w in existing
            )
            if not found:
                wh = await self.acreate(
                    name=f"BYOVA Service App {event}",
                    target_url=target_url,
                    event=event,
                )
                created.append(wh)
                existing.append(wh)
        return created
