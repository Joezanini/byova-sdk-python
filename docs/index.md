# webex-byova

Python SDK for Webex Contact Center **Bring Your Own Virtual Agent (BYOVA)** and **Bring Your Own Data Source (BYODS)**.

## Features

- **Integration OAuth** with built-in redirect listener (`integration.aauthorize()`)
- **Service App tokens** per organization (webhook-driven or manual)
- **DataSource CRUD** — register, list, update, delete data sources
- **Schema discovery** — list and inspect BYODS schemas
- **JWS verification** — validate inbound tokens from Webex

## Install

```bash
pip install webex-byova
```

## Quick links

| Topic | Guide |
|-------|-------|
| First steps | [Getting Started](getting-started.md) |
| How it fits together | [Architecture](concepts/architecture.md) |
| OAuth flow | [Integration OAuth](integration-oauth.md) |
| Multi-tenant setup | [Automated Token Flow](automated-token-flow.md) |
| Webhook handler | [Webhooks](guides/webhooks.md) |
| API reference | [webex_byova](api/webex_byova.md) |

See [Getting Started](getting-started.md) for the full walkthrough.
