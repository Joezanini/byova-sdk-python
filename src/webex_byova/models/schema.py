"""Schema API models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Schema(BaseModel):
    """Data source schema."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    app_type: str | None = Field(None, alias="appType")
    created_at: str | None = Field(None, alias="createdAt")
    protocol: str | None = None
    service_type: str | None = Field(None, alias="serviceType")
    url: str | None = None


class SchemaListResponse(BaseModel):
    items: list[Schema] = Field(default_factory=list)
