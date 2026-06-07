"""BYOVA protocol adapter helpers (internal)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from webex_byova.media.config import MediaServerConfig

from webex_byova.media._internal.generated import byova_common_pb2, voicevirtualagent_pb2


def build_input_handling_config(config: MediaServerConfig) -> byova_common_pb2.InputHandlingConfig:
    """Build default input handling configuration for outbound responses."""
    timeout_ms = int(config.no_input_timeout * 1000)
    speech = byova_common_pb2.InputSpeechTimers(
        max_speech_timeout_msec=30000,
        complete_timeout_msec=config.end_of_input_silence_ms,
        incomplete_timeout_msec=config.end_of_input_silence_ms,
        no_input_timeout_msec=timeout_ms,
    )
    dtmf = byova_common_pb2.DTMFInputConfig(
        inter_digit_timeout_msec=3000,
        termchar=byova_common_pb2.DTMF_DIGIT_POUND,
        dtmf_input_length=20,
    )
    return byova_common_pb2.InputHandlingConfig(dtmf_config=dtmf, speech_timers=speech)


def map_input_mode(config: MediaServerConfig) -> voicevirtualagent_pb2.VoiceVAInputMode:
    """Map public input mode to proto enum."""
    mapping = {
        "voice": voicevirtualagent_pb2.INPUT_VOICE,
        "dtmf": voicevirtualagent_pb2.INPUT_EVENT_DTMF,
        "mixed": voicevirtualagent_pb2.INPUT_VOICE_DTMF,
    }
    return mapping[config.input_mode]


def build_output_event(
    event_type: byova_common_pb2.OutputEvent.EventType,
) -> voicevirtualagent_pb2.VoiceVAResponse:
    """Build a response carrying a single output event."""
    event = byova_common_pb2.OutputEvent(event_type=event_type)
    return voicevirtualagent_pb2.VoiceVAResponse(output_events=[event])


def build_start_of_input() -> voicevirtualagent_pb2.VoiceVAResponse:
    """Build START_OF_INPUT platform event."""
    return build_output_event(byova_common_pb2.OutputEvent.START_OF_INPUT)


def build_end_of_input() -> voicevirtualagent_pb2.VoiceVAResponse:
    """Build END_OF_INPUT platform event."""
    return build_output_event(byova_common_pb2.OutputEvent.END_OF_INPUT)


def build_no_input_event() -> voicevirtualagent_pb2.VoiceVAResponse:
    """Build NO_INPUT platform event."""
    return build_output_event(byova_common_pb2.OutputEvent.NO_INPUT)


def build_audio_chunk_response(
    audio: bytes,
    *,
    config: MediaServerConfig,
    is_final_chunk: bool,
    barge_in: bool,
    text: str | None = None,
) -> voicevirtualagent_pb2.VoiceVAResponse:
    """Build an outbound audio chunk response."""
    prompt = voicevirtualagent_pb2.Prompt(
        text=text or "",
        audio_content=audio,
        is_barge_in_enabled=barge_in,
    )
    response_type = (
        voicevirtualagent_pb2.VoiceVAResponse.FINAL
        if is_final_chunk
        else voicevirtualagent_pb2.VoiceVAResponse.CHUNK
    )
    return voicevirtualagent_pb2.VoiceVAResponse(
        prompts=[prompt],
        response_type=response_type,
        input_mode=map_input_mode(config),
        input_handling_config=build_input_handling_config(config),
    )


def build_response_final(config: MediaServerConfig) -> voicevirtualagent_pb2.VoiceVAResponse:
    """Build RESPONSE_FINAL turn closure message."""
    return voicevirtualagent_pb2.VoiceVAResponse(
        response_type=voicevirtualagent_pb2.VoiceVAResponse.FINAL,
        input_mode=map_input_mode(config),
        input_handling_config=build_input_handling_config(config),
    )


async def close_turn(
    send_response: Any,
    *,
    config: MediaServerConfig,
) -> None:
    """Send RESPONSE_FINAL per BYOVA turn closure contract (PC-001)."""
    await send_response(build_response_final(config))
