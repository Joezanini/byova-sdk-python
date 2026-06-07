"""Internal audio encoding utilities."""

from __future__ import annotations

import struct
from collections.abc import Iterator

from webex_byova.media.exceptions import PromptValidationError

WAV_RIFF_MAGIC = b"RIFF"
WAV_DATA_CHUNK = b"data"

# G.711 μ-law encode/decode tables (pure Python — audioop removed in 3.13)
_BIAS = 0x84
_CLIP = 32635
_EXP_LUT = (
    0,
    0,
    1,
    1,
    2,
    2,
    2,
    2,
    3,
    3,
    3,
    3,
    3,
    3,
    3,
    3,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
)


def _linear_to_mulaw(sample: int) -> int:
    sign = (sample >> 8) & 0x80
    if sign:
        sample = -sample
    if sample > _CLIP:
        sample = _CLIP
    sample += _BIAS
    exponent = _EXP_LUT[(sample >> 7) & 0xFF]
    mantissa = (sample >> (exponent + 3)) & 0x0F
    ulaw = ~(sign | (exponent << 4) | mantissa) & 0xFF
    return ulaw


def _mulaw_to_linear(ulaw: int) -> int:
    ulaw = ~ulaw & 0xFF
    sign = ulaw & 0x80
    exponent = (ulaw >> 4) & 0x07
    mantissa = ulaw & 0x0F
    sample = ((mantissa << 3) + _BIAS) << exponent
    sample -= _BIAS
    return -sample if sign else sample


def strip_wav_header(data: bytes) -> bytes:
    """Remove WAV container header and return raw μ-law payload bytes."""
    if not data.startswith(WAV_RIFF_MAGIC):
        return data

    offset = 12
    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        chunk_size = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
        chunk_start = offset + 8
        if chunk_id == WAV_DATA_CHUNK:
            return data[chunk_start : chunk_start + chunk_size]
        offset = chunk_start + chunk_size
        if chunk_size % 2:
            offset += 1

    raise PromptValidationError("Invalid WAV file: data chunk not found")


def ensure_raw_mulaw(data: bytes, *, audio_mode: str) -> bytes:
    """Return raw μ-law bytes, stripping WAV header in chunked mode."""
    if audio_mode == "chunked" and data.startswith(WAV_RIFF_MAGIC):
        return strip_wav_header(data)
    return data


def chunk_audio(data: bytes, chunk_size: int) -> Iterator[bytes]:
    """Yield fixed-size raw audio segments."""
    if chunk_size <= 0:
        raise PromptValidationError("chunk_size must be positive")
    for start in range(0, len(data), chunk_size):
        yield data[start : start + chunk_size]


def encode_mulaw(linear16: bytes, sample_width: int = 2) -> bytes:
    """Encode 16-bit linear PCM to G.711 μ-law."""
    if sample_width != 2:
        raise PromptValidationError("Only 16-bit linear PCM supported")
    out = bytearray()
    for i in range(0, len(linear16), 2):
        sample = struct.unpack("<h", linear16[i : i + 2])[0]
        out.append(_linear_to_mulaw(sample))
    return bytes(out)


def decode_mulaw(data: bytes, sample_width: int = 2) -> bytes:
    """Decode G.711 μ-law to 16-bit linear PCM."""
    if sample_width != 2:
        raise PromptValidationError("Only 16-bit linear PCM supported")
    out = bytearray()
    for byte in data:
        sample = _mulaw_to_linear(byte)
        out.extend(struct.pack("<h", sample))
    return bytes(out)


def build_mulaw_wav(data: bytes, sample_rate: int = 8000, channels: int = 1) -> bytes:
    """Wrap raw μ-law bytes in a minimal WAV container."""
    byte_rate = sample_rate * channels
    block_align = channels
    bits_per_sample = 8
    fmt_chunk = struct.pack(
        "<HHIIHH",
        7,  # WAVE_FORMAT_MULAW
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
    )
    fact_chunk = struct.pack("<II", 4, len(data))
    data_chunk = struct.pack("<4sI", b"data", len(data))
    riff_size = 4 + 8 + len(fmt_chunk) + 8 + len(fact_chunk) + 8 + len(data)
    header = b"".join(
        [
            b"RIFF",
            struct.pack("<I", riff_size),
            b"WAVE",
            b"fmt ",
            struct.pack("<I", len(fmt_chunk)),
            fmt_chunk,
            b"fact",
            fact_chunk,
            data_chunk,
        ]
    )
    return header + data


def validate_no_riff_in_chunks(chunks: list[bytes]) -> None:
    """Ensure chunked payloads do not contain WAV headers."""
    for chunk in chunks:
        if chunk.startswith(WAV_RIFF_MAGIC):
            raise PromptValidationError("Chunked outbound audio must not contain WAV headers")
