# JWS Verification

When Webex sends data to your DAP endpoint, it includes a JWS token in the request header. Verify it before processing:

```python
claims = sdk.verify_jws_token(jws_token)
# or async:
claims = await sdk.averify_jws_token(jws_token)
```

## Regions

```python
from webex_byova import BYOVAConfig

config = BYOVAConfig(region="eu")  # uses EU JWK endpoint
sdk = BYOVA(..., config=config)
```

US JWK: `https://idbroker.webex.com/idb/oauth2/v2/keys/verificationjwk`

EU JWK: `https://idbroker-eu.webex.com/idb/oauth2/v2/keys/verificationjwk`

## Security

- Rotate `nonce` regularly on data source updates
- Refresh tokens before `tokenLifetimeMinutes` expires
- Never log full JWS tokens in production
