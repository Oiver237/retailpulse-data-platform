"""Tests for event contract validation."""

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest

from retailpulse.contracts.loader import load_json_contract
from retailpulse.contracts.validation import (
    ContractValidationError,
    validate_avro_event,
    validate_order_created_business_rules,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "contracts" / "events" / "orders" / "order-created-v1.avsc"
EVENT_PATH = PROJECT_ROOT / "tests" / "fixtures" / "events" / "valid-order-created.json"


@pytest.fixture
def valid_order_event() -> dict[str, Any]:
    """Load a valid order event fixture."""

    content = EVENT_PATH.read_text(encoding="utf-8")
    return cast(dict[str, Any], json.loads(content))


def test_valid_order_matches_avro_schema(
    valid_order_event: dict[str, Any],
) -> None:
    """A valid event should conform to the Avro schema."""

    schema = load_json_contract(SCHEMA_PATH)

    validate_avro_event(valid_order_event, schema)


def test_valid_order_matches_business_rules(
    valid_order_event: dict[str, Any],
) -> None:
    """A valid event should pass business validation."""

    validate_order_created_business_rules(valid_order_event)


def test_order_with_invalid_total_is_rejected(
    valid_order_event: dict[str, Any],
) -> None:
    """An inconsistent order total should be rejected."""

    event = copy.deepcopy(valid_order_event)
    event["payload"]["total_amount_minor"] = 999999

    with pytest.raises(
        ContractValidationError,
        match="does not match the expected total",
    ):
        validate_order_created_business_rules(event)


def test_order_without_items_is_rejected(
    valid_order_event: dict[str, Any],
) -> None:
    """An order without items should be rejected."""

    event = copy.deepcopy(valid_order_event)
    event["payload"]["items"] = []

    with pytest.raises(
        ContractValidationError,
        match="at least one item",
    ):
        validate_order_created_business_rules(event)


def test_order_with_invalid_currency_is_rejected(
    valid_order_event: dict[str, Any],
) -> None:
    """A lowercase currency should be rejected."""

    event = copy.deepcopy(valid_order_event)
    event["payload"]["currency"] = "eur"

    with pytest.raises(
        ContractValidationError,
        match="three uppercase letters",
    ):
        validate_order_created_business_rules(event)


def test_order_with_duplicate_items_is_rejected(
    valid_order_event: dict[str, Any],
) -> None:
    """Duplicate order item identifiers should be rejected."""

    event = copy.deepcopy(valid_order_event)
    event["payload"]["items"].append(copy.deepcopy(event["payload"]["items"][0]))

    with pytest.raises(
        ContractValidationError,
        match="unique within an order",
    ):
        validate_order_created_business_rules(event)
