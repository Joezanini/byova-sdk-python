"""DataSource schema resource."""

from __future__ import annotations

from webex_byova._http import HttpClient
from webex_byova.auth.service_app import ServiceAppTokenManager
from webex_byova.models.schema import Schema, SchemaListResponse


class SchemaResource:
    """List and retrieve BYODS data source schemas for an organization."""

    def __init__(
        self,
        service_app: ServiceAppTokenManager,
        http: HttpClient,
        org_id: str,
    ) -> None:
        """Initialize the schema resource.

        Args:
            service_app: Service App token manager.
            http: Shared HTTP client.
            org_id: Organization UUID for token scoping.
        """
        self._service_app = service_app
        self._http = http
        self._org_id = org_id

    async def alist(self) -> list[Schema]:
        """List available BYODS schemas for the organization.

        Returns:
            List of schema definitions.
        """
        bearer = await self._service_app.aget_access_token(self._org_id)
        data = await self._http.ajson_request("GET", "/dataSources/schemas", bearer=bearer)
        return SchemaListResponse.model_validate(data).items

    async def aget(self, schema_id: str) -> Schema:
        """Get a schema by ID.

        Args:
            schema_id: Unique schema UUID.

        Returns:
            Schema definition.
        """
        bearer = await self._service_app.aget_access_token(self._org_id)
        data = await self._http.ajson_request(
            "GET", f"/dataSources/schemas/{schema_id}", bearer=bearer
        )
        return Schema.model_validate(data)
