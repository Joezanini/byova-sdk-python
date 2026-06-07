# Getting Started

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

## Install

```bash
pip install webex-byova
```

For development with docs and tests:

```bash
pip install -e ".[dev,docs]"
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

## Next steps

- [Architecture](concepts/architecture.md) — two-tier credentials and async conventions
- [Automated Token Flow](automated-token-flow.md) — end-to-end multi-tenant sequence
- [Webhooks](guides/webhooks.md) — handle authorized/deauthorized events
- [Examples](guides/examples.md) — runnable scripts in `examples/`
