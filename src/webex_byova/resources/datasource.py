"""DataSource CRUD resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from webex_byova._http import HttpClient
from webex_byova.auth.service_app import ServiceAppTokenManager
from webex_byova.exceptions import AuthenticationError
from webex_byova.models.datasource import (
    DataSource,
    DataSourceCreate,
    DataSourceListItem,
    DataSourceListResponse,
    DataSourceUpdate,
)
from webex_byova.resources.schemas import SchemaResource

if TYPE_CHECKING:
    pass


class DataSourceResource:
    """Async CRUD operations for ``/dataSources`` endpoints.

    Automatically refreshes Service App tokens on 401 responses.
    """

    def __init__(
        self,
        org_id: str,
        service_app: ServiceAppTokenManager,
        http: HttpClient,
    ) -> None:
        """Initialize the data source resource.

        Args:
            org_id: Organization UUID for token scoping.
            service_app: Service App token manager.
            http: Shared HTTP client.
        """
        self._org_id = org_id
        self._service_app = service_app
        self._http = http

    async def _bearer(self) -> str:
        return await self._service_app.aget_access_token(self._org_id)

    async def _with_retry(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            bearer = await self._bearer()
            return await self._http.ajson_request(method, path, bearer=bearer, **kwargs)
        except AuthenticationError:
            await self._service_app.arefresh_for_org(self._org_id)
            bearer = await self._bearer()
            return await self._http.ajson_request(method, path, bearer=bearer, **kwargs)

    async def alist(self) -> list[DataSourceListItem]:
        """List all data sources for the organization.

        Returns:
            List of data source summary items.
        """
        data = await self._with_retry("GET", "/dataSources/")
        resp = DataSourceListResponse.model_validate(data)
        return resp.items

    async def aget(self, data_source_id: str) -> DataSource:
        """Get a data source by ID.

        Args:
            data_source_id: Unique data source identifier.

        Returns:
            Full data source resource.
        """
        data = await self._with_retry("GET", f"/dataSources/{data_source_id}")
        return DataSource.model_validate(data)

    async def acreate(self, payload: DataSourceCreate | dict[str, Any]) -> DataSource:
        """Create a new data source.

        Args:
            payload: Create payload as a model or dict with camelCase keys.

        Returns:
            Created data source resource.
        """
        body = (
            payload.model_dump(by_alias=True) if isinstance(payload, DataSourceCreate) else payload
        )
        data = await self._with_retry("POST", "/dataSources", json=body)
        return DataSource.model_validate(data)

    async def aupdate(
        self, data_source_id: str, payload: DataSourceUpdate | dict[str, Any]
    ) -> DataSource:
        """Update an existing data source.

        Args:
            data_source_id: Unique data source identifier.
            payload: Update payload as a model or dict.

        Returns:
            Updated data source resource.
        """
        body = payload.model_dump_api() if isinstance(payload, DataSourceUpdate) else payload
        data = await self._with_retry("PUT", f"/dataSources/{data_source_id}", json=body)
        return DataSource.model_validate(data)

    async def adelete(self, data_source_id: str) -> None:
        """Delete a data source.

        Args:
            data_source_id: Unique data source identifier.
        """
        bearer = await self._bearer()
        try:
            await self._http.arequest("DELETE", f"/dataSources/{data_source_id}", bearer=bearer)
        except AuthenticationError:
            await self._service_app.arefresh_for_org(self._org_id)
            bearer = await self._bearer()
            await self._http.arequest("DELETE", f"/dataSources/{data_source_id}", bearer=bearer)


class OrgClient:
    """Per-organization API client with DataSource and Schema resources.

    Attributes:
        org_id: Organization UUID this client is scoped to.
        data_sources: Data source CRUD operations.
        schemas: Schema discovery operations.
    """

    def __init__(
        self,
        org_id: str,
        service_app: ServiceAppTokenManager,
        http: HttpClient,
    ) -> None:
        """Initialize an org-scoped client.

        Args:
            org_id: Organization UUID.
            service_app: Service App token manager.
            http: Shared HTTP client.
        """
        self.org_id = org_id
        self.data_sources = DataSourceResource(org_id, service_app, http)
        self.schemas = SchemaResource(service_app, http, org_id)
