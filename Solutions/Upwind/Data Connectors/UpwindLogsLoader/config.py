"""Configuration management for the Upwind Logs Loader function."""

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
    "azure_stream_name",
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


def _resolve_upwind_secret(credential, key_vault_uri, secret_name):
    """Retrieve Upwind client secret from Key Vault (preferred) or env var (fallback)."""

    if key_vault_uri and secret_name and credential:
        try:
            secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
            retrieved_secret = secret_client.get_secret(secret_name)
            logging.debug("Successfully retrieved Upwind secret from Key Vault.")
            return retrieved_secret.value
        except Exception as e:
            logging.error("Failed to retrieve Upwind secret from Key Vault: %s", e)
            return None

    logging.warning(
        "Key Vault not fully configured. "
        "Falling back to UPWIND_CLIENT_SECRET env var."
    )
    return os.getenv("UPWIND_CLIENT_SECRET")


def load_configuration(azure_credential=None) -> ConfigStore:
    """Load and validate configuration from environment variables and Key Vault.

    :param azure_credential: Azure credential to use for Key Vault and DCR uploads.
                             Defaults to ManagedIdentityCredential when not provided.
    """

    load_dotenv()

    azure_client_id = os.getenv("AZURE_CLIENT_ID")

    if azure_credential is None and azure_client_id:
        azure_credential = ManagedIdentityCredential(client_id=azure_client_id)

    upwind_client_secret = _resolve_upwind_secret(
        azure_credential,
        os.getenv("KEY_VAULT_URI"),
        os.getenv("UPWIND_SECRET_NAME"),
    )

    config = ConfigStore(
        azure_credential=azure_credential,
        azure_dce_endpoint=os.getenv("DCE_ENDPOINT"),
        azure_dcr_immutableid=os.getenv("DCR_IMMUTABLEID"),
        azure_stream_name=os.getenv("STREAM_NAME"),
        upwind_org_id=os.getenv("UPWIND_ORG_ID"),
        upwind_client_id=os.getenv("UPWIND_CLIENT_ID"),
        upwind_client_secret=upwind_client_secret,
        upwind_auth_url=os.getenv("UPWIND_AUTH_URL", "https://auth.upwind.io/oauth/token"),
        upwind_api_base_url=os.getenv("UPWIND_API_BASE_URL", "https://api.upwind.io"),
        upwind_page_size=_parse_int_env("UPWIND_PAGE_SIZE", "100"),
        upwind_max_retries=_parse_int_env("UPWIND_MAX_RETRIES", "5"),
        upwind_initial_backoff_seconds=_parse_int_env("UPWIND_INITIAL_BACKOFF_SECONDS", "1"),
        upwind_max_backoff_seconds=_parse_int_env("UPWIND_MAX_BACKOFF_SECONDS", "60"),
    )

    # Validate required config
    missing = []
    for key in _REQUIRED_CONFIG_KEYS:
        if not config.get(key):
            missing.append(key)
    if not upwind_client_secret:
        missing.append("UPWIND_CLIENT_SECRET (or KEY_VAULT_URI + UPWIND_SECRET_NAME)")
    if not azure_credential:
        missing.append("AZURE_CLIENT_ID (or azure_credential)")
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    logging.debug(
        "Config loaded: dce_endpoint=%s, org_id=%s, page_size=%s",
        config.get("azure_dce_endpoint"),
        config.get("upwind_org_id"),
        config.get("upwind_page_size"),
    )

    return config
