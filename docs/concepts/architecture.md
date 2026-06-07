# Architecture

The SDK is built around a **two-tier credential model** and **async-first** API design.

## Two-tier credentials

```mermaid
flowchart TB
  subgraph dev [Developer tier]
    Integration[Integration OAuth]
    Webhooks[Webhook registration]
  end
  subgraph org [Per-org tier]
    ServiceApp[Service App tokens]
    DataSources[DataSource CRUD]
    Schemas[Schema discovery]
  end
  Integration --> ServiceApp
  Integration --> Webhooks
  ServiceApp --> DataSources
  ServiceApp --> Schemas
```

| Tier | Who authorizes | SDK component | Purpose |
|------|----------------|---------------|---------|
| Integration | Developer (you) | `IntegrationTokenManager` | OAuth, webhooks, fetch org tokens |
| Service App | Customer admin | `ServiceAppTokenManager` | Per-org API access |

See [Credentials](../credentials.md) for field details.

## Multi-tenant org model

Each customer organization that authorizes your Service App gets its own token pair stored via `TokenStorage`. Use `BYOVA.aget_client_for_org(org_id)` to obtain an `OrgClient` scoped to that org:

```python
client = await sdk.aget_client_for_org(org_id)
await client.data_sources.acreate({...})
schemas = await client.schemas.alist()
```

The SDK raises `OrgNotRegisteredError` if you request a client for an org without stored tokens. Register orgs via webhooks or `service_app.asave_registration()` — see [Authentication](../authentication.md).

## Async-first conventions

All resource methods use the `a*` prefix (`alist`, `acreate`, `aauthorize`). Sync wrappers exist on select entry points (`authorize`, `get_client_for_org`, `verify_jws_token`) for convenience; they delegate to `asyncio.run()`.

**Recommended pattern:**

```python
import asyncio
from webex_byova import BYOVA

async def main():
    sdk = BYOVA.from_env()
    try:
        await sdk.integration.aauthorize()
        # ... async API calls ...
    finally:
        await sdk.aclose()

asyncio.run(main())
```

Always call `aclose()` when done to release HTTP connections.

## Component overview

| Component | Module | Role |
|-----------|--------|------|
| `BYOVA` | `webex_byova` | Facade wiring all subsystems |
| `IntegrationTokenManager` | `webex_byova.auth` | Developer OAuth flow |
| `ServiceAppTokenManager` | `webex_byova.auth` | Per-org token fetch/refresh |
| `WebhookManager` | `webex_byova.webhooks` | Register serviceApp hooks |
| `OrgClient` | `webex_byova.resources` | Org-scoped DataSource + Schema APIs |
| `JWSVerifier` | `webex_byova.jws` | Verify inbound data tokens |

For the full API surface, see [API Reference](../api/webex_byova.md).
