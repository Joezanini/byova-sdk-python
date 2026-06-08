# Getting Started

The SDK supports two complementary integration paths:

| Path | Use when | Entry point |
|------|----------|-------------|
| **BYODS REST** | Register data sources, ingest call metadata, schema-driven integrations | `BYOVA` client |
| **BYOVA media** | Host a voice virtual agent — prompts, caller audio, DTMF, multi-turn dialogs | `BYOVAMediaServer` |

Most production BYOVA apps use **both**: REST APIs for provisioning and webhooks, plus the gRPC media server for live call handling. See [Architecture](concepts/architecture.md) and [Deployment](media-server/deployment.md#coexistence-with-byods).

## Prerequisites

1. A [Webex Developer](https://developer.webex.com/) account
2. A **Webex Integration** with scopes:
   - `spark:all`
   - `spark:applications_token`
   - `application:webhooks_write`
   - `application:webhooks_read`
3. A **Webex Service App** with BYODS scopes:
   - `spark-admin:datasource_read`
   - `spark-admin:datasource_write`
4. Redirect URI registered on the Integration (e.g. `http://127.0.0.1:8765/callback`)

For the media server, Webex Contact Center must reach your server on the configured host/port (typically `50051`). See [Media Server Quickstart](media-server/quickstart.md#3-register-with-webex).

## Install

Core SDK:

```bash
pip install webex-byova
```

For the gRPC media server (voice streaming):

```bash
pip install "webex-byova[media]"
```

For development with docs and tests:

```bash
pip install -e ".[dev,docs,media]"
```

## Authorize Integration and register webhooks

```python
import asyncio
from webex_byova import BYOVA
from webex_byova.models import IntegrationCredentials, ServiceAppCredentials

sdk = BYOVA(
    integration=IntegrationCredentials(...),
    service_app=ServiceAppCredentials(...),
)

async def setup():
    tokens = await sdk.integration.aauthorize()
    print("Authorized; access token expires at", tokens.expires_at)
    await sdk.webhooks.aensure_service_app_webhooks(
        "https://your-server.example.com/webhooks/webex"
    )

asyncio.run(setup())
```

Or load credentials from environment variables — see [Environment Variables](guides/environment-variables.md).

## Register a data source

After a customer admin authorizes your Service App, handle the `authorized` webhook, then:

```python
client = await sdk.aget_client_for_org(org_id)
await client.data_sources.acreate({
    "audience": "MyVirtualAgent",
    "subject": "callAudioData",
    "nonce": "unique-nonce-string",
    "schemaId": "<schema-uuid>",
    "url": "https://your-dap.example.com/ingest",
    "tokenLifetimeMinutes": 60,
})
```

Discover schemas first — see [Schemas](guides/schemas.md).

For **voice** integrations, register a data source with schema `5397013b-7920-4ffc-807c-e8a3e0a18f43` (Voice Virtual Agent) and point the URL to your media server endpoint. Details: [Media Server Quickstart — Register with Webex](media-server/quickstart.md#3-register-with-webex).

## Run a media server (voice)

Minimal hello-world server (requires `[media]` extra):

```python
import asyncio
from webex_byova.media import BYOVAMediaServer, MediaServerConfig

async def main():
    server = BYOVAMediaServer(MediaServerConfig(port=50051, verify_tokens=False))

    @server.on("session_start")
    async def greet(session, turn):
        await turn.play_prompt(text="Hello from webex-byova")

    async with server:
        await server._grpc_server.wait_for_termination()

asyncio.run(main())
```

Or start from environment variables:

```python
server = BYOVAMediaServer.from_env()
```

See [Media Server Quickstart](media-server/quickstart.md) for the full walkthrough, handler events, and local validation with pytest. Runnable scripts live in `examples/media_server_*.py` — catalogued in [Examples](guides/examples.md).

## Next steps

### BYODS and platform

- [Architecture](concepts/architecture.md) — two-tier credentials and async conventions
- [Automated Token Flow](automated-token-flow.md) — end-to-end multi-tenant sequence
- [Webhooks](guides/webhooks.md) — handle authorized/deauthorized events
- [Examples](guides/examples.md) — OAuth, webhooks, and sandbox scripts

### Media server

- [Media Server Overview](media-server/index.md) — architecture and public API
- [Handlers](media-server/handlers.md) — events, `TurnContext`, and `MediaSession`
- [Configuration](media-server/configuration.md) — `MediaServerConfig` and env vars
- [WebSocket Proxy](media-server/proxy.md) — bridge to external voice AI
- [API Reference: webex_byova.media](api/media.md)
