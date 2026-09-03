"""Tests for deterministic identifiers."""

import pytest

from retailpulse.generator.identifiers import deterministic_uuid


def test_identifier_is_deterministic() -> None:
    """The same inputs should produce the same identifier."""

    first = deterministic_uuid("customer", "1", 42)
    second = deterministic_uuid("customer", "1", 42)

    assert first == second


def test_identifier_changes_with_seed() -> None:
    """Different seeds should produce different identifiers."""

    first = deterministic_uuid("customer", "1", 42)
    second = deterministic_uuid("customer", "1", 43)

    assert first != second


def test_identifier_changes_with_entity_type() -> None:
    """Different entity types should not share identifiers."""

    customer_id = deterministic_uuid("customer", "1", 42)
    product_id = deterministic_uuid("product", "1", 42)

    assert customer_id != product_id


def test_identifier_rejects_empty_entity_type() -> None:
    """Entity type must not be empty."""

    with pytest.raises(ValueError, match="entity_type"):
        deterministic_uuid("", "1", 42)


def test_identifier_rejects_empty_entity_key() -> None:
    """Entity key must not be empty."""

    with pytest.raises(ValueError, match="entity_key"):
        deterministic_uuid("customer", "", 42)
