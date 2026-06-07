# BYOVA Protocol Notes

These notes document internal protocol behavior for operators troubleshooting call audio issues. Application code never needs to implement these — the SDK handles them automatically.

## Turn closure (PC-001)

Every bot turn MUST end with `RESPONSE_FINAL` followed immediately by stream close. The SDK sends this automatically when `play_prompt()` completes or `end_turn()` is called.

## Barge-in (PC-002)

When `barge_in_enabled=True`, caller speech during playback cancels remaining prompt chunks and emits a `barge_in` handler event.

## Input events (PC-003)

The SDK sends `START_OF_INPUT` and `END_OF_INPUT` platform events on the gRPC response stream during caller utterances.

## Audio format (PC-004 / PC-005)

| Mode | Wire format |
|------|-------------|
| `chunked` (default) | Raw 8-bit μ-law bytes, no WAV header |
| `full` | Complete WAV container with μ-law payload |

WAV files passed to `play_prompt()` are automatically stripped in chunked mode.

## Sample rate (PC-006)

Supported rates: **8000 Hz** (default) and **16000 Hz**. Set via `MediaServerConfig.sample_rate`.

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| Silent audio after bot response | Turn not closed with `RESPONSE_FINAL` — upgrade SDK; check logs |
| Garbled audio | WAV header sent in chunked mode — use raw μ-law or let SDK strip |
| Overlapping prompts | Barge-in disabled — set `barge_in_enabled=True` |
| Wrong pitch/speed | Sample rate mismatch — align `sample_rate` with audio source |
