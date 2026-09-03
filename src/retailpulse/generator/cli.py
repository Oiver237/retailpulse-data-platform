"""Command-line interface for synthetic data generation."""

import argparse
from pathlib import Path

from retailpulse.generator.config import GenerationConfig
from retailpulse.generator.service import DataGenerator
from retailpulse.generator.writers import write_dataset


def build_parser() -> argparse.ArgumentParser:
    """Build the generator command-line parser."""

    parser = argparse.ArgumentParser(description="Generate synthetic RetailPulse data.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--run-id",
        default="tiny-seed-42",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/generated"),
    )
    parser.add_argument(
        "--customers",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--products",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--orders",
        type=int,
        default=500,
    )
    parser.add_argument(
        "--currency",
        default="EUR",
        help="Three-letter uppercase currency code, for example EUR or USD.",
    )
    return parser


def main() -> None:
    """Generate and write a synthetic dataset."""

    arguments = build_parser().parse_args()

    config = GenerationConfig(
        seed=arguments.seed,
        run_id=arguments.run_id,
        customer_count=arguments.customers,
        product_count=arguments.products,
        order_count=arguments.orders,
        currency=arguments.currency,
    )

    dataset = DataGenerator(config).generate()
    manifest_path = write_dataset(
        dataset,
        config,
        arguments.output,
    )

    print(f"Generation completed: {manifest_path}")


if __name__ == "__main__":
    main()
