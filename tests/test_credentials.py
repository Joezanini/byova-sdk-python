"""Tests for credential utilities."""

from webex_byova.auth.utils import decode_org_id, derive_application_id


def test_derive_application_id() -> None:
    app_id = derive_application_id("Cf2e954e018f2de8c1403e2618323551df65")
    assert app_id
    assert "=" not in app_id


def test_decode_org_id_roundtrip_style() -> None:
    import base64

    org_uuid = "63b02f90-9cc6-43b8-aa6d-cad425ac554c"
    encoded = (
        base64.urlsafe_b64encode(f"ciscospark://us/ORGANIZATION/{org_uuid}".encode())
        .decode()
        .rstrip("=")
    )
    assert decode_org_id(encoded) == org_uuid
