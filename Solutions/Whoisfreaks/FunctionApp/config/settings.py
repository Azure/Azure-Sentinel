import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Raised when required application configuration is missing."""


def _require(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ConfigError(
            f"Required application setting '{name}' is not configured."
        )

    return value


def _optional(name: str, default: str = "") -> str:
    return os.getenv(name) or default


@dataclass(frozen=True)
class Settings:
    api_key: str
    checkpoint_storage_account: str
    dcr_ingestion_endpoint: str
    dcr_immutable_id: str


def load_settings() -> Settings:
    """
    Load and validate application settings.

    WHOISFREAKS_API_KEY may be empty only for infrastructure / local
    testing of the Function host itself. Live feed ingestion requires
    a real key (normally supplied by the end-user during Content Hub
    installation via createUiDefinition).

    All other settings remain mandatory so a misconfigured deployment
    fails fast instead of writing to the wrong resources.
    """

    return Settings(
        api_key=_optional("WHOISFREAKS_API_KEY"),
        checkpoint_storage_account=_require("CHECKPOINT_STORAGE_ACCOUNT"),
        dcr_ingestion_endpoint=_require("DCR_INGESTION_ENDPOINT"),
        dcr_immutable_id=_require("DCR_IMMUTABLE_ID"),
    )
