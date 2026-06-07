# BYOVA gRPC Media Server

The `webex_byova.media` module provides a developer-hosted BYOVA gRPC media server that hides all protobuf/gRPC details behind an async handler API.

## Install

```bash
pip install webex-byova[media]
```

## Quick links

- [Quickstart](quickstart.md)
- [Handlers](handlers.md)
- [Configuration](configuration.md)
- [WebSocket proxy](proxy.md)
- [Protocol notes](protocol-notes.md)
- [Deployment](deployment.md)

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
