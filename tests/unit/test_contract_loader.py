"""Tests for contract loading utilities."""

import json
from pathlib import Path

import pytest

from retailpulse.contracts.loader import (
    ContractLoadingError,
    load_json_contract,
    load_yaml_contract,
)


def test_load_json_contract(tmp_path: Path) -> None:
    """A valid JSON contract should be loaded."""

    path = tmp_path / "contract.json"
    path.write_text(
        json.dumps({"name": "order_created"}),
        encoding="utf-8",
    )

    contract = load_json_contract(path)

    assert contract["name"] == "order_created"


def test_missing_json_contract_is_rejected(tmp_path: Path) -> None:
    """A missing contract should produce an explicit error."""

    path = tmp_path / "missing.json"

    with pytest.raises(ContractLoadingError, match="Contract not found"):
        load_json_contract(path)


def test_invalid_json_contract_is_rejected(tmp_path: Path) -> None:
    """Malformed JSON should be rejected."""

    path = tmp_path / "contract.json"
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ContractLoadingError, match="Invalid JSON contract"):
        load_json_contract(path)


def test_load_yaml_contract(tmp_path: Path) -> None:
    """A valid YAML contract should be loaded."""

    path = tmp_path / "contract.yaml"
    path.write_text(
        "contract:\n  name: orders\n  version: 1.0.0\n",
        encoding="utf-8",
    )

    contract = load_yaml_contract(path)

    assert contract["contract"]["name"] == "orders"


def test_payments_dataset_contract_is_complete() -> None:
    """The payments dataset contract should expose its required sections."""

    project_root = Path(__file__).resolve().parents[2]
    contract_path = project_root / "contracts" / "datasets" / "payments-v1.yaml"

    contract = load_yaml_contract(contract_path)

    assert contract["contract"]["name"] == "payments"
    assert contract["contract"]["version"] == "1.0.0"
    assert contract["source"]["table"] == "payments"
    assert contract["source"]["primary_key"] == ["payment_id"]
    assert contract["delivery"]["format"] == "parquet"
    assert contract["schema"]["fields"]
    assert contract["quality"]
    assert contract["classification"]["contains_payment_card_data"] is False
    assert contract["compatibility"]["mode"] == "backward"
