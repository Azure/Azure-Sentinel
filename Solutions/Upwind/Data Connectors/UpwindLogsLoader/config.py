"""Configuration management for the Upwind Catalog Loader function."""

import logging
import os

from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv


class ConfigStore:
    """External parameters required by the function application."""

    def __init__(self, **kwargs):
        self._config = {}
        for key, value in kwargs.items():
            self._config[key] = value

    def get(self, key, default=None):
        """Retrieve a config value by key."""
        return self._config.get(key, default)

    def __repr__(self):
        return f"ConfigStore(keys={list(self._config.keys())})"


_REQUIRED_CONFIG_KEYS = [
    "azure_dce_endpoint",
    "azure_dcr_immutableid",
    "azure_stream_name_inventory",
    "upwind_org_id",
    "upwind_client_id",
    "upwind_auth_url",
]


def _parse_int_env(name: str, default: str) -> int:
    raw = os.getenv(name, default)
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Invalid integer for {name}: '{raw}'")


def _resolve_upwind_secret(azure_client_id, key_vault_uri, secret_name):
    """Retrieve Upwind client secret from Key Vault (preferred) or env var (fallback)."""

    if key_vault_uri and secret_name and azure_client_id:
        try:
            credential = ManagedIdentityCredential(client_id=azure_client_id)
            secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
            retrieved_secret = secret_client.get_secret(secret_name)
            logging.info("Successfully retrieved Upwind secret from Key Vault.")
            return retrieved_secret.value
        except Exception as e:
            logging.error("Failed to retrieve Upwind secret from Key Vault: %s", e)
            return None

    logging.warning(
        "Key Vault not fully configured. "
        "Falling back to UPWIND_CLIENT_SECRET env var."
    )
    return os.getenv("UPWIND_CLIENT_SECRET")


def load_configuration() -> ConfigStore:
    """Load and validate configuration from environment variables and Key Vault."""

    load_dotenv()

    azure_client_id = os.getenv("AZURE_CLIENT_ID")
    upwind_client_secret = _resolve_upwind_secret(
        azure_client_id,
        os.getenv("KEY_VAULT_URI"),
        os.getenv("UPWIND_SECRET_NAME"),
    )

    config = ConfigStore(
        azure_client_id=azure_client_id,
        azure_dce_endpoint=os.getenv("DCE_ENDPOINT"),
        azure_dcr_immutableid=os.getenv("DCR_IMMUTABLEID"),
        # Inventory/catalog keeps the original STREAM_NAME env var as a fallback
        # so Function Apps deployed before the multi-endpoint update keep working
        # without needing every new app setting populated immediately.
        azure_stream_name_inventory=os.getenv("STREAM_NAME_INVENTORY", os.getenv("STREAM_NAME")),
        azure_stream_name_vulnerability=os.getenv("STREAM_NAME_VULNERABILITY"),
        azure_stream_name_threat_detections=os.getenv("STREAM_NAME_THREAT_DETECTIONS"),
        azure_stream_name_threat_events=os.getenv("STREAM_NAME_THREAT_EVENTS"),
        azure_stream_name_threat_stories=os.getenv("STREAM_NAME_THREAT_STORIES"),
        azure_stream_name_config_findings=os.getenv("STREAM_NAME_CONFIG_FINDINGS"),
        upwind_org_id=os.getenv("UPWIND_ORG_ID"),
        upwind_client_id=os.getenv("UPWIND_CLIENT_ID"),
        upwind_client_secret=upwind_client_secret,
        upwind_auth_url=os.getenv("UPWIND_AUTH_URL", "https://auth.upwind.io/oauth/token"),
        upwind_api_base_url=os.getenv("UPWIND_API_BASE_URL", "https://api.upwind.io"),
        upwind_page_size=_parse_int_env("UPWIND_PAGE_SIZE", "100"),
        upwind_max_retries=_parse_int_env("UPWIND_MAX_RETRIES", "5"),
        upwind_initial_backoff_seconds=_parse_int_env("UPWIND_INITIAL_BACKOFF_SECONDS", "1"),
        upwind_max_backoff_seconds=_parse_int_env("UPWIND_MAX_BACKOFF_SECONDS", "60"),
        upwind_threat_lookback_minutes=_parse_int_env("UPWIND_THREAT_LOOKBACK_MINUTES", "90"),
    )

    # Validate required config
    missing = []
    for key in _REQUIRED_CONFIG_KEYS:
        if not config.get(key):
            missing.append(key)
    if not upwind_client_secret:
        missing.append("UPWIND_CLIENT_SECRET (or KEY_VAULT_URI + UPWIND_SECRET_NAME)")
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    logging.info(
        "Config loaded: dce_endpoint=%s, org_id=%s, page_size=%s",
        config.get("azure_dce_endpoint"),
        config.get("upwind_org_id"),
        config.get("upwind_page_size"),
    )

    return config
