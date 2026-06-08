# webex-byova

Python SDK for Webex Contact Center **Bring Your Own Virtual Agent (BYOVA)** and **Bring Your Own Data Source (BYODS)**.

## Features

### BYODS and platform APIs

- **Integration OAuth** with built-in redirect listener (`integration.aauthorize()`)
- **Service App tokens** per organization (webhook-driven or manual)
- **DataSource CRUD** — register, list, update, delete data sources
- **Schema discovery** — list and inspect BYODS schemas
- **JWS verification** — validate inbound tokens from Webex

### BYOVA gRPC media server

Install with the optional `[media]` extra (`pip install "webex-byova[media]"`):

- **Handler-based media server** — `BYOVAMediaServer` with async event callbacks (no protobuf/gRPC code required)
- **Turn-based sessions** — play prompts, collect voice or DTMF input, barge-in, multi-turn dialogs
- **WebSocket proxy** — bridge sessions to external voice AI backends via `WebSocketProxyConnector`
- **Protocol compliance** — BYOVA chunking, μ-law audio, and turn closure handled internally
- **Coexistence with BYODS** — run REST APIs and the media server in the same process

## Install

Core SDK (BYODS, OAuth, webhooks):

```bash
pip install webex-byova
```

Voice / gRPC media server:

```bash
pip install "webex-byova[media]"
```

## Quick links

| Topic | Guide |
|-------|-------|
| First steps | [Getting Started](getting-started.md) |
| How it fits together | [Architecture](concepts/architecture.md) |
| OAuth flow | [Integration OAuth](integration-oauth.md) |
| Multi-tenant setup | [Automated Token Flow](automated-token-flow.md) |
| Webhook handler | [Webhooks](guides/webhooks.md) |
| **Media server overview** | [BYOVA gRPC Media Server](media-server/index.md) |
| **Media quickstart** | [Media Server Quickstart](media-server/quickstart.md) |
| **Runnable examples** | [Examples](guides/examples.md) |
| API reference | [webex_byova](api/webex_byova.md) · [webex_byova.media](api/media.md) |

See [Getting Started](getting-started.md) for the BYODS walkthrough, or jump to the [Media Server Quickstart](media-server/quickstart.md) for voice integration.
