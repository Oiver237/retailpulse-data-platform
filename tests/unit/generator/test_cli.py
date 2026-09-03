"""Tests for the data generator command-line interface."""

from pathlib import Path

from retailpulse.generator.cli import build_parser


def test_cli_uses_eur_by_default() -> None:
    """The CLI should use EUR when no currency is provided."""

    arguments = build_parser().parse_args([])

    assert arguments.currency == "EUR"


def test_cli_accepts_usd_currency() -> None:
    """The CLI should accept an explicit USD currency."""

    arguments = build_parser().parse_args(
        [
            "--currency",
            "USD",
        ]
    )

    assert arguments.currency == "USD"


def test_cli_reads_generation_arguments() -> None:
    """The CLI should read all supported generation arguments."""

    arguments = build_parser().parse_args(
        [
            "--seed",
            "21",
            "--run-id",
            "tiny-usd",
            "--output",
            "data/test-output",
            "--customers",
            "10",
            "--products",
            "20",
            "--orders",
            "30",
            "--currency",
            "USD",
        ]
    )

    assert arguments.seed == 21
    assert arguments.run_id == "tiny-usd"
    assert arguments.output == Path("data/test-output")
    assert arguments.customers == 10
    assert arguments.products == 20
    assert arguments.orders == 30
    assert arguments.currency == "USD"
