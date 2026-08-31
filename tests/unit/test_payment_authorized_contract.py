"""Tests for the payment_authorized event contract."""

import copy
import json
import re
from pathlib import Path
from typing import Any, cast

import pytest

from retailpulse.contracts.loader import load_json_contract
from retailpulse.contracts.validation import (
    ContractValidationError,
    validate_avro_event,
    validate_payment_authorized_business_rules,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_PATH = (
    PROJECT_ROOT / "contracts" / "events" / "payments" / "payment-authorized-v1.avsc"
)

EVENT_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "events" / "valid-payment-authorized.json"
)


@pytest.fixture
def valid_payment_authorized_event() -> dict[str, Any]:
    """Load a valid payment authorized event."""

    content = EVENT_PATH.read_text(encoding="utf-8")
    event: object = json.loads(content)

    if not isinstance(event, dict):
        raise TypeError("The payment event fixture must contain a JSON object.")

    return cast(dict[str, Any], event)


def test_valid_payment_authorized_event(
    valid_payment_authorized_event: dict[str, Any],
) -> None:
    """A valid authorization should satisfy all contract rules."""

    schema = load_json_contract(SCHEMA_PATH)

    validate_avro_event(
        valid_payment_authorized_event,
        schema,
    )
    validate_payment_authorized_business_rules(valid_payment_authorized_event)


def test_payment_authorized_with_zero_amount_is_rejected(
    valid_payment_authorized_event: dict[str, Any],
) -> None:
    """An authorization with a zero amount should be rejected."""

    event = copy.deepcopy(valid_payment_authorized_event)
    event["payload"]["authorized_amount_minor"] = 0

    with pytest.raises(
        ContractValidationError,
        match="must be strictly positive",
    ):
        validate_payment_authorized_business_rules(event)


def test_payment_authorized_with_invalid_expiration_is_rejected(
    valid_payment_authorized_event: dict[str, Any],
) -> None:
    """An authorization must expire after its event time."""

    event = copy.deepcopy(valid_payment_authorized_event)
    event["payload"]["authorization_expires_at"] = event["event_time"]

    with pytest.raises(
        ContractValidationError,
        match="must be later than event_time",
    ):
        validate_payment_authorized_business_rules(event)


def test_payment_authorized_with_wrong_correlation_id_is_rejected(
    valid_payment_authorized_event: dict[str, Any],
) -> None:
    """The correlation identifier should match the order identifier."""

    event = copy.deepcopy(valid_payment_authorized_event)
    event["correlation_id"] = "1f0f394d-b1b7-45a1-a057-bbb28483420c"

    with pytest.raises(
        ContractValidationError,
        match=re.escape("must match payload.order_id"),
    ):
        validate_payment_authorized_business_rules(event)


def test_payment_authorized_without_required_field_is_rejected(
    valid_payment_authorized_event: dict[str, Any],
) -> None:
    """Avro should reject an event missing a required field."""

    schema = load_json_contract(SCHEMA_PATH)
    event = copy.deepcopy(valid_payment_authorized_event)
    del event["payload"]["payment_provider"]

    with pytest.raises(
        ContractValidationError,
        match="does not conform to its Avro contract",
    ):
        validate_avro_event(event, schema)
