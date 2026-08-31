"""Domain models produced by the synthetic data generator."""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Customer:
    """Synthetic retail customer."""

    customer_id: str
    first_name: str
    last_name: str
    email: str
    country_code: str
    created_at: datetime

    def to_record(self) -> dict[str, Any]:
        """Convert the customer to a serializable record."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class Category:
    """Retail product category."""

    category_id: str
    category_name: str

    def to_record(self) -> dict[str, Any]:
        """Convert the category to a serializable record."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class Product:
    """Synthetic retail product."""

    product_id: str
    category_id: str
    product_name: str
    unit_price_amount_minor: int
    currency: str
    active: bool
    created_at: datetime

    def to_record(self) -> dict[str, Any]:
        """Convert the product to a serializable record."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class Order:
    """Synthetic customer order."""

    order_id: str
    customer_id: str
    channel: str
    status: str
    currency: str
    subtotal_amount_minor: int
    discount_amount_minor: int
    shipping_amount_minor: int
    tax_amount_minor: int
    total_amount_minor: int
    created_at: datetime
    updated_at: datetime

    def to_record(self) -> dict[str, Any]:
        """Convert the order to a serializable record."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class OrderItem:
    """Product line belonging to an order."""

    order_item_id: str
    order_id: str
    product_id: str
    quantity: int
    unit_price_amount_minor: int
    discount_amount_minor: int

    def to_record(self) -> dict[str, Any]:
        """Convert the order item to a serializable record."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class Payment:
    """Synthetic payment attempt."""

    payment_id: str
    order_id: str
    attempt_number: int
    status: str
    amount_minor: int
    currency: str
    payment_method: str
    payment_provider: str
    provider_transaction_id: str | None
    created_at: datetime
    updated_at: datetime

    def to_record(self) -> dict[str, Any]:
        """Convert the payment to a serializable record."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class GeneratedDataset:
    """Complete output of one generation run."""

    customers: list[Customer]
    categories: list[Category]
    products: list[Product]
    orders: list[Order]
    order_items: list[OrderItem]
    payments: list[Payment]
    order_events: list[dict[str, Any]]
    payment_events: list[dict[str, Any]]
