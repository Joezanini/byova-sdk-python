# Error Handling

The SDK raises typed exceptions derived from `WebexBYOVAError`. All exceptions carry optional `status_code` and `body` attributes from the Webex API response.

## Exception hierarchy

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
