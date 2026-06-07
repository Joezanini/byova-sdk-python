# Examples

Runnable scripts live in the [`examples/`](https://github.com/Joezanini/byova-sdk-python/tree/main/examples) directory.

## quickstart_authorize.py

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

## quickstart_manual_token.py

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

## webhook_handler_fastapi.py

FastAPI server that handles `serviceApp` webhooks.

```bash
pip install fastapi uvicorn
export WEBEX_INTEGRATION_CLIENT_ID=...
# ... other WEBEX_* vars ...

python examples/webhook_handler_fastapi.py
```

POST webhook payloads to `http://localhost:8000/webhooks/webex`. See [Webhooks](webhooks.md) for production deployment notes.
