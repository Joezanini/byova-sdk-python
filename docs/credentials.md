# Credentials

The SDK uses a **two-tier credential model**. You supply all OAuth client credentials from the Webex Developer Portal.

## Integration (developer-owned)

| Field | Description |
|-------|-------------|
| `client_id` | Integration Client ID |
| `client_secret` | Integration Client Secret |
| `redirect_uri` | Must match a redirect URI on the Integration |

Used for: Integration OAuth, webhook registration, fetching Service App tokens per org.

**Who authorizes:** The developer who owns the Integration — via `integration.authorize()`.

## Service App (per customer org)

| Field | Description |
|-------|-------------|
| `client_id` | Service App Client ID |
| `client_secret` | Service App Client Secret |

Used for: Request body when calling `POST /applications/{id}/token`; Bearer token on DataSource API calls.

**Who authorizes:** Each customer's Full Admin in Control Hub — not via SDK OAuth.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `WEBEX_INTEGRATION_CLIENT_ID` | Integration client ID |
| `WEBEX_INTEGRATION_CLIENT_SECRET` | Integration client secret |
| `WEBEX_INTEGRATION_REDIRECT_URI` | OAuth redirect (default `http://127.0.0.1:8765/callback`) |
| `WEBEX_SA_CLIENT_ID` | Service App client ID |
| `WEBEX_SA_CLIENT_SECRET` | Service App client secret |
