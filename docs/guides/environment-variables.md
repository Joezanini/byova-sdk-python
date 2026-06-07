# Environment Variables

Use environment variables for credentials and quick-start scripts. Load them with `BYOVA.from_env()` or `load_credentials_from_env()`.

Media server settings load separately via `MediaServerConfig.from_env()` or `BYOVAMediaServer.from_env()` — see [Media server variables](#media-server-optional) below.

## Required for `BYOVA.from_env()`

| Variable | Description |
|----------|-------------|
| `WEBEX_INTEGRATION_CLIENT_ID` | Integration client ID from Webex Developer portal |
| `WEBEX_INTEGRATION_CLIENT_SECRET` | Integration client secret |
| `WEBEX_SA_CLIENT_ID` | Service App client ID |
| `WEBEX_SA_CLIENT_SECRET` | Service App client secret |

## Optional (BYODS / platform)

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBEX_INTEGRATION_REDIRECT_URI` | `http://127.0.0.1:8765/callback` | OAuth redirect URI registered on the Integration |
| `WEBEX_ORG_ID` | — | Organization UUID (sandbox manual token example) |
| `WEBEX_SA_REFRESH_TOKEN` | — | Service App refresh token (sandbox manual token example) |
| `WEBEX_WEBHOOK_TARGET_URL` | — | HTTPS URL for webhook registration in quickstart example |
| `PORT` | `8000` | Port for FastAPI webhook example |

## Media server (optional)

Used by `MediaServerConfig.from_env()` and `BYOVAMediaServer.from_env()`. Requires `pip install webex-byova[media]`.

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBEX_MEDIA_HOST` | `0.0.0.0` | Bind address |
| `WEBEX_MEDIA_PORT` | `50051` | Listen port |
| `WEBEX_MEDIA_AUDIO_MODE` | `chunked` | Audio wire format (`chunked` or `full`) |
| `WEBEX_MEDIA_SAMPLE_RATE` | `8000` | Telephony sample rate (`8000` or `16000`) |
| `WEBEX_MEDIA_BARGE_IN_ENABLED` | `false` | Enable barge-in |
| `WEBEX_MEDIA_INPUT_MODE` | `voice` | Input mode (`voice`, `dtmf`, or `mixed`) |
| `WEBEX_MEDIA_VERIFY_TOKENS` | `true` | JWS verification for inbound sessions |
| `WEBEX_MEDIA_NO_INPUT_TIMEOUT` | `5.0` | No-input timeout in seconds |
| `WEBEX_MEDIA_TLS_CERT` | — | TLS certificate path |
| `WEBEX_MEDIA_TLS_KEY` | — | TLS private key path |

Full field reference: [Media Server Configuration](../media-server/configuration.md).

## Example `.env` setup

BYODS client:

```bash
export WEBEX_INTEGRATION_CLIENT_ID=your-integration-id
export WEBEX_INTEGRATION_CLIENT_SECRET=your-integration-secret
export WEBEX_SA_CLIENT_ID=your-service-app-id
export WEBEX_SA_CLIENT_SECRET=your-service-app-secret
export WEBEX_INTEGRATION_REDIRECT_URI=http://127.0.0.1:8765/callback
export WEBEX_WEBHOOK_TARGET_URL=https://your-tunnel.example.com/webhooks/webex
```

Media server (add when running voice examples):

```bash
export WEBEX_MEDIA_HOST=0.0.0.0
export WEBEX_MEDIA_PORT=50051
export WEBEX_MEDIA_VERIFY_TOKENS=false   # local dev only
```

```python
from webex_byova import BYOVA
from webex_byova.media import BYOVAMediaServer

sdk = BYOVA.from_env()
server = BYOVAMediaServer.from_env()
```

!!! warning "Never commit secrets"
    Use environment variables or a secrets manager. Do not hardcode credentials or commit `.env` files.

See [Credentials](../credentials.md) for the two-tier credential model.
