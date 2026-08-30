"""Unit tests for RetailPulse settings."""

import pytest

from retailpulse.config import Environment, Settings


def test_settings_use_local_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings should use safe local defaults."""

    monkeypatch.delenv("RETAILPULSE_ENV", raising=False)
    monkeypatch.delenv("RETAILPULSE_LOG_LEVEL", raising=False)

    settings = Settings.from_environment()

    assert settings.environment is Environment.LOCAL
    assert settings.log_level == "INFO"
    assert settings.project_name == "retailpulse"


def test_settings_read_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings should load supported environment variables."""

    monkeypatch.setenv("RETAILPULSE_ENV", "dev")
    monkeypatch.setenv("RETAILPULSE_LOG_LEVEL", "debug")

    settings = Settings.from_environment()

    assert settings.environment is Environment.DEV
    assert settings.log_level == "DEBUG"


def test_settings_reject_unknown_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings should reject an unsupported environment."""

    monkeypatch.setenv("RETAILPULSE_ENV", "sandbox")

    with pytest.raises(ValueError, match="Unsupported RETAILPULSE_ENV"):
        Settings.from_environment()


def test_settings_reject_unknown_log_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Settings should reject an unsupported log level."""

    monkeypatch.setenv("RETAILPULSE_LOG_LEVEL", "verbose")

    with pytest.raises(ValueError, match="Unsupported RETAILPULSE_LOG_LEVEL"):
        Settings.from_environment()
