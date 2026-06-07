# Environment Variables

Use environment variables for credentials and quick-start scripts. Load them with `BYOVA.from_env()` or `load_credentials_from_env()`.

## Required for `from_env()`

| Variable | Description |
|----------|-------------|
| `WEBEX_INTEGRATION_CLIENT_ID` | Integration client ID from Webex Developer portal |
| `WEBEX_INTEGRATION_CLIENT_SECRET` | Integration client secret |
| `WEBEX_SA_CLIENT_ID` | Service App client ID |
| `WEBEX_SA_CLIENT_SECRET` | Service App client secret |

## Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBEX_INTEGRATION_REDIRECT_URI` | `http://127.0.0.1:8765/callback` | OAuth redirect URI registered on the Integration |
| `WEBEX_ORG_ID` | — | Organization UUID (sandbox manual token example) |
| `WEBEX_SA_REFRESH_TOKEN` | — | Service App refresh token (sandbox manual token example) |
| `WEBEX_WEBHOOK_TARGET_URL` | — | HTTPS URL for webhook registration in quickstart example |
| `PORT` | `8000` | Port for FastAPI webhook example |

## Example `.env` setup

```bash
export WEBEX_INTEGRATION_CLIENT_ID=your-integration-id
export WEBEX_INTEGRATION_CLIENT_SECRET=your-integration-secret
export WEBEX_SA_CLIENT_ID=your-service-app-id
export WEBEX_SA_CLIENT_SECRET=your-service-app-secret
export WEBEX_INTEGRATION_REDIRECT_URI=http://127.0.0.1:8765/callback
export WEBEX_WEBHOOK_TARGET_URL=https://your-tunnel.example.com/webhooks/webex
```

```python
from webex_byova import BYOVA

sdk = BYOVA.from_env()
```

!!! warning "Never commit secrets"
    Use environment variables or a secrets manager. Do not hardcode credentials or commit `.env` files.

See [Credentials](../credentials.md) for the two-tier credential model.
