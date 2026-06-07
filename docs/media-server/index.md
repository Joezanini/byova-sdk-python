# BYOVA gRPC Media Server

The `webex_byova.media` module provides a developer-hosted BYOVA gRPC media server that hides all protobuf/gRPC details behind an async handler API.

Use it when Webex Contact Center connects to **your** server for live voice sessions — prompts, caller audio, DTMF, barge-in, and multi-turn dialogs. For data source registration and REST APIs, use the core `BYOVA` client alongside or independently.

## Install

```bash
pip install webex-byova[media]
```

The core package (`pip install webex-byova`) is unchanged; media dependencies (gRPC, WebSocket client) are gated behind the `[media]` extra.

## Quick links

- [Quickstart](quickstart.md) — hello world in under 15 minutes
- [Handlers](handlers.md) — events and session API
- [Configuration](configuration.md) — `MediaServerConfig` and env vars
- [WebSocket proxy](proxy.md) — external voice AI backends
- [Protocol notes](protocol-notes.md) — BYOVA turn closure and audio formats
- [Deployment](deployment.md) — TLS, token verification, BYODS coexistence
- [Examples](../guides/examples.md#media-server-voice) — all runnable scripts
- [API reference](../api/media.md) — generated class documentation

## Architecture

```text
Webex Contact Center  ←gRPC→  BYOVAMediaServer  ←handlers→  Your logic
                                      ↓ optional
                              WebSocketProxyConnector  ←→  External voice AI
```

Public API entry point:

```python
from webex_byova.media import BYOVAMediaServer, MediaServerConfig
```

## Runnable examples

| Script | Demonstrates |
|--------|--------------|
| `examples/media_server_minimal.py` | Single greeting on `session_start` |
| `examples/media_server_multiturn.py` | Audio input and session end |
| `examples/media_server_dtmf.py` | DTMF digit collection |
| `examples/media_server_proxy.py` | WebSocket proxy to external AI |
| `examples/byods_and_media_combined.py` | REST client + media server together |

## Related docs

- [Getting Started](../getting-started.md#run-a-media-server-voice) — prerequisites and first server
- [Architecture](../concepts/architecture.md#byova-media-server-optional) — how media fits with BYODS
- [Environment variables](../guides/environment-variables.md#media-server-optional) — `WEBEX_MEDIA_*` settings
