"""Tests for generation configuration."""

from datetime import datetime

import pytest

from retailpulse.generator.config import GenerationConfig


def test_tiny_configuration_has_expected_defaults() -> None:
    """Tiny generation should expose safe local defaults."""

    config = GenerationConfig()

    assert config.seed == 42
    assert config.customer_count == 100
    assert config.product_count == 50
    assert config.order_count == 500
    assert config.currency == "EUR"
    assert config.start_time.tzinfo is not None


def test_configuration_rejects_zero_orders() -> None:
    """A generation run must contain at least one order."""

    with pytest.raises(
        ValueError,
        match="order_count must be strictly positive",
    ):
        GenerationConfig(order_count=0)


def test_configuration_rejects_naive_timestamp() -> None:
    """Generation timestamps must include a timezone."""

    with pytest.raises(
        ValueError,
        match="start_time must be timezone-aware",
    ):
        GenerationConfig(start_time=datetime(2026, 1, 1))


def test_configuration_rejects_empty_run_id() -> None:
    """A generation run must have a non-empty identifier."""

    with pytest.raises(
        ValueError,
        match="run_id must not be empty",
    ):
        GenerationConfig(run_id="   ")


def test_configuration_rejects_invalid_currency() -> None:
    """Currency must use three uppercase letters."""

    with pytest.raises(
        ValueError,
        match="currency must contain three uppercase letters",
    ):
        GenerationConfig(currency="eur")


def test_configuration_accepts_usd_currency() -> None:
    """USD should be accepted as a generation currency."""

    config = GenerationConfig(currency="USD")

    assert config.currency == "USD"


def test_configuration_rejects_lowercase_currency() -> None:
    """A lowercase currency code should be rejected."""

    with pytest.raises(
        ValueError,
        match="currency must contain three uppercase letters",
    ):
        GenerationConfig(currency="eur")
