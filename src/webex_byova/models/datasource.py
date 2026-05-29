"""DataSource API models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DataSource(BaseModel):
    """Data source resource."""

    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    audience: str | None = None
    subject: str | None = None
    nonce: str | None = None
    schema_id: str | None = Field(None, alias="schemaId")
    url: str | None = None
    token_lifetime_minutes: int | None = Field(None, alias="tokenLifetimeMinutes")
    status: str | None = None
    error_message: str | None = Field(None, alias="errorMessage")


class DataSourceCreate(BaseModel):
    """Payload for POST /dataSources."""

    model_config = ConfigDict(populate_by_name=True)

    audience: str
    subject: str
    nonce: str
    schema_id: str = Field(alias="schemaId")
    url: str
    token_lifetime_minutes: int = Field(alias="tokenLifetimeMinutes")


class DataSourceUpdate(BaseModel):
    """Payload for PUT /dataSources/{id}."""

    model_config = ConfigDict(populate_by_name=True, exclude_none=True)

    audience: str | None = None
    subject: str | None = None
    nonce: str | None = None
    schema_id: str | None = Field(None, alias="schemaId")
    url: str | None = None
    token_lifetime_minutes: int | None = Field(None, alias="tokenLifetimeMinutes")
    status: str | None = None
    error_message: str | None = Field(None, alias="errorMessage")

    def model_dump_api(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


class DataSourceListItem(BaseModel):
    """Item in GET /dataSources/ list response."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    application_id: str | None = Field(None, alias="applicationId")
    created_at: str | None = Field(None, alias="createdAt")
    created_by: str | None = Field(None, alias="createdBy")
    jws_token: str | None = Field(None, alias="jwsToken")
    org_id: str | None = Field(None, alias="orgId")


class DataSourceListResponse(BaseModel):
    items: list[DataSourceListItem] = Field(default_factory=list)
