"""Webex auth utility functions."""

from __future__ import annotations

import base64


def derive_application_id(service_app_client_id: str) -> str:
    """Derive the Service App application ID from its client ID.

    Webex encodes the application ID as base64url of
    ``ciscospark://us/APPLICATION/{client_id}``.

    Args:
        service_app_client_id: Service App OAuth client ID.

    Returns:
        Base64url-encoded application ID used in API paths.
    """
    prefix = "ciscospark://us/APPLICATION/"
    raw = (prefix + service_app_client_id).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def decode_org_id(encoded_org_id: str) -> str:
    """Decode an organization ID from a webhook ``orgId`` value.

    Webex sends a base64url-encoded URI in authorized webhook payloads.
    This extracts the org UUID from the decoded path.

    Args:
        encoded_org_id: Base64url-encoded org identifier from a webhook.

    Returns:
        Decoded organization UUID, or the full decoded string if parsing fails.
    """
    padded = encoded_org_id + "=" * (-len(encoded_org_id) % 4)
    decoded = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
    parts = decoded.split("/")
    if len(parts) >= 5:
        return parts[4]
    return decoded
