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
    await sdk.integration.aauthorize()
    await sdk.webhooks.aensure_service_app_webhooks(
        "https://your-server.example.com/webhooks/webex"
    )

asyncio.run(setup())
```

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
