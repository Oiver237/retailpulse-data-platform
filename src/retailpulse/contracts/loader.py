"""Utilities for loading RetailPulse data contracts."""

import json
from pathlib import Path
from typing import Any

import yaml

Contract = dict[str, Any]


class ContractLoadingError(ValueError):
    """Raised when a contract cannot be loaded."""


def load_json_contract(path: Path) -> Contract:
    """Load a JSON or Avro contract from disk."""

    try:
        content = path.read_text(encoding="utf-8")
        contract = json.loads(content)
    except FileNotFoundError as error:
        raise ContractLoadingError(f"Contract not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ContractLoadingError(f"Invalid JSON contract: {path}") from error

    if not isinstance(contract, dict):
        raise ContractLoadingError(f"Contract must contain a JSON object: {path}")

    return contract


def load_yaml_contract(path: Path) -> Contract:
    """Load a YAML data contract from disk."""

    try:
        content = path.read_text(encoding="utf-8")
        contract = yaml.safe_load(content)
    except FileNotFoundError as error:
        raise ContractLoadingError(f"Contract not found: {path}") from error
    except yaml.YAMLError as error:
        raise ContractLoadingError(f"Invalid YAML contract: {path}") from error

    if not isinstance(contract, dict):
        raise ContractLoadingError(f"Contract must contain a YAML mapping: {path}")

    return contract
