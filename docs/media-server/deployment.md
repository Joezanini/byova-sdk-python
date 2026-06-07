# Deployment Guide

## Requirements

- Python ≥3.10
- `pip install webex-byova[media]`
- Network access from Webex Contact Center to your server port

## TLS

For production, terminate TLS at a load balancer or configure server-side TLS:

```python
MediaServerConfig(
    port=50051,
    tls_cert="/path/to/cert.pem",
    tls_key="/path/to/key.pem",
)
```

## Token verification

`verify_tokens=True` (default) validates inbound JWS tokens using the existing SDK `JWSVerifier`. Disable only for local development:

```python
MediaServerConfig(verify_tokens=False)
```

## Coexistence with BYODS

The media module is optional and does not affect existing BYODS APIs:

```python
from webex_byova import BYOVA
from webex_byova.media import BYOVAMediaServer
```

Run both in the same process — see `examples/byods_and_media_combined.py`.

## Sample rates

Use `8000` for standard telephony. Use `16000` when your audio pipeline produces wideband μ-law. Mismatch causes pitch/speed errors.

## CI

Install with the media extra in CI:

```bash
pip install -e ".[dev,media]"
pytest tests/ -v
```
