"""SDK configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BYOVAConfig:
    """Global SDK configuration."""

    base_url: str = "https://webexapis.com/v1"
    authorize_url: str = "https://webexapis.com/v1/authorize"
    token_url: str = "https://webexapis.com/v1/access_token"
    jwk_url_us: str = "https://idbroker.webex.com/idb/oauth2/v2/keys/verificationjwk"
    jwk_url_eu: str = "https://idbroker-eu.webex.com/idb/oauth2/v2/keys/verificationjwk"
    region: str = "us"
    timeout: float = 30.0

    @property
    def jwk_url(self) -> str:
        if self.region.lower() == "eu":
            return self.jwk_url_eu
        return self.jwk_url_us
