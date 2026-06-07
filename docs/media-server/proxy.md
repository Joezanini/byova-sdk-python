# WebSocket Proxy

Bridge Webex sessions to external voice AI backends without custom protocol glue.

```python
from webex_byova.media import BYOVAMediaServer, WebSocketProxyConnector, DefaultProxyAdapter

server = BYOVAMediaServer()
server.use_proxy(WebSocketProxyConnector(
    url="wss://your-backend.example/ws",
    adapter=DefaultProxyAdapter(),
))
```

## Default JSON protocol

**SDK → backend**: `{ "type": "session_start|audio|dtmf|...", "conversation_id", "turn_id", "payload" }`

**Backend → SDK**: `{ "type": "prompt|end_session", "payload": { "text", "audio" (base64) } }`

## Custom adapters

Implement `ProxyAdapter` with `to_backend()` and `from_backend()` methods. See `contracts/websocket-proxy.md` in the feature spec.

## Buffer overflow

Default policy disconnects the session when the proxy buffer exceeds `proxy_buffer_limit`. Set `proxy_overflow_policy="drop_oldest"` to drop oldest chunks instead.
