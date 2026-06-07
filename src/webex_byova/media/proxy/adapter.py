"""Proxy adapter protocol and default JSON mapping."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from webex_byova.media.events import MediaEvent
from webex_byova.media.prompts import PromptRequest

if TYPE_CHECKING:
    from webex_byova.media.session import MediaSession


@runtime_checkable
class ProxyAdapter(Protocol):
    """Map media events to backend messages and vice versa."""

    def to_backend(self, event: MediaEvent, session: MediaSession) -> str | bytes: ...

    def from_backend(self, message: str | bytes, session: MediaSession) -> PromptRequest | None: ...


class DefaultProxyAdapter:
    """JSON message mapping per websocket-proxy contract."""

    def to_backend(self, event: MediaEvent, session: MediaSession) -> str:
        payload: dict[str, object] = {}
        event_type = event.type
        if event_type == "audio_input":
            from webex_byova.media.events import AudioInputEvent

            assert isinstance(event, AudioInputEvent)
            payload = {
                "encoding": event.encoding,
                "sample_rate": event.sample_rate,
                "channels": 1,
                "data": base64.b64encode(event.audio).decode("ascii"),
                "is_final": event.is_final,
            }
        elif event_type == "dtmf_input":
            from webex_byova.media.events import DtmfInputEvent

            assert isinstance(event, DtmfInputEvent)
            payload = {"digits": event.digits}
        elif event_type == "session_start":
            from webex_byova.media.events import SessionStartEvent

            assert isinstance(event, SessionStartEvent)
            payload = dict(event.metadata)

        turn_id = session.active_turn.turn_id if session.active_turn else ""
        body = {
            "type": event_type,
            "conversation_id": session.conversation_id,
            "turn_id": turn_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "payload": payload,
        }
        return json.dumps(body)

    def from_backend(self, message: str | bytes, session: MediaSession) -> PromptRequest | None:
        _ = session
        text = message.decode() if isinstance(message, bytes) else message
        data = json.loads(text)
        msg_type = data.get("type")
        payload = data.get("payload") or {}
        if msg_type == "prompt":
            audio_b64 = payload.get("audio")
            audio = base64.b64decode(audio_b64) if audio_b64 else None
            return PromptRequest(
                text=payload.get("text"),
                ssml=payload.get("ssml"),
                audio=audio,
            )
        if msg_type == "end_session":
            return None
        return None
