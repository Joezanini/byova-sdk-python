"""Schema API models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Schema(BaseModel):
    """Data source schema available for BYODS registration.

    Attributes:
        id: Unique schema UUID.
        app_type: Application type identifier.
        created_at: ISO 8601 creation timestamp.
        protocol: Data delivery protocol.
        service_type: Service type classification.
        url: Schema documentation or reference URL.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Unique schema UUID.")
    app_type: str | None = Field(default=None, alias="appType", description="Application type.")
    created_at: str | None = Field(
        default=None, alias="createdAt", description="ISO 8601 creation timestamp."
    )
    protocol: str | None = Field(default=None, description="Data delivery protocol.")
    service_type: str | None = Field(
        default=None, alias="serviceType", description="Service type classification."
    )
    url: str | None = Field(default=None, description="Schema reference URL.")


class SchemaListResponse(BaseModel):
    """Response wrapper for ``GET /dataSources/schemas``."""

    items: list[Schema] = Field(default_factory=list, description="Available BYODS schemas.")
