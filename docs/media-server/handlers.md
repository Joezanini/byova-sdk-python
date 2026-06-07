# Handler Reference

Register handlers with `@server.on("event")` or `@server.handler("event")`.

## Supported events

| Event | Handler signature | Description |
|-------|-------------------|-------------|
| `session_start` | `(session, turn)` | New call session |
| `turn_started` | `(event, session, turn)` | Turn stream opened |
| `audio_input` | `(event, session, turn)` | Caller audio chunk |
| `dtmf_input` | `(event, session, turn)` | DTMF digits |
| `barge_in` | `(event, session, turn)` | Caller interrupted playback |
| `no_input` | `(event, session, turn)` | Input timeout |
| `turn_ended` | `(event, session, turn)` | Turn closed |
| `session_end` | `(event, session, turn)` | Session terminated |
| `error` | `(event, session, turn)` | Handler or server error |

Sync handlers are supported via `asyncio.to_thread`.

## TurnContext methods

- `await turn.play_prompt(text=, audio=, ssml=, barge_in=)`
- `await turn.collect_input(mode=, timeout=)`
- `await turn.end_turn()`

## MediaSession methods

- `await session.play_prompt(...)` — delegates to active turn
- `await session.collect_input(...)`
- `await session.end_session(reason=)`
