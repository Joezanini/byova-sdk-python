# Integration OAuth

The developer authorizes the **Integration** on their own behalf. The SDK provides a built-in redirect listener — no separate OAuth server required for local development.

## Primary flow: `authorize()`

```python
tokens = await sdk.integration.aauthorize(
    scopes=[
        "spark:applications_token",
        "application:webhooks_write",
        "application:webhooks_read",
    ],
    open_browser=True,
    timeout=300,
)
```

This will:

1. Build the authorization URL
2. Start a temporary HTTP server on `redirect_uri`
3. Open the system browser (optional)
4. Capture `?code=` from the redirect
5. Exchange the code and store tokens

## Manual / CI flow

```python
url, state = sdk.integration.get_authorization_url(scopes=[...])
# Complete OAuth in browser, then:
tokens = await sdk.integration.aexchange_code(code)
```

## Redirect URI requirements

- Must be registered on your Integration in the Developer Portal
- `http://127.0.0.1:8765/callback` works for local development
- Production integrations may use HTTPS callbacks on your own server; use `exchange_code()` if you handle the redirect externally

## Token refresh

```python
token = await sdk.integration.aget_access_token()  # auto-refreshes if expired
```
