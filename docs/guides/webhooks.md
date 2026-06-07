# Webhooks

Service App lifecycle events (`authorized`, `deauthorized`) are delivered via **HTTPS webhooks**, not Webex Mercury WebSockets.

## Register webhooks

After Integration OAuth, register both events:

```python
created = await sdk.webhooks.aensure_service_app_webhooks(
    "https://your-server.example.com/webhooks/webex"
)
print(f"Created {len(created)} webhook(s)")
```

`aensure_service_app_webhooks` is idempotent — it skips events already registered for the same target URL.

You can also manage webhooks individually:

```python
webhooks = await sdk.webhooks.alist_service_app_webhooks(
    target_url="https://your-server.example.com/webhooks/webex"
)
```

## Handle incoming events

Use `BYOVA.ahandle_service_app_webhook()` to process payloads:

```python
result = await sdk.ahandle_service_app_webhook(payload)

if result.event == "authorized":
    # Tokens fetched and stored; use result.org_id
    client = await sdk.aget_client_for_org(result.org_id)
elif result.event == "deauthorized":
    # Stored tokens removed for result.org_id
    pass
```

## FastAPI example

See [`examples/webhook_handler_fastapi.py`](https://github.com/Joezanini/byova-sdk-python/blob/main/examples/webhook_handler_fastapi.py):

```python
from fastapi import FastAPI, Request
from webex_byova import BYOVA

app = FastAPI()
sdk = BYOVA.from_env()

@app.post("/webhooks/webex")
async def webex_webhook(request: Request):
    payload = await request.json()
    result = await sdk.ahandle_service_app_webhook(payload)
    return {"status": "ok", "org_id": result.org_id, "event": result.event}
```

## Requirements

- **HTTPS** endpoint reachable from the public internet (or use a tunnel like ngrok for development)
- Set `WEBEX_WEBHOOK_TARGET_URL` when running the authorize quickstart example
- Webhook registration requires Integration scopes `application:webhooks_write` and `application:webhooks_read`

## Event flow

See [Automated Token Flow](../automated-token-flow.md) for the end-to-end sequence diagram.
