"""Pluggable token storage."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from webex_byova.models.auth import OAuthTokens, ServiceAppTokens


@runtime_checkable
class TokenStorage(Protocol):
    """Protocol for storing Integration and per-org Service App tokens.

    Implement this protocol for production persistence (Redis, database, etc.).
    All methods are async to support non-blocking I/O backends.
    """

    async def get_integration_tokens(self) -> OAuthTokens | None:
        """Return stored Integration OAuth tokens, or ``None`` if not authorized."""

    async def set_integration_tokens(self, tokens: OAuthTokens) -> None:
        """Persist Integration OAuth tokens."""

    async def get_service_app_tokens(self, org_id: str) -> ServiceAppTokens | None:
        """Return Service App tokens for an org, or ``None`` if not registered."""

    async def set_service_app_tokens(self, org_id: str, tokens: ServiceAppTokens) -> None:
        """Persist Service App tokens for an organization."""

    async def delete_service_app_tokens(self, org_id: str) -> None:
        """Remove Service App tokens for an organization (deauthorization)."""

    async def list_registered_orgs(self) -> list[str]:
        """Return organization IDs with stored Service App tokens."""


class InMemoryTokenStorage:
    """Default in-process token storage for development and testing.

    Tokens are lost when the process exits. Use a custom ``TokenStorage``
    implementation for production deployments.
    """

    def __init__(self) -> None:
        """Initialize empty in-memory token stores."""
        self._integration: OAuthTokens | None = None
        self._service_apps: dict[str, ServiceAppTokens] = {}

    async def get_integration_tokens(self) -> OAuthTokens | None:
        """Return stored Integration OAuth tokens.

        Returns:
            Integration tokens, or ``None`` if not authorized.
        """
        return self._integration

    async def set_integration_tokens(self, tokens: OAuthTokens) -> None:
        """Store Integration OAuth tokens.

        Args:
            tokens: Tokens to persist.
        """
        self._integration = tokens

    async def get_service_app_tokens(self, org_id: str) -> ServiceAppTokens | None:
        """Return Service App tokens for an organization.

        Args:
            org_id: Organization UUID.

        Returns:
            Service App tokens, or ``None`` if the org is not registered.
        """
        return self._service_apps.get(org_id)

    async def set_service_app_tokens(self, org_id: str, tokens: ServiceAppTokens) -> None:
        """Store Service App tokens for an organization.

        Args:
            org_id: Organization UUID.
            tokens: Tokens to persist.
        """
        self._service_apps[org_id] = tokens

    async def delete_service_app_tokens(self, org_id: str) -> None:
        """Remove Service App tokens for an organization.

        Args:
            org_id: Organization UUID.
        """
        self._service_apps.pop(org_id, None)

    async def list_registered_orgs(self) -> list[str]:
        """Return all organization IDs with stored Service App tokens.

        Returns:
            List of registered organization UUIDs.
        """
        return list(self._service_apps.keys())
