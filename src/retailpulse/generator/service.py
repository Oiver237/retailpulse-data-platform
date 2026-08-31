"""Deterministic synthetic data generation service."""

import random
from datetime import timedelta
from typing import Any

from faker import Faker

from retailpulse.generator.config import GenerationConfig
from retailpulse.generator.identifiers import deterministic_uuid
from retailpulse.generator.models import (
    Category,
    Customer,
    GeneratedDataset,
    Order,
    OrderItem,
    Payment,
    Product,
)
from retailpulse.generator.time import (
    timestamp_from_index,
    to_epoch_millis,
)

CHANNELS = ("web", "mobile", "marketplace", "store")
PAYMENT_METHODS = ("card", "wallet", "bank_transfer", "gift_card")
PAYMENT_PROVIDERS = ("synthetic-pay", "demo-wallet", "test-bank")

CATEGORY_NAMES = (
    "computers",
    "mobile-accessories",
    "audio",
    "networking",
    "office",
    "gaming",
    "storage",
    "smart-home",
)


class DataGenerator:
    """Generate coherent RetailPulse datasets."""

    def __init__(self, config: GenerationConfig) -> None:
        """Initialize deterministic random generators."""
        self.config = config
        self.random = random.Random(config.seed)
        self.fake = Faker("fr_FR")
        self.fake.seed_instance(config.seed)

    def generate(self) -> GeneratedDataset:
        """Generate a complete coherent dataset."""
        categories = self._generate_categories()
        customers = self._generate_customers()
        products = self._generate_products(categories)

        orders: list[Order] = []
        order_items: list[OrderItem] = []
        payments: list[Payment] = []
        order_events: list[dict[str, Any]] = []
        payment_events: list[dict[str, Any]] = []

        for order_index in range(self.config.order_count):
            order, items = self._generate_order(
                order_index,
                customers,
                products,
            )
            payment = self._generate_payment(order_index, order)

            orders.append(order)
            order_items.extend(items)
            payments.append(payment)
            order_events.append(self._build_order_created_event(order, items))
            payment_events.append(self._build_payment_authorized_event(payment, order))

        return GeneratedDataset(
            customers=customers,
            categories=categories,
            products=products,
            orders=orders,
            order_items=order_items,
            payments=payments,
            order_events=order_events,
            payment_events=payment_events,
        )

    def _generate_categories(self) -> list[Category]:
        """Generate product categories."""
        return [
            Category(
                category_id=str(
                    deterministic_uuid(
                        "category",
                        str(index),
                        self.config.seed,
                    )
                ),
                category_name=CATEGORY_NAMES[index % len(CATEGORY_NAMES)],
            )
            for index in range(self.config.category_count)
        ]

    def _generate_customers(self) -> list[Customer]:
        """Generate synthetic customers."""
        customers: list[Customer] = []

        for index in range(self.config.customer_count):
            created_at = timestamp_from_index(
                self.config.start_time,
                index,
                interval_seconds=300,
            )

            customers.append(
                Customer(
                    customer_id=str(
                        deterministic_uuid(
                            "customer",
                            str(index),
                            self.config.seed,
                        )
                    ),
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    email=f"customer-{index}@example.test",
                    country_code="FR",
                    created_at=created_at,
                )
            )

        return customers

    def _generate_products(
        self,
        categories: list[Category],
    ) -> list[Product]:
        """Generate synthetic products linked to categories."""
        products: list[Product] = []

        for index in range(self.config.product_count):
            category = categories[index % len(categories)]
            price_minor = self.random.randint(500, 200_000)

            products.append(
                Product(
                    product_id=str(
                        deterministic_uuid(
                            "product",
                            str(index),
                            self.config.seed,
                        )
                    ),
                    category_id=category.category_id,
                    product_name=f"Product {index + 1:04d}",
                    unit_price_amount_minor=price_minor,
                    currency=self.config.currency,
                    active=True,
                    created_at=timestamp_from_index(
                        self.config.start_time,
                        index,
                        interval_seconds=600,
                    ),
                )
            )

        return products

    def _generate_order(
        self,
        order_index: int,
        customers: list[Customer],
        products: list[Product],
    ) -> tuple[Order, list[OrderItem]]:
        """Generate an order and its product lines."""
        order_id = str(
            deterministic_uuid(
                "order",
                str(order_index),
                self.config.seed,
            )
        )
        customer = self.random.choice(customers)
        item_count = self.random.randint(1, 5)
        selected_products = self.random.sample(
            products,
            k=min(item_count, len(products)),
        )

        items: list[OrderItem] = []
        subtotal = 0

        for item_index, product in enumerate(selected_products):
            quantity = self.random.randint(1, 3)
            gross_amount = quantity * product.unit_price_amount_minor
            item_discount = 0
            subtotal += gross_amount

            items.append(
                OrderItem(
                    order_item_id=str(
                        deterministic_uuid(
                            "order-item",
                            f"{order_index}-{item_index}",
                            self.config.seed,
                        )
                    ),
                    order_id=order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price_amount_minor=(product.unit_price_amount_minor),
                    discount_amount_minor=item_discount,
                )
            )

        discount = 0
        shipping = 0 if subtotal >= 5_000 else 499
        tax = subtotal * 20 // 100
        total = subtotal - discount + shipping + tax

        created_at = timestamp_from_index(
            self.config.start_time,
            order_index,
            interval_seconds=120,
        )

        order = Order(
            order_id=order_id,
            customer_id=customer.customer_id,
            channel=self.random.choice(CHANNELS),
            status="CONFIRMED",
            currency=self.config.currency,
            subtotal_amount_minor=subtotal,
            discount_amount_minor=discount,
            shipping_amount_minor=shipping,
            tax_amount_minor=tax,
            total_amount_minor=total,
            created_at=created_at,
            updated_at=created_at + timedelta(seconds=10),
        )

        return order, items

    def _generate_payment(
        self,
        order_index: int,
        order: Order,
    ) -> Payment:
        """Generate one successful payment per order."""
        created_at = order.created_at + timedelta(seconds=2)
        updated_at = order.created_at + timedelta(seconds=8)

        return Payment(
            payment_id=str(
                deterministic_uuid(
                    "payment",
                    str(order_index),
                    self.config.seed,
                )
            ),
            order_id=order.order_id,
            attempt_number=1,
            status="AUTHORIZED",
            amount_minor=order.total_amount_minor,
            currency=order.currency,
            payment_method=self.random.choice(PAYMENT_METHODS),
            payment_provider=self.random.choice(PAYMENT_PROVIDERS),
            provider_transaction_id=(f"transaction-{self.config.seed}-{order_index}"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _build_order_created_event(
        self,
        order: Order,
        items: list[OrderItem],
    ) -> dict[str, Any]:
        """Build an order_created event."""
        event_time = order.created_at

        return {
            "event_id": str(
                deterministic_uuid(
                    "order-created-event",
                    order.order_id,
                    self.config.seed,
                )
            ),
            "event_type": "order_created",
            "event_version": 1,
            "event_time": to_epoch_millis(event_time),
            "produced_at": to_epoch_millis(event_time + timedelta(seconds=1)),
            "producer": "data-generator",
            "correlation_id": order.order_id,
            "trace_id": str(
                deterministic_uuid(
                    "trace",
                    order.order_id,
                    self.config.seed,
                )
            ),
            "payload": {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "session_id": None,
                "channel": order.channel,
                "currency": order.currency,
                "subtotal_amount_minor": (order.subtotal_amount_minor),
                "discount_amount_minor": (order.discount_amount_minor),
                "shipping_amount_minor": (order.shipping_amount_minor),
                "tax_amount_minor": order.tax_amount_minor,
                "total_amount_minor": order.total_amount_minor,
                "items": [
                    {
                        "order_item_id": item.order_item_id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price_amount_minor": (item.unit_price_amount_minor),
                        "discount_amount_minor": (item.discount_amount_minor),
                    }
                    for item in items
                ],
                "promotion_codes": [],
            },
        }

    def _build_payment_authorized_event(
        self,
        payment: Payment,
        order: Order,
    ) -> dict[str, Any]:
        """Build a payment_authorized event."""
        event_time = payment.updated_at

        return {
            "event_id": str(
                deterministic_uuid(
                    "payment-authorized-event",
                    payment.payment_id,
                    self.config.seed,
                )
            ),
            "event_type": "payment_authorized",
            "event_version": 1,
            "event_time": to_epoch_millis(event_time),
            "produced_at": to_epoch_millis(event_time + timedelta(seconds=1)),
            "producer": "data-generator",
            "correlation_id": order.order_id,
            "trace_id": str(
                deterministic_uuid(
                    "trace",
                    order.order_id,
                    self.config.seed,
                )
            ),
            "payload": {
                "payment_id": payment.payment_id,
                "order_id": order.order_id,
                "attempt_number": payment.attempt_number,
                "authorized_amount_minor": payment.amount_minor,
                "currency": payment.currency,
                "payment_provider": payment.payment_provider,
                "provider_authorization_id": (payment.provider_transaction_id),
                "authorization_expires_at": to_epoch_millis(
                    event_time + timedelta(hours=1)
                ),
            },
        }
