# Configuration Reference

## MediaServerConfig

```python
from webex_byova.media import MediaServerConfig

config = MediaServerConfig(
    host="0.0.0.0",
    port=50051,
    audio_mode="chunked",       # "chunked" | "full"
    sample_rate=8000,             # 8000 | 16000
    barge_in_enabled=False,
    input_mode="voice",           # "voice" | "dtmf" | "mixed"
    verify_tokens=True,
    no_input_timeout=5.0,
)
```

## Environment variables

Load from environment with `MediaServerConfig.from_env()` or `BYOVAMediaServer.from_env()`.

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBEX_MEDIA_HOST` | `0.0.0.0` | Bind address |
| `WEBEX_MEDIA_PORT` | `50051` | Listen port |
| `WEBEX_MEDIA_AUDIO_MODE` | `chunked` | Audio wire format |
| `WEBEX_MEDIA_SAMPLE_RATE` | `8000` | Telephony sample rate |
| `WEBEX_MEDIA_BARGE_IN_ENABLED` | `false` | Enable barge-in |
| `WEBEX_MEDIA_INPUT_MODE` | `voice` | Input collection mode |
| `WEBEX_MEDIA_VERIFY_TOKENS` | `true` | JWS verification |
| `WEBEX_MEDIA_NO_INPUT_TIMEOUT` | `5.0` | No-input seconds |
| `WEBEX_MEDIA_TLS_CERT` | — | TLS certificate path |
| `WEBEX_MEDIA_TLS_KEY` | — | TLS private key path |

See `MediaServerConfig` docstrings for the full field list.
