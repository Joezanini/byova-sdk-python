"""DataSource API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DataSource(BaseModel):
    """Data source resource returned by the Webex BYODS API.

    Attributes:
        id: Unique data source identifier.
        audience: Virtual agent or application audience name.
        subject: Data subject identifier (for example ``callAudioData``).
        nonce: Unique nonce string for the data source.
        schema_id: UUID of the associated BYODS schema.
        url: Ingestion endpoint URL for data delivery.
        token_lifetime_minutes: JWS token lifetime in minutes.
        status: Provisioning status (for example ``active``, ``error``).
        error_message: Error details when status indicates failure.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, description="Unique data source identifier.")
    audience: str | None = Field(default=None, description="Virtual agent audience name.")
    subject: str | None = Field(default=None, description="Data subject identifier.")
    nonce: str | None = Field(default=None, description="Unique nonce for the data source.")
    schema_id: str | None = Field(default=None, alias="schemaId", description="BYODS schema UUID.")
    url: str | None = Field(default=None, description="Ingestion endpoint URL.")
    token_lifetime_minutes: int | None = Field(
        default=None, alias="tokenLifetimeMinutes", description="JWS token lifetime in minutes."
    )
    status: str | None = Field(default=None, description="Provisioning status.")
    error_message: str | None = Field(
        default=None, alias="errorMessage", description="Error details when status is error."
    )


class DataSourceCreate(BaseModel):
    """Payload for ``POST /dataSources``.

    Attributes:
        audience: Virtual agent or application audience name.
        subject: Data subject identifier.
        nonce: Unique nonce string.
        schema_id: UUID of the BYODS schema to use.
        url: Ingestion endpoint URL.
        token_lifetime_minutes: JWS token lifetime in minutes.
    """

    model_config = ConfigDict(populate_by_name=True)

    audience: str = Field(description="Virtual agent or application audience name.")
    subject: str = Field(description="Data subject identifier.")
    nonce: str = Field(description="Unique nonce string.")
    schema_id: str = Field(alias="schemaId", description="UUID of the BYODS schema.")
    url: str = Field(description="Ingestion endpoint URL.")
    token_lifetime_minutes: int = Field(
        alias="tokenLifetimeMinutes", description="JWS token lifetime in minutes."
    )


class DataSourceUpdate(BaseModel):
    """Payload for ``PUT /dataSources/{id}``.

    All fields are optional; only provided fields are sent to the API.
    """

    model_config = ConfigDict(populate_by_name=True, exclude_none=True)

    audience: str | None = Field(default=None, description="Virtual agent audience name.")
    subject: str | None = Field(default=None, description="Data subject identifier.")
    nonce: str | None = Field(default=None, description="Unique nonce string.")
    schema_id: str | None = Field(default=None, alias="schemaId", description="BYODS schema UUID.")
    url: str | None = Field(default=None, description="Ingestion endpoint URL.")
    token_lifetime_minutes: int | None = Field(
        default=None, alias="tokenLifetimeMinutes", description="JWS token lifetime in minutes."
    )
    status: str | None = Field(default=None, description="Provisioning status.")
    error_message: str | None = Field(
        default=None, alias="errorMessage", description="Error message for failed provisioning."
    )

    def model_dump_api(self) -> dict[str, Any]:
        """Serialize for the Webex API using camelCase field names.

        Returns:
            Dictionary with ``None`` values excluded.
        """
        return self.model_dump(by_alias=True, exclude_none=True)


class DataSourceListItem(BaseModel):
    """Item in the ``GET /dataSources/`` list response."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    application_id: str | None = Field(
        default=None, alias="applicationId", description="Service App application ID."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="ISO 8601 creation timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator identifier."
    )
    jws_token: str | None = Field(
        default=None, alias="jwsToken", description="Sample JWS token for the data source."
    )
    org_id: str | None = Field(default=None, alias="orgId", description="Organization ID.")


class DataSourceListResponse(BaseModel):
    """Response wrapper for ``GET /dataSources/``."""

    items: list[DataSourceListItem] = Field(
        default_factory=list, description="List of data source summary items."
    )
