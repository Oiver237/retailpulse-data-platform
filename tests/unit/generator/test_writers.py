"""Tests for generated dataset writers."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest

from retailpulse.generator.config import GenerationConfig
from retailpulse.generator.service import DataGenerator
from retailpulse.generator.writers import (
    json_serializer,
    write_dataset,
    write_json_lines,
)


def load_json_object(path: Path) -> dict[str, Any]:
    """Load and validate a JSON object from disk."""

    content: object = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(content, dict):
        raise TypeError(f"Expected a JSON object in {path}.")

    return cast(dict[str, Any], content)


def test_json_serializer_converts_datetime() -> None:
    """The JSON serializer should convert datetimes to ISO 8601."""

    timestamp = datetime(
        2026,
        1,
        1,
        12,
        30,
        tzinfo=UTC,
    )

    result = json_serializer(timestamp)

    assert result == "2026-01-01T12:30:00+00:00"


def test_json_serializer_rejects_unsupported_value() -> None:
    """The JSON serializer should reject unsupported objects."""

    with pytest.raises(
        TypeError,
        match="is not JSON serializable",
    ):
        json_serializer(object())


def test_write_json_lines_writes_all_records(
    tmp_path: Path,
) -> None:
    """The JSON Lines writer should write one line per record."""

    output_path = tmp_path / "records.jsonl"
    records = [
        {
            "id": "first",
            "created_at": datetime(
                2026,
                1,
                1,
                tzinfo=UTC,
            ),
        },
        {
            "id": "second",
            "created_at": datetime(
                2026,
                1,
                2,
                tzinfo=UTC,
            ),
        },
    ]

    count = write_json_lines(output_path, records)

    lines = output_path.read_text(encoding="utf-8").splitlines()

    assert count == 2
    assert len(lines) == 2

    first_record = json.loads(lines[0])
    second_record = json.loads(lines[1])

    assert first_record["id"] == "first"
    assert second_record["id"] == "second"
    assert first_record["created_at"] == ("2026-01-01T00:00:00+00:00")


def test_write_json_lines_creates_parent_directories(
    tmp_path: Path,
) -> None:
    """The writer should create missing parent directories."""

    output_path = tmp_path / "nested" / "directory" / "records.jsonl"

    count = write_json_lines(
        output_path,
        [{"id": "record-1"}],
    )

    assert count == 1
    assert output_path.is_file()


def test_write_json_lines_supports_empty_collection(
    tmp_path: Path,
) -> None:
    """An empty collection should produce an empty file."""

    output_path = tmp_path / "empty.jsonl"

    count = write_json_lines(output_path, [])

    assert count == 0
    assert output_path.is_file()
    assert output_path.read_text(encoding="utf-8") == ""


def test_write_dataset_creates_expected_files(
    tmp_path: Path,
) -> None:
    """A complete dataset should create every expected file."""

    config = GenerationConfig(
        seed=42,
        run_id="writer-test",
        customer_count=3,
        category_count=2,
        product_count=4,
        order_count=5,
    )
    dataset = DataGenerator(config).generate()

    manifest_path = write_dataset(
        dataset,
        config,
        tmp_path,
    )

    output_directory = tmp_path / "writer-test"

    expected_files = {
        "customers.jsonl",
        "categories.jsonl",
        "products.jsonl",
        "orders.jsonl",
        "order_items.jsonl",
        "payments.jsonl",
        "order_events.jsonl",
        "payment_events.jsonl",
        "manifest.json",
    }

    actual_files = {path.name for path in output_directory.iterdir() if path.is_file()}

    assert manifest_path == output_directory / "manifest.json"
    assert manifest_path.is_file()
    assert actual_files == expected_files


def test_write_dataset_manifest_contains_correct_counts(
    tmp_path: Path,
) -> None:
    """The manifest should contain the generated record counts."""

    config = GenerationConfig(
        seed=42,
        run_id="manifest-test",
        customer_count=3,
        category_count=2,
        product_count=4,
        order_count=5,
    )
    dataset = DataGenerator(config).generate()

    manifest_path = write_dataset(
        dataset,
        config,
        tmp_path,
    )
    manifest = load_json_object(manifest_path)
    counts = cast(dict[str, int], manifest["counts"])

    assert manifest["run_id"] == "manifest-test"
    assert manifest["seed"] == 42
    assert manifest["profile"] == "tiny"
    assert counts["customers"] == 3
    assert counts["categories"] == 2
    assert counts["products"] == 4
    assert counts["orders"] == 5
    assert counts["payments"] == 5
    assert counts["order_events"] == 5
    assert counts["payment_events"] == 5
    assert counts["order_items"] == len(dataset.order_items)


def test_written_order_events_are_valid_json_lines(
    tmp_path: Path,
) -> None:
    """Every written order event should be valid JSON."""

    config = GenerationConfig(
        run_id="event-writer-test",
        customer_count=2,
        category_count=2,
        product_count=3,
        order_count=4,
    )
    dataset = DataGenerator(config).generate()

    write_dataset(dataset, config, tmp_path)

    events_path = tmp_path / config.run_id / "order_events.jsonl"
    lines = events_path.read_text(encoding="utf-8").splitlines()

    events = [json.loads(line) for line in lines]

    assert len(events) == 4
    assert all(event["event_type"] == "order_created" for event in events)


def test_write_dataset_manifest_contains_currency(
    tmp_path: Path,
) -> None:
    """The manifest should expose the configured currency."""

    config = GenerationConfig(
        seed=42,
        run_id="manifest-usd-test",
        currency="USD",
        customer_count=3,
        category_count=2,
        product_count=4,
        order_count=5,
    )
    dataset = DataGenerator(config).generate()

    manifest_path = write_dataset(
        dataset,
        config,
        tmp_path,
    )
    manifest = load_json_object(manifest_path)

    assert manifest["run_id"] == "manifest-usd-test"
    assert manifest["currency"] == "USD"
