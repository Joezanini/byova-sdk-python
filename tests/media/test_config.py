"""Configuration validation tests."""

import pytest

from webex_byova.media.config import MediaServerConfig
from webex_byova.media.exceptions import MediaConfigError


def test_default_config() -> None:
    config = MediaServerConfig()
    assert config.port == 50051
    assert config.sample_rate == 8000
    assert config.verify_tokens is True


def test_sample_rate_validation() -> None:
    config = MediaServerConfig(sample_rate=16000)
    assert config.sample_rate == 16000


def test_invalid_sample_rate() -> None:
    with pytest.raises(Exception):
        MediaServerConfig(sample_rate=44100)  # type: ignore[arg-type]


def test_tls_pair_validation() -> None:
    with pytest.raises(MediaConfigError):
        MediaServerConfig(tls_cert="/tmp/cert.pem")


def test_chunk_bytes_8k_20ms() -> None:
    config = MediaServerConfig(sample_rate=8000, chunk_size_ms=20)
    assert config.chunk_bytes == 160


def test_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEBEX_MEDIA_PORT", "50100")
    monkeypatch.setenv("WEBEX_MEDIA_BARGE_IN_ENABLED", "true")
    monkeypatch.setenv("WEBEX_MEDIA_SAMPLE_RATE", "16000")
    config = MediaServerConfig.from_env()
    assert config.port == 50100
    assert config.barge_in_enabled is True
    assert config.sample_rate == 16000


def test_from_env_verify_tokens_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEBEX_MEDIA_VERIFY_TOKENS", "false")
    config = MediaServerConfig.from_env()
    assert config.verify_tokens is False


def test_max_session_duration_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEBEX_MEDIA_MAX_SESSION_DURATION", "none")
    config = MediaServerConfig.from_env()
    assert config.max_session_duration is None
