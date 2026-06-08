# Error Handling

The SDK raises typed exceptions derived from `WebexBYOVAError`. All exceptions carry optional `status_code` and `body` attributes from the Webex API response where applicable.

## Exception hierarchy

### BYODS and platform

```
WebexBYOVAError
├── AuthenticationError      (401, 403)
├── NotFoundError            (404)
├── ValidationError          (400, 409, 415)
├── RateLimitError           (429)
├── OAuthRedirectError       (OAuth user denied)
├── OAuthRedirectTimeout     (redirect listener timeout)
└── OrgNotRegisteredError    (no tokens for org)
```

### Media server (`webex_byova.media`)

Requires `pip install "webex-byova[media]"`.

```
WebexBYOVAError
└── MediaServerError
    ├── MediaConfigError           (invalid MediaServerConfig)
    ├── DuplicateTurnStreamError   (concurrent turn stream rejected)
    ├── PromptValidationError      (invalid prompt audio/format)
    ├── ProxyConnectionError       (WebSocket backend unreachable)
    └── ProxyBufferOverflowError   (proxy buffer limit exceeded)
```

See [API Reference: Exceptions](../api/exceptions.md) for generated docstrings.

## Common exceptions

### `AuthenticationError`

Raised when OAuth or API authentication fails.

```python
try:
    token = await sdk.integration.aget_access_token()
except AuthenticationError as exc:
    print(exc.status_code, exc.body)
    await sdk.integration.aauthorize()
```

### `OrgNotRegisteredError`

Raised when requesting an `OrgClient` for an org without stored Service App tokens.

**Remediation:**

1. Wait for the customer admin to authorize your Service App in Control Hub
2. Handle the `authorized` webhook via `ahandle_service_app_webhook()`
3. Or use `service_app.asave_registration()` in sandbox environments

### `RateLimitError`

Raised on HTTP 429. Check `retry_after` for the recommended wait time:

```python
except RateLimitError as exc:
    await asyncio.sleep(exc.retry_after or 60)
```

### `OAuthRedirectTimeout`

The local redirect listener timed out during `aauthorize()`. Increase `timeout` or complete OAuth manually with `get_authorization_url()` + `aexchange_code()`.

### `ValidationError`

Raised for invalid webhook payloads or API validation errors. Inspect `exc.body` for Webex error details.

### Media server errors

Register an `error` handler on `BYOVAMediaServer` for runtime failures inside your callbacks:

```python
@server.on("error")
async def on_error(event, session, turn):
    print(event.message)
```

Configuration problems raise before the server starts:

```python
from webex_byova.media.exceptions import MediaConfigError, ProxyConnectionError

try:
    server = BYOVAMediaServer.from_env()
except MediaConfigError as exc:
    print(f"Invalid media config: {exc}")
```

During proxied sessions, a unreachable WebSocket backend raises `ProxyConnectionError`. Tune buffer limits if you see `ProxyBufferOverflowError` — see [WebSocket Proxy](../media-server/proxy.md).

## Example

```python
from webex_byova.exceptions import (
    AuthenticationError,
    OrgNotRegisteredError,
    RateLimitError,
    WebexBYOVAError,
)

try:
    client = await sdk.aget_client_for_org(org_id)
    sources = await client.data_sources.alist()
except OrgNotRegisteredError:
    print("Org not yet authorized — wait for webhook")
except AuthenticationError:
    await sdk.service_app.arefresh_for_org(org_id)
except RateLimitError as exc:
    await asyncio.sleep(exc.retry_after or 30)
except WebexBYOVAError as exc:
    print(f"API error {exc.status_code}: {exc}")
```

See the [Exceptions API reference](../api/exceptions.md) for full details.
