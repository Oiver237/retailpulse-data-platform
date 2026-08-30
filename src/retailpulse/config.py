"""Shared configuration primitives for the RetailPulse platform."""

from dataclasses import dataclass
from enum import StrEnum
from os import getenv


class Environment(StrEnum):
    """Supported execution environments."""

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


@dataclass(frozen=True, slots=True)
class Settings:
    """Minimal platform settings shared by RetailPulse components."""

    environment: Environment
    log_level: str
    project_name: str = "retailpulse"

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings from environment variables."""

        environment_value = getenv("RETAILPULSE_ENV", Environment.LOCAL.value)
        log_level = getenv("RETAILPULSE_LOG_LEVEL", "INFO").upper()

        try:
            environment = Environment(environment_value)
        except ValueError as error:
            allowed_values = ", ".join(item.value for item in Environment)
            message = (
                f"Unsupported RETAILPULSE_ENV={environment_value!r}. "
                f"Expected one of: {allowed_values}."
            )
            raise ValueError(message) from error

        allowed_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level not in allowed_log_levels:
            message = (
                f"Unsupported RETAILPULSE_LOG_LEVEL={log_level!r}. "
                f"Expected one of: {sorted(allowed_log_levels)}."
            )
            raise ValueError(message)

        return cls(
            environment=environment,
            log_level=log_level,
        )
