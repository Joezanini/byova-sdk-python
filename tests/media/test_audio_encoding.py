"""Audio encoding unit tests."""

import pytest

from webex_byova.media._internal.audio import (
    build_mulaw_wav,
    chunk_audio,
    decode_mulaw,
    encode_mulaw,
    strip_wav_header,
    validate_no_riff_in_chunks,
)
from webex_byova.media.exceptions import PromptValidationError


def test_mulaw_roundtrip() -> None:
    linear = b"\x00\x01" * 80
    encoded = encode_mulaw(linear)
    decoded = decode_mulaw(encoded)
    assert len(encoded) == 80
    assert len(decoded) == 160


def test_strip_wav_header() -> None:
    raw = b"\xff" * 100
    wav = build_mulaw_wav(raw, sample_rate=8000)
    stripped = strip_wav_header(wav)
    assert stripped == raw
    assert not stripped.startswith(b"RIFF")


def test_strip_non_wav_passthrough() -> None:
    raw = b"\xff" * 50
    assert strip_wav_header(raw) == raw


def test_chunk_audio_sizes() -> None:
    data = b"\x00" * 500
    chunks = list(chunk_audio(data, 160))
    assert len(chunks) == 4
    assert sum(len(c) for c in chunks) == 500


def test_validate_no_riff_in_chunks() -> None:
    validate_no_riff_in_chunks([b"\xff" * 10, b"\x00" * 10])
    with pytest.raises(PromptValidationError):
        validate_no_riff_in_chunks([b"RIFFxxxx"])


def test_build_mulaw_wav_has_riff() -> None:
    wav = build_mulaw_wav(b"\xff" * 80, sample_rate=8000)
    assert wav.startswith(b"RIFF")


def test_sample_rate_16k_chunk_size() -> None:
    from webex_byova.media.config import MediaServerConfig

    config = MediaServerConfig(sample_rate=16000, chunk_size_ms=20)
    assert config.chunk_bytes == 320
