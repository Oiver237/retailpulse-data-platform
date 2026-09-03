"""Tests for the deterministic data generator."""

from pathlib import Path

from retailpulse.contracts.loader import load_json_contract
from retailpulse.contracts.validation import (
    validate_avro_event,
    validate_order_created_business_rules,
    validate_payment_authorized_business_rules,
)
from retailpulse.generator.config import GenerationConfig
from retailpulse.generator.service import DataGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_ROOT = PROJECT_ROOT / "contracts" / "events"


def test_generator_produces_expected_counts() -> None:
    """The generator should respect configured entity counts."""

    config = GenerationConfig(
        customer_count=10,
        category_count=3,
        product_count=8,
        order_count=20,
    )

    dataset = DataGenerator(config).generate()

    assert len(dataset.customers) == 10
    assert len(dataset.categories) == 3
    assert len(dataset.products) == 8
    assert len(dataset.orders) == 20
    assert len(dataset.payments) == 20
    assert len(dataset.order_events) == 20
    assert len(dataset.payment_events) == 20
    assert len(dataset.order_items) >= 20


def test_all_orders_reference_existing_customers() -> None:
    """Every generated order should reference a customer."""

    dataset = DataGenerator(
        GenerationConfig(
            customer_count=10,
            product_count=10,
            order_count=25,
        )
    ).generate()

    customer_ids = {customer.customer_id for customer in dataset.customers}

    assert all(order.customer_id in customer_ids for order in dataset.orders)


def test_all_order_items_reference_existing_entities() -> None:
    """Order items should reference existing orders and products."""

    dataset = DataGenerator(
        GenerationConfig(
            customer_count=10,
            product_count=10,
            order_count=25,
        )
    ).generate()

    order_ids = {order.order_id for order in dataset.orders}
    product_ids = {product.product_id for product in dataset.products}

    assert all(item.order_id in order_ids for item in dataset.order_items)
    assert all(item.product_id in product_ids for item in dataset.order_items)


def test_generation_is_deterministic() -> None:
    """The same configuration should generate the same records."""

    config = GenerationConfig(
        customer_count=5,
        product_count=5,
        order_count=10,
    )

    first = DataGenerator(config).generate()
    second = DataGenerator(config).generate()

    assert first.customers == second.customers
    assert first.products == second.products
    assert first.orders == second.orders
    assert first.payments == second.payments
    assert first.order_events == second.order_events
    assert first.payment_events == second.payment_events


def test_generated_order_events_respect_contracts() -> None:
    """Generated order events should satisfy their contract."""

    schema = load_json_contract(SCHEMA_ROOT / "orders" / "order-created-v1.avsc")

    dataset = DataGenerator(
        GenerationConfig(
            customer_count=5,
            product_count=5,
            order_count=10,
        )
    ).generate()

    for event in dataset.order_events:
        validate_avro_event(event, schema)
        validate_order_created_business_rules(event)


def test_generated_payment_events_respect_contracts() -> None:
    """Generated payment events should satisfy their contract."""

    schema = load_json_contract(SCHEMA_ROOT / "payments" / "payment-authorized-v1.avsc")

    dataset = DataGenerator(
        GenerationConfig(
            customer_count=5,
            product_count=5,
            order_count=10,
        )
    ).generate()

    for event in dataset.payment_events:
        validate_avro_event(event, schema)
        validate_payment_authorized_business_rules(event)


def test_generated_products_use_configured_currency() -> None:
    """Products should use the configured currency."""

    config = GenerationConfig(
        currency="USD",
        customer_count=5,
        category_count=2,
        product_count=10,
        order_count=10,
    )

    dataset = DataGenerator(config).generate()

    assert dataset.products
    assert all(product.currency == "USD" for product in dataset.products)


def test_usd_events_respect_avro_and_business_contracts() -> None:
    """USD events should continue to satisfy their contracts."""

    order_schema = load_json_contract(SCHEMA_ROOT / "orders" / "order-created-v1.avsc")
    payment_schema = load_json_contract(
        SCHEMA_ROOT / "payments" / "payment-authorized-v1.avsc"
    )

    config = GenerationConfig(
        currency="USD",
        customer_count=5,
        category_count=2,
        product_count=10,
        order_count=10,
    )
    dataset = DataGenerator(config).generate()

    for event in dataset.order_events:
        validate_avro_event(event, order_schema)
        validate_order_created_business_rules(event)

    for event in dataset.payment_events:
        validate_avro_event(event, payment_schema)
        validate_payment_authorized_business_rules(event)
