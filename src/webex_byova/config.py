"""SDK configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BYOVAConfig:
    """Global SDK configuration for Webex API endpoints and behavior.

    Attributes:
        base_url: Base URL for Webex REST API requests.
        authorize_url: OAuth authorization endpoint.
        token_url: OAuth token exchange and refresh endpoint.
        jwk_url_us: JWK verification URL for US region.
        jwk_url_eu: JWK verification URL for EU region.
        region: Active region for JWK lookup (``us`` or ``eu``).
        timeout: HTTP request timeout in seconds.
    """

    base_url: str = "https://webexapis.com/v1"
    authorize_url: str = "https://webexapis.com/v1/authorize"
    token_url: str = "https://webexapis.com/v1/access_token"
    jwk_url_us: str = "https://idbroker.webex.com/idb/oauth2/v2/keys/verificationjwk"
    jwk_url_eu: str = "https://idbroker-eu.webex.com/idb/oauth2/v2/keys/verificationjwk"
    region: str = "us"
    timeout: float = 30.0

    @property
    def jwk_url(self) -> str:
        """Return the JWK URL for the configured region.

        Returns:
            JWK verification URL for ``us`` or ``eu`` based on ``region``.
        """
        if self.region.lower() == "eu":
            return self.jwk_url_eu
        return self.jwk_url_us
