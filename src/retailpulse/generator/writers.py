"""Output writers for generated datasets."""

import json
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from retailpulse.generator.config import GenerationConfig
from retailpulse.generator.models import GeneratedDataset


def json_serializer(value: object) -> str:
    """Serialize supported non-JSON-native values."""

    if isinstance(value, datetime):
        return value.isoformat()

    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable.")


def write_json_lines(
    path: Path,
    records: Iterable[Mapping[str, Any]],
) -> int:
    """Write records to a JSON Lines file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with path.open("w", encoding="utf-8") as output:
        for record in records:
            line = json.dumps(
                dict(record),
                default=json_serializer,
                ensure_ascii=False,
                sort_keys=True,
            )
            output.write(f"{line}\n")
            count += 1

    return count


def write_dataset(
    dataset: GeneratedDataset,
    config: GenerationConfig,
    root_directory: Path,
) -> Path:
    """Write a generated dataset and return its manifest path."""

    output_directory = root_directory / config.run_id
    output_directory.mkdir(parents=True, exist_ok=True)

    counts = {
        "customers": write_json_lines(
            output_directory / "customers.jsonl",
            (item.to_record() for item in dataset.customers),
        ),
        "categories": write_json_lines(
            output_directory / "categories.jsonl",
            (item.to_record() for item in dataset.categories),
        ),
        "products": write_json_lines(
            output_directory / "products.jsonl",
            (item.to_record() for item in dataset.products),
        ),
        "orders": write_json_lines(
            output_directory / "orders.jsonl",
            (item.to_record() for item in dataset.orders),
        ),
        "order_items": write_json_lines(
            output_directory / "order_items.jsonl",
            (item.to_record() for item in dataset.order_items),
        ),
        "payments": write_json_lines(
            output_directory / "payments.jsonl",
            (item.to_record() for item in dataset.payments),
        ),
        "order_events": write_json_lines(
            output_directory / "order_events.jsonl",
            dataset.order_events,
        ),
        "payment_events": write_json_lines(
            output_directory / "payment_events.jsonl",
            dataset.payment_events,
        ),
    }

    manifest = {
        "run_id": config.run_id,
        "seed": config.seed,
        "profile": "tiny",
        "generated_at": config.start_time.isoformat(),
        "counts": counts,
    }

    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return manifest_path
