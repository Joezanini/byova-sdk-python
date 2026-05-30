"""Webhook event models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookRegistration(BaseModel):
    """Registered webhook."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    target_url: str | None = Field(None, alias="targetUrl")
    resource: str | None = None
    event: str | None = None
    filter: str | None = None
    secret: str | None = None
    status: str | None = None
    created: str | None = None
    owned_by: str | None = Field(None, alias="ownedBy")


class WebhookUpdate(BaseModel):
    """Payload for PUT /webhooks/{id}."""

    model_config = ConfigDict(populate_by_name=True, exclude_none=True)

    name: str
    target_url: str = Field(alias="targetUrl")
    secret: str | None = None
    status: str | None = None

    def model_dump_api(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


class ServiceAppWebhookEvent(BaseModel):
    """Parsed serviceApp authorized/deauthorized webhook payload."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str | None = None
    name: str | None = None
    resource: str | None = None
    event: str | None = None
    org_id: str | None = Field(None, alias="orgId")
    application_id: str | None = Field(None, alias="applicationId")
    data: dict[str, Any] | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ServiceAppWebhookEvent:
        org_id = payload.get("orgId") or (payload.get("data") or {}).get("orgId")
        app_id = payload.get("applicationId") or (payload.get("data") or {}).get("applicationId")
        return cls(
            id=payload.get("id"),
            name=payload.get("name"),
            resource=payload.get("resource"),
            event=payload.get("event") or payload.get("name"),
            org_id=org_id,
            application_id=app_id,
            data=payload.get("data"),
            raw=payload,
        )


class ServiceAppAuthorizedResult(BaseModel):
    """Result of handling a serviceApp authorized event."""

    org_id: str
    tokens: Any = None
    event: str = "authorized"


class ServiceAppDeauthorizedResult(BaseModel):
    """Result of handling a serviceApp deauthorized event."""

    org_id: str
    event: str = "deauthorized"
