"""HTTP client wrapper with error mapping."""

from __future__ import annotations

from typing import Any

import httpx

from webex_byova.config import BYOVAConfig
from webex_byova.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    WebexBYOVAError,
)


def raise_for_status(response: httpx.Response) -> None:
    """Map HTTP status codes to SDK exceptions."""
    if response.is_success:
        return

    body: Any
    try:
        body = response.json()
    except Exception:
        body = response.text

    message = f"HTTP {response.status_code}"
    if isinstance(body, dict) and "message" in body:
        message = f"{message}: {body['message']}"
    elif isinstance(body, str) and body:
        message = f"{message}: {body[:200]}"

    status = response.status_code
    if status in (401, 403):
        raise AuthenticationError(message, status_code=status, body=body)
    if status == 404:
        raise NotFoundError(message, status_code=status, body=body)
    if status in (400, 409, 415):
        raise ValidationError(message, status_code=status, body=body)
    if status == 429:
        retry_after = response.headers.get("Retry-After")
        raise RateLimitError(
            message,
            status_code=status,
            body=body,
            retry_after=int(retry_after) if retry_after and retry_after.isdigit() else None,
        )
    raise WebexBYOVAError(message, status_code=status, body=body)


class HttpClient:
    """Sync/async HTTP wrapper around httpx."""

    def __init__(self, config: BYOVAConfig) -> None:
        self._config = config
        self._sync = httpx.Client(timeout=config.timeout)
        self._async = httpx.AsyncClient(timeout=config.timeout)

    @property
    def config(self) -> BYOVAConfig:
        return self._config

    def close(self) -> None:
        self._sync.close()

    async def aclose(self) -> None:
        await self._async.aclose()

    def request(
        self,
        method: str,
        path: str,
        *,
        bearer: str | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        url = path if path.startswith("http") else f"{self._config.base_url}{path}"
        hdrs = dict(headers or {})
        if bearer:
            hdrs["Authorization"] = f"Bearer {bearer}"
        if json is not None:
            hdrs.setdefault("Content-Type", "application/json")
        response = self._sync.request(
            method, url, json=json, data=data, params=params, headers=hdrs
        )
        raise_for_status(response)
        return response

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        bearer: str | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        url = path if path.startswith("http") else f"{self._config.base_url}{path}"
        hdrs = dict(headers or {})
        if bearer:
            hdrs["Authorization"] = f"Bearer {bearer}"
        if json is not None:
            hdrs.setdefault("Content-Type", "application/json")
        response = await self._async.request(
            method, url, json=json, data=data, params=params, headers=hdrs
        )
        raise_for_status(response)
        return response

    def json_request(self, method: str, path: str, **kwargs: Any) -> Any:
        return self.request(method, path, **kwargs).json()

    async def ajson_request(self, method: str, path: str, **kwargs: Any) -> Any:
        return (await self.arequest(method, path, **kwargs)).json()
