"""Tests for JWS verification."""

import base64
import json
from unittest.mock import patch

import jwt
import pytest

from webex_byova.jws.verifier import JWSVerifier


def _minimal_jws_header() -> str:
    hdr = json.dumps({"alg": "RS256", "kid": "missing"}).encode()
    header = base64.urlsafe_b64encode(hdr).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(b"{}").rstrip(b"=").decode()
    sig = base64.urlsafe_b64encode(b"sig").rstrip(b"=").decode()
    return f"{header}.{payload}.{sig}"


def test_jws_verifier_requires_jwks() -> None:
    verifier = JWSVerifier()
    token = _minimal_jws_header()
    with patch.object(verifier, "_fetch_jwks", return_value={"keys": []}):
        with pytest.raises((ValueError, jwt.exceptions.DecodeError)):
            verifier.verify(token)
