"""Configuration models for synthetic data generation."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class GenerationConfig:
    """Configuration of a deterministic generation run."""

    seed: int = 42
    run_id: str = "tiny-seed-42"
    customer_count: int = 100
    category_count: int = 5
    product_count: int = 50
    order_count: int = 500
    currency: str = "EUR"
    start_time: datetime = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )

    def __post_init__(self) -> None:
        """Validate generation settings."""

        positive_fields = {
            "customer_count": self.customer_count,
            "category_count": self.category_count,
            "product_count": self.product_count,
            "order_count": self.order_count,
        }

        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be strictly positive.")

        if not self.run_id.strip():
            raise ValueError("run_id must not be empty.")

        if len(self.currency) != 3 or not self.currency.isupper():
            raise ValueError("currency must contain three uppercase letters.")

        if self.start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware.")
