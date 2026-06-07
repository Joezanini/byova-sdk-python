# webex-byova

Python SDK for **Webex Contact Center BYOVA** and the foundational **Bring Your Own Data Source (BYODS)** APIs.

Simplify Service App token management, Integration OAuth, DataSource CRUD, schema discovery, JWS verification, and BYOVA gRPC media streaming.

## Install

```bash
pip install webex-byova
```

For the gRPC media server (voice virtual agent streaming), install the optional dependencies:

```bash
pip install "webex-byova[media]"
```

## Quick start (BYODS)

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

## Quick start (media server)

Requires `pip install "webex-byova[media]"`:

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

See [Media Server Quickstart](https://joezanini.github.io/byova-sdk-python/media-server/quickstart/) and `examples/media_server_minimal.py`.

## Examples

| Area | Scripts |
|------|---------|
| OAuth / webhooks | `quickstart_authorize.py`, `webhook_handler_fastapi.py` |
| Sandbox BYODS | `quickstart_manual_token.py` |
| Voice / media | `media_server_minimal.py`, `media_server_multiturn.py`, `media_server_dtmf.py`, `media_server_proxy.py`, `byods_and_media_combined.py` |

Full catalog: [Examples guide](https://joezanini.github.io/byova-sdk-python/guides/examples/).

## Environment variables

```bash
export WEBEX_INTEGRATION_CLIENT_ID=...
export WEBEX_INTEGRATION_CLIENT_SECRET=...
export WEBEX_SA_CLIENT_ID=...
export WEBEX_SA_CLIENT_SECRET=...
export WEBEX_INTEGRATION_REDIRECT_URI=http://127.0.0.1:8765/callback
```

Media server (optional):

```bash
export WEBEX_MEDIA_HOST=0.0.0.0
export WEBEX_MEDIA_PORT=50051
```

```python
sdk = BYOVA.from_env()
server = BYOVAMediaServer.from_env()  # requires [media]
```

## Documentation

Full documentation: **[joezanini.github.io/byova-sdk-python](https://joezanini.github.io/byova-sdk-python/)**

- [Getting Started](https://joezanini.github.io/byova-sdk-python/getting-started/)
- [Media Server Overview](https://joezanini.github.io/byova-sdk-python/media-server/)
- [API: webex_byova.media](https://joezanini.github.io/byova-sdk-python/api/media/)

Build and preview locally:

```bash
pip install -e ".[docs,media]"
mkdocs serve -f docs/mkdocs.yml   # http://127.0.0.1:8000
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## License

MIT — see [LICENSE](LICENSE).
