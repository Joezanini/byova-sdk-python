# webex-byova

Python SDK for **Webex Contact Center BYOVA** and the foundational **Bring Your Own Data Source (BYODS)** APIs.

Simplify Service App token management, Integration OAuth, DataSource CRUD, schema discovery, and JWS verification.

## Install

```bash
pip install webex-byova
```

## Quick start

```python
import asyncio
from webex_byova import BYOVA
from webex_byova.models import IntegrationCredentials, ServiceAppCredentials

sdk = BYOVA(
    integration=IntegrationCredentials(
        client_id="YOUR_INTEGRATION_CLIENT_ID",
        client_secret="YOUR_INTEGRATION_CLIENT_SECRET",
        redirect_uri="http://127.0.0.1:8765/callback",
    ),
    service_app=ServiceAppCredentials(
        client_id="YOUR_SERVICE_APP_CLIENT_ID",
        client_secret="YOUR_SERVICE_APP_CLIENT_SECRET",
    ),
)

async def main():
  # Developer authorizes Integration (not customer admin)
  await sdk.integration.aauthorize(open_browser=True)

  await sdk.webhooks.aensure_service_app_webhooks(
      target_url="https://your-app.example.com/webhooks/webex",
  )

asyncio.run(main())
```

After a customer admin authorizes your Service App in Control Hub, handle the webhook:

```python
result = await sdk.ahandle_service_app_webhook(webhook_json)
client = await sdk.aget_client_for_org(result.org_id)
sources = await client.data_sources.alist()
```

## Environment variables

```bash
export WEBEX_INTEGRATION_CLIENT_ID=...
export WEBEX_INTEGRATION_CLIENT_SECRET=...
export WEBEX_SA_CLIENT_ID=...
export WEBEX_SA_CLIENT_SECRET=...
export WEBEX_INTEGRATION_REDIRECT_URI=http://127.0.0.1:8765/callback
```

```python
sdk = BYOVA.from_env()
```

## Documentation

Full documentation: **[joezanini.github.io/byova-sdk-python](https://joezanini.github.io/byova-sdk-python/)**

Build and preview locally:

```bash
pip install -e ".[docs]"
mkdocs serve -f docs/mkdocs.yml   # http://127.0.0.1:8000
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

MIT — see [LICENSE](LICENSE).
