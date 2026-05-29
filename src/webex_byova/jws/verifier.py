"""Verify inbound BYODS JWS tokens from Webex."""

from __future__ import annotations

from typing import Any

import httpx
import jwt

from webex_byova.config import BYOVAConfig


class JWSVerifier:
    """Fetch JWKs and verify JWS tokens."""

    def __init__(self, config: BYOVAConfig | None = None) -> None:
        self._config = config or BYOVAConfig()
        self._jwks_cache: dict[str, Any] | None = None

    def _fetch_jwks(self) -> dict[str, Any]:
        if self._jwks_cache is not None:
            return self._jwks_cache
        response = httpx.get(self._config.jwk_url, timeout=self._config.timeout)
        response.raise_for_status()
        self._jwks_cache = response.json()
        return self._jwks_cache

    def verify(self, jws_token: str) -> dict[str, Any]:
        """Verify JWS and return decoded claims."""
        jwks = self._fetch_jwks()
        try:
            header = jwt.get_unverified_header(jws_token)
        except jwt.exceptions.DecodeError as exc:
            raise ValueError(f"Invalid JWS token: {exc}") from exc
        kid = header.get("kid")
        key = None
        for jwk_key in jwks.get("keys", []):
            if jwk_key.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk_key)
                break
        if key is None and jwks.get("keys"):
            key = jwt.algorithms.RSAAlgorithm.from_jwk(jwks["keys"][0])

        if key is None:
            raise ValueError("No matching JWK found for token")

        return jwt.decode(
            jws_token,
            key=key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )

    async def averify(self, jws_token: str) -> dict[str, Any]:
        return self.verify(jws_token)
