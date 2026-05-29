"""Webex auth utility functions."""

from __future__ import annotations

import base64


def derive_application_id(service_app_client_id: str) -> str:
    """Derive Service App application ID from client ID (base64url)."""
    prefix = "ciscospark://us/APPLICATION/"
    raw = (prefix + service_app_client_id).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def decode_org_id(encoded_org_id: str) -> str:
    """Decode org ID from webhook authorized event payload."""
    padded = encoded_org_id + "=" * (-len(encoded_org_id) % 4)
    decoded = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
    parts = decoded.split("/")
    if len(parts) >= 5:
        return parts[4]
    return decoded
