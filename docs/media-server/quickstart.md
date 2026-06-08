# Media Server Quickstart

Run a minimal media server in under 15 minutes.

## 1. Install

```bash
pip install "webex-byova[media]"
```

## 2. Hello world

```python
import asyncio
from webex_byova.media import BYOVAMediaServer, MediaServerConfig

async def main():
    server = BYOVAMediaServer(MediaServerConfig(port=50051, verify_tokens=False))

    @server.on("session_start")
    async def greet(session, turn):
        await turn.play_prompt(text="Hello from webex-byova")

    async with server:
        await server._grpc_server.wait_for_termination()

asyncio.run(main())
```

See also: [`examples/media_server_minimal.py`](https://github.com/Joezanini/byova-sdk-python/blob/main/examples/media_server_minimal.py)

More examples (multi-turn, DTMF, WebSocket proxy, BYODS combined): [Examples guide](../guides/examples.md#media-server-voice).

## 3. Register with Webex

1. Create a Service App with BYODS scopes.
2. Register a data source with schema `5397013b-7920-4ffc-807c-e8a3e0a18f43`.
3. Point the data source URL to your server (`host:port`).

## 4. Validate locally

```bash
pytest tests/media/test_server.py -v
```

## Validation scenarios

| Scenario | Command |
|----------|---------|
| Minimal session | `pytest tests/media/test_server.py::test_minimal_session_flow -v` |
| Multi-turn | `pytest tests/media/test_turn_lifecycle.py -v` |
| Protocol compliance | `pytest tests/media/test_protocol_compliance.py -v` |
| Token verification | `pytest tests/media/test_token_verification.py -v` |
| WebSocket proxy | `pytest tests/media/test_proxy.py -v` |
