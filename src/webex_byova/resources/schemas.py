"""DataSource schema resource."""

from __future__ import annotations

from webex_byova._http import HttpClient
from webex_byova.auth.service_app import ServiceAppTokenManager
from webex_byova.models.schema import Schema, SchemaListResponse


class SchemaResource:
    """List and get data source schemas."""

    def __init__(
        self,
        service_app: ServiceAppTokenManager,
        http: HttpClient,
        org_id: str,
    ) -> None:
        self._service_app = service_app
        self._http = http
        self._org_id = org_id

    async def alist(self) -> list[Schema]:
        bearer = await self._service_app.aget_access_token(self._org_id)
        data = await self._http.ajson_request("GET", "/dataSources/schemas", bearer=bearer)
        return SchemaListResponse.model_validate(data).items

    async def aget(self, schema_id: str) -> Schema:
        bearer = await self._service_app.aget_access_token(self._org_id)
        data = await self._http.ajson_request(
            "GET", f"/dataSources/schemas/{schema_id}", bearer=bearer
        )
        return Schema.model_validate(data)
