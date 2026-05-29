"""Pluggable token storage."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from webex_byova.models.auth import OAuthTokens, ServiceAppTokens


@runtime_checkable
class TokenStorage(Protocol):
    """Store Integration and per-org Service App tokens."""

    async def get_integration_tokens(self) -> OAuthTokens | None: ...

    async def set_integration_tokens(self, tokens: OAuthTokens) -> None: ...

    async def get_service_app_tokens(self, org_id: str) -> ServiceAppTokens | None: ...

    async def set_service_app_tokens(self, org_id: str, tokens: ServiceAppTokens) -> None: ...

    async def delete_service_app_tokens(self, org_id: str) -> None: ...

    async def list_registered_orgs(self) -> list[str]: ...


class InMemoryTokenStorage:
    """Default in-memory token storage."""

    def __init__(self) -> None:
        self._integration: OAuthTokens | None = None
        self._service_apps: dict[str, ServiceAppTokens] = {}

    async def get_integration_tokens(self) -> OAuthTokens | None:
        return self._integration

    async def set_integration_tokens(self, tokens: OAuthTokens) -> None:
        self._integration = tokens

    async def get_service_app_tokens(self, org_id: str) -> ServiceAppTokens | None:
        return self._service_apps.get(org_id)

    async def set_service_app_tokens(self, org_id: str, tokens: ServiceAppTokens) -> None:
        self._service_apps[org_id] = tokens

    async def delete_service_app_tokens(self, org_id: str) -> None:
        self._service_apps.pop(org_id, None)

    async def list_registered_orgs(self) -> list[str]:
        return list(self._service_apps.keys())
