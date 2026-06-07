"""Webhook event models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookRegistration(BaseModel):
    """Registered Webex webhook.

    Attributes:
        id: Unique webhook identifier.
        name: Human-readable webhook name.
        target_url: HTTPS URL that receives webhook payloads.
        resource: Webhook resource type (for example ``serviceApp``).
        event: Event name (for example ``authorized``).
        filter: Optional webhook filter expression.
        secret: Shared secret for payload verification.
        status: Webhook status from Webex.
        created: ISO 8601 creation timestamp.
        owned_by: Owner identifier.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str = Field(description="Unique webhook identifier.")
    name: str | None = Field(default=None, description="Human-readable webhook name.")
    target_url: str | None = Field(
        default=None, alias="targetUrl", description="HTTPS URL for webhook delivery."
    )
    resource: str | None = Field(default=None, description="Webhook resource type.")
    event: str | None = Field(default=None, description="Event name.")
    filter: str | None = Field(default=None, description="Optional webhook filter.")
    secret: str | None = Field(default=None, description="Shared secret for verification.")
    status: str | None = Field(default=None, description="Webhook status from Webex.")
    created: str | None = Field(default=None, description="ISO 8601 creation timestamp.")
    owned_by: str | None = Field(default=None, alias="ownedBy", description="Owner identifier.")


class WebhookUpdate(BaseModel):
    """Payload for ``PUT /webhooks/{id}``."""

    model_config = ConfigDict(populate_by_name=True, exclude_none=True)

    name: str = Field(description="Updated webhook name.")
    target_url: str = Field(alias="targetUrl", description="Updated target URL.")
    secret: str | None = Field(default=None, description="Updated shared secret.")
    status: str | None = Field(default=None, description="Updated webhook status.")

    def model_dump_api(self) -> dict[str, Any]:
        """Serialize for the Webex API using camelCase field names.

        Returns:
            Dictionary with ``None`` values excluded.
        """
        return self.model_dump(by_alias=True, exclude_none=True)


class ServiceAppWebhookEvent(BaseModel):
    """Parsed ``serviceApp`` authorized or deauthorized webhook payload."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str | None = Field(default=None, description="Webhook event ID.")
    name: str | None = Field(default=None, description="Event name.")
    resource: str | None = Field(default=None, description="Resource type.")
    event: str | None = Field(default=None, description="Event type.")
    org_id: str | None = Field(default=None, alias="orgId", description="Encoded organization ID.")
    application_id: str | None = Field(
        default=None, alias="applicationId", description="Service App application ID."
    )
    data: dict[str, Any] | None = Field(default=None, description="Event data payload.")
    raw: dict[str, Any] = Field(default_factory=dict, description="Original webhook JSON.")

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ServiceAppWebhookEvent:
        """Parse a raw webhook JSON payload into a structured event.

        Args:
            payload: Raw webhook JSON from Webex.

        Returns:
            Parsed ``ServiceAppWebhookEvent`` instance.
        """
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
    """Result of handling a ``serviceApp`` authorized event.

    Attributes:
        org_id: Decoded organization ID.
        tokens: Service App tokens fetched for the org.
        event: Event name (``authorized``).
    """

    org_id: str = Field(description="Decoded organization ID.")
    tokens: Any = Field(default=None, description="Service App tokens for the org.")
    event: str = Field(default="authorized", description="Event name.")


class ServiceAppDeauthorizedResult(BaseModel):
    """Result of handling a ``serviceApp`` deauthorized event.

    Attributes:
        org_id: Organization ID that was deauthorized.
        event: Event name (``deauthorized``).
    """

    org_id: str = Field(description="Organization ID that was deauthorized.")
    event: str = Field(default="deauthorized", description="Event name.")
