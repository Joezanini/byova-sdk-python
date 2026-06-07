# Configuration

Global SDK behavior is controlled via `BYOVAConfig`:

```python
from webex_byova import BYOVA, BYOVAConfig

config = BYOVAConfig(
    region="us",
    timeout=30.0,
)
sdk = BYOVA(integration=..., service_app=..., config=config)
```

## Fields

| Field | Default | Description |
|-------|---------|-------------|
| `base_url` | `https://webexapis.com/v1` | Webex REST API base URL |
| `authorize_url` | `https://webexapis.com/v1/authorize` | OAuth authorization endpoint |
| `token_url` | `https://webexapis.com/v1/access_token` | OAuth token endpoint |
| `jwk_url_us` | US idbroker URL | JWK verification keys (US) |
| `jwk_url_eu` | EU idbroker URL | JWK verification keys (EU) |
| `region` | `"us"` | Active region for JWK lookup (`us` or `eu`) |
| `timeout` | `30.0` | HTTP request timeout in seconds |

## US vs EU regions

Set `region="eu"` for European deployments. This selects the EU JWK endpoint for JWS verification:

```python
config = BYOVAConfig(region="eu")
sdk = BYOVA(..., config=config)
claims = await sdk.averify_jws_token(jws_token)
```

See [JWS Verification](../jws-verification.md) for endpoint URLs.

## Custom base URLs

Override `base_url`, `authorize_url`, and `token_url` for testing against mocks or staging environments:

```python
config = BYOVAConfig(
    base_url="http://localhost:8080/v1",
    authorize_url="http://localhost:8080/v1/authorize",
    token_url="http://localhost:8080/v1/access_token",
)
```

## Accessing config

```python
print(sdk.config.region)
print(sdk.config.jwk_url)  # property — resolves US or EU URL
```
