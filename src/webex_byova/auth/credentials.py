"""Credential loading helpers."""

from __future__ import annotations

import os

from webex_byova.models.auth import IntegrationCredentials, ServiceAppCredentials


def load_credentials_from_env() -> tuple[IntegrationCredentials, ServiceAppCredentials]:
    """Load Integration and Service App credentials from environment variables."""
    int_id = os.environ.get("WEBEX_INTEGRATION_CLIENT_ID")
    int_secret = os.environ.get("WEBEX_INTEGRATION_CLIENT_SECRET")
    sa_id = os.environ.get("WEBEX_SA_CLIENT_ID")
    sa_secret = os.environ.get("WEBEX_SA_CLIENT_SECRET")
    redirect = os.environ.get(
        "WEBEX_INTEGRATION_REDIRECT_URI", "http://127.0.0.1:8765/callback"
    )

    missing = [
        name
        for name, val in [
            ("WEBEX_INTEGRATION_CLIENT_ID", int_id),
            ("WEBEX_INTEGRATION_CLIENT_SECRET", int_secret),
            ("WEBEX_SA_CLIENT_ID", sa_id),
            ("WEBEX_SA_CLIENT_SECRET", sa_secret),
        ]
        if not val
    ]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return (
        IntegrationCredentials(
            client_id=int_id,  # type: ignore[arg-type]
            client_secret=int_secret,  # type: ignore[arg-type]
            redirect_uri=redirect,
        ),
        ServiceAppCredentials(
            client_id=sa_id,  # type: ignore[arg-type]
            client_secret=sa_secret,  # type: ignore[arg-type]
        ),
    )
