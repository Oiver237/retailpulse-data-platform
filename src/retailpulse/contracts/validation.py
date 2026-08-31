"""Structural and business validation for RetailPulse events."""

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from fastavro import parse_schema
from fastavro.validation import validate

Event = Mapping[str, Any]


class ContractValidationError(ValueError):
    """Raised when an event violates its data contract."""


def validate_avro_event(
    event: Event,
    schema: dict[str, Any],
) -> None:
    """Validate an event against an Avro schema."""

    parsed_schema = parse_schema(schema)

    if not validate(dict(event), parsed_schema, raise_errors=False):
        raise ContractValidationError("Event does not conform to its Avro contract.")


def validate_uuid(value: str, field_name: str) -> None:
    """Validate that a field contains a UUID."""

    try:
        UUID(value)
    except ValueError as error:
        raise ContractValidationError(
            f"{field_name} must contain a valid UUID."
        ) from error


def validate_currency(currency: str) -> None:
    """Validate an uppercase three-letter currency code."""

    if len(currency) != 3 or not currency.isalpha() or not currency.isupper():
        raise ContractValidationError("currency must contain three uppercase letters.")


def validate_order_created_business_rules(event: Event) -> None:
    """Validate the business rules of an order_created event."""

    if event.get("event_type") != "order_created":
        raise ContractValidationError("Expected event_type='order_created'.")

    event_id = str(event["event_id"])
    correlation_id = str(event["correlation_id"])
    payload = event["payload"]

    if not isinstance(payload, Mapping):
        raise ContractValidationError("payload must be an object.")

    order_id = str(payload["order_id"])
    currency = str(payload["currency"])
    items = payload["items"]

    validate_uuid(event_id, "event_id")
    validate_uuid(order_id, "payload.order_id")
    validate_uuid(correlation_id, "correlation_id")
    validate_currency(currency)

    if correlation_id != order_id:
        raise ContractValidationError("correlation_id must match payload.order_id.")

    if not isinstance(items, list) or not items:
        raise ContractValidationError("An order must contain at least one item.")

    order_item_ids: set[str] = set()

    for item in items:
        if not isinstance(item, Mapping):
            raise ContractValidationError("Each order item must be an object.")

        order_item_id = str(item["order_item_id"])
        quantity = int(item["quantity"])
        unit_price = int(item["unit_price_amount_minor"])
        item_discount = int(item["discount_amount_minor"])

        validate_uuid(order_item_id, "payload.items.order_item_id")
        validate_uuid(
            str(item["product_id"]),
            "payload.items.product_id",
        )

        if order_item_id in order_item_ids:
            raise ContractValidationError(
                "order_item_id must be unique within an order."
            )

        order_item_ids.add(order_item_id)

        if quantity <= 0:
            raise ContractValidationError("Item quantity must be strictly positive.")

        if unit_price < 0:
            raise ContractValidationError("Item unit price cannot be negative.")

        if item_discount < 0:
            raise ContractValidationError("Item discount cannot be negative.")

        if item_discount > quantity * unit_price:
            raise ContractValidationError(
                "Item discount cannot exceed the gross item amount."
            )

    subtotal = int(payload["subtotal_amount_minor"])
    discount = int(payload["discount_amount_minor"])
    shipping = int(payload["shipping_amount_minor"])
    tax = int(payload["tax_amount_minor"])
    total = int(payload["total_amount_minor"])

    monetary_values = {
        "subtotal_amount_minor": subtotal,
        "discount_amount_minor": discount,
        "shipping_amount_minor": shipping,
        "tax_amount_minor": tax,
        "total_amount_minor": total,
    }

    for field_name, value in monetary_values.items():
        if value < 0:
            raise ContractValidationError(f"{field_name} cannot be negative.")

    expected_total = subtotal - discount + shipping + tax

    if total != expected_total:
        raise ContractValidationError(
            "total_amount_minor does not match the expected total."
        )


def validate_payment_authorized_business_rules(event: Event) -> None:
    """Validate the business rules of a payment_authorized event."""

    if event.get("event_type") != "payment_authorized":
        raise ContractValidationError("Expected event_type='payment_authorized'.")

    if event.get("event_version") != 1:
        raise ContractValidationError("Expected event_version=1.")

    event_id = str(event["event_id"])
    correlation_id = str(event["correlation_id"])
    event_time = int(event["event_time"])
    produced_at = int(event["produced_at"])
    payload = event["payload"]

    validate_uuid(event_id, "event_id")
    validate_uuid(correlation_id, "correlation_id")

    if not isinstance(payload, Mapping):
        raise ContractValidationError("payload must be an object.")

    payment_id = str(payload["payment_id"])
    order_id = str(payload["order_id"])
    attempt_number = int(payload["attempt_number"])
    authorized_amount = int(payload["authorized_amount_minor"])
    currency = str(payload["currency"])
    payment_provider = str(payload["payment_provider"]).strip()
    provider_authorization_id = str(payload["provider_authorization_id"]).strip()
    authorization_expires_at = int(payload["authorization_expires_at"])

    validate_uuid(payment_id, "payload.payment_id")
    validate_uuid(order_id, "payload.order_id")
    validate_currency(currency)

    if correlation_id != order_id:
        raise ContractValidationError("correlation_id must match payload.order_id.")

    if attempt_number < 1:
        raise ContractValidationError(
            "attempt_number must be greater than or equal to 1."
        )

    if authorized_amount <= 0:
        raise ContractValidationError(
            "authorized_amount_minor must be strictly positive."
        )

    if produced_at < event_time:
        raise ContractValidationError("produced_at must not precede event_time.")

    if authorization_expires_at <= event_time:
        raise ContractValidationError(
            "authorization_expires_at must be later than event_time."
        )

    if not payment_provider:
        raise ContractValidationError("payment_provider must not be empty.")

    if not provider_authorization_id:
        raise ContractValidationError("provider_authorization_id must not be empty.")
