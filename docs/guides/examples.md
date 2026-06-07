# Examples

Runnable scripts live in the [`examples/`](https://github.com/Joezanini/byova-sdk-python/tree/main/examples) directory.

## BYODS and platform

These examples use the core package (`pip install webex-byova`).

### quickstart_authorize.py

Integration OAuth plus optional webhook registration.

```bash
export WEBEX_INTEGRATION_CLIENT_ID=...
export WEBEX_INTEGRATION_CLIENT_SECRET=...
export WEBEX_SA_CLIENT_ID=...
export WEBEX_SA_CLIENT_SECRET=...
export WEBEX_WEBHOOK_TARGET_URL=https://your-tunnel.example.com/webhooks/webex

python examples/quickstart_authorize.py
```

Opens a browser for developer Integration authorization, then registers `authorized` and `deauthorized` webhooks if `WEBEX_WEBHOOK_TARGET_URL` is set.

### quickstart_manual_token.py

Sandbox path using a pre-existing Service App refresh token.

```bash
export WEBEX_INTEGRATION_CLIENT_ID=...
export WEBEX_INTEGRATION_CLIENT_SECRET=...
export WEBEX_SA_CLIENT_ID=...
export WEBEX_SA_CLIENT_SECRET=...
export WEBEX_ORG_ID=your-org-uuid
export WEBEX_SA_REFRESH_TOKEN=your-refresh-token

python examples/quickstart_manual_token.py
```

Registers the org via `asave_registration()`, then lists available schemas.

### webhook_handler_fastapi.py

FastAPI server that handles `serviceApp` webhooks.

```bash
pip install fastapi uvicorn
export WEBEX_INTEGRATION_CLIENT_ID=...
# ... other WEBEX_* vars ...

python examples/webhook_handler_fastapi.py
```

POST webhook payloads to `http://localhost:8000/webhooks/webex`. See [Webhooks](webhooks.md) for production deployment notes.

## Media server (voice)

These examples require the optional media extra:

```bash
pip install webex-byova[media]
```

For local development, disable token verification with `MediaServerConfig(verify_tokens=False)` or `WEBEX_MEDIA_VERIFY_TOKENS=false`. See [Media Server Configuration](../media-server/configuration.md).

### media_server_minimal.py

Smallest runnable media server — greets the caller on `session_start`.

```bash
python examples/media_server_minimal.py
```

Listens on `0.0.0.0:50051` by default. See [Media Server Quickstart](../media-server/quickstart.md).

### media_server_multiturn.py

Multi-turn dialog: welcome prompt, responds to caller audio, then ends the session.

```bash
python examples/media_server_multiturn.py
```

Demonstrates `session_start`, `audio_input`, and `session.end_session()`. See [Handlers](../media-server/handlers.md).

### media_server_dtmf.py

DTMF collection with `input_mode="dtmf"` — prompts for digits and echoes them back.

```bash
python examples/media_server_dtmf.py
```

Demonstrates `dtmf_input` events and `turn.end_turn()`.

### media_server_proxy.py

Forwards session media and events to an external WebSocket voice AI backend.

```bash
python examples/media_server_proxy.py
```

Configure the backend URL in the script or via proxy settings. See [WebSocket Proxy](../media-server/proxy.md).

### byods_and_media_combined.py

Runs `BYOVAMediaServer` alongside the `BYOVA` REST client in one process — the typical production layout.

```bash
python examples/byods_and_media_combined.py
```

See [Deployment — Coexistence with BYODS](../media-server/deployment.md#coexistence-with-byods).

## Validate with tests

```bash
pip install -e ".[dev,media]"
pytest tests/media/ -v
```

Key scenarios are listed in [Media Server Quickstart — Validation scenarios](../media-server/quickstart.md#validation-scenarios).
