# Authentication

## Responsibilities

| Actor | Action |
|-------|--------|
| Developer | Authorize Integration via SDK |
| Developer | Register webhooks, host HTTPS endpoint |
| Customer admin | Authorize Service App in Control Hub |
| SDK | Fetch/store per-org Service App tokens |

## Token storage

Implement `TokenStorage` for production (Redis, database, secrets manager):

```python
from webex_byova.auth import TokenStorage

class RedisTokenStorage:
    async def get_integration_tokens(self): ...
    async def set_integration_tokens(self, tokens): ...
    # ...
```

Default: `InMemoryTokenStorage` (development only).

## Paths to Service App tokens

**Webhook (production):** `handle_service_app_webhook` after customer admin authorizes.

**Manual (sandbox):** `await sdk.service_app.asave_registration(org_id, refresh_token)`

**On-demand:** `await sdk.service_app.afetch_token_for_org(org_id)` when org is already authorized.
