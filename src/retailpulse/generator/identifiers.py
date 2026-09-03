"""Deterministic identifiers for generated entities."""

from uuid import NAMESPACE_URL, UUID, uuid5


def deterministic_uuid(
    entity_type: str,
    entity_key: str,
    seed: int,
) -> UUID:
    """Build a stable UUID from an entity type, key and seed."""

    if not entity_type.strip():
        raise ValueError("entity_type must not be empty.")

    if not entity_key.strip():
        raise ValueError("entity_key must not be empty.")

    source = f"https://retailpulse.local/{seed}/{entity_type}/{entity_key}"
    return uuid5(NAMESPACE_URL, source)
