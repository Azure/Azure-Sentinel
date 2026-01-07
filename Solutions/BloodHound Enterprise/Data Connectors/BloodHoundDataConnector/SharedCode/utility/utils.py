import os
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

@dataclass
class EnvironmentConfig:
    """Configuration for a BloodHound environment."""
    tenant_domain: str
    token_id: str
    token_key: str
    selected_environments: Optional[List[str]] = None
    selected_finding_types: Optional[str] = None  # Can be "all" or comma-separated list

@dataclass
class AzureConfig:
    """Azure-specific configuration."""
    tenant_id: str
    app_id: str
    app_secret: str
    dce_uri: str
    dcr_immutable_id: str
    table_name: str
    key_vault_url: str

def fetch_env_variables(required_vars):
    """
    Fetches all required environment variables and returns a dict.
    Logs and raises KeyError if any are missing.
    """
    env = {}
    missing = []
    for var in required_vars:
        value = os.environ.get(var)
        if value is None:
            missing.append(var)
        env[var] = value
    if missing:
        logging.error(f"Missing required environment variables: {', '.join(missing)}")
        raise KeyError(f"Missing required environment variables: {', '.join(missing)}")
    return env

def fetch_key_vault_secrets(key_vault_url, token_ids_secret_name, token_keys_secret_name):
    """
    Fetches token IDs and token keys from Azure Key Vault.
    Returns two lists: all_token_ids, all_token_keys.
    
    Note: This function does not handle exceptions. The caller is responsible for
    catching and logging any errors that occur during secret retrieval.
    """
    credential = DefaultAzureCredential()         # CodeQL [SM05139] CCF based data connector is in development. This will be retired once CCF based data connector is generally available.
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
    
    token_ids = secret_client.get_secret(token_ids_secret_name).value
    token_keys = secret_client.get_secret(token_keys_secret_name).value
    
    all_token_ids = [token_id.strip() for token_id in token_ids.split(',')]
    all_token_keys = [token_key.strip() for token_key in token_keys.split(',')]
    
    logging.info("Successfully retrieved all API tokens from Azure Key Vault.")
    
    return all_token_ids, all_token_keys

def get_token_lists(key_vault_url=None, token_ids_secret_name=None, token_keys_secret_name=None):
    """
    Returns all_token_ids and all_token_keys from Key Vault using provided names and URL.
    Raises ValueError if insufficient information is provided.
    """
    if key_vault_url and token_ids_secret_name and token_keys_secret_name:
        return fetch_key_vault_secrets(key_vault_url, token_ids_secret_name, token_keys_secret_name)
    else:
        logging.error("Insufficient information to fetch token IDs and keys from Key Vault.")
        raise ValueError("Insufficient information to fetch token IDs and keys from Key Vault.")

def load_environment_configs(table_name: str) -> Tuple[List[EnvironmentConfig], AzureConfig]:
    """
    Load and validate environment configurations.
    
    Args:
        table_name: Name of the table environment variable to use (e.g. 'AUDIT_LOGS_TABLE_NAME' or 'TIER_ZERO_ASSETS_TABLE_NAME')
    
    Returns:
        Tuple containing list of BloodHound environment configs and Azure config
    Raises:
        KeyError: If required environment variables are missing
        ValueError: If configuration validation fails
    """
    env_vars = fetch_env_variables([
        "BLOODHOUND_TENANT_DOMAIN",
        "BLOODHOUND_TOKEN_ID_SECRET_NAME",
        "BLOODHOUND_TOKEN_KEY_SECRET_NAME",
        "MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID",
        "MICROSOFT_ENTRA_ID_APPLICATION_APP_ID",
        "MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET",
        "DCE_URI",
        "DCR_IMMUTABLE_ID",
        table_name,
        "KEY_VAULT_URL",
        # "BLOODHOUND_TOKEN_ID",
        # "BLOODHOUND_TOKEN_KEY",
        "SELECTED_BLOODHOUND_ENVIRONMENTS",
        "SELECTED_FINDING_TYPES"
    ])

    # Parse environment configs
    tenant_domains = [td.strip() for td in env_vars["BLOODHOUND_TENANT_DOMAIN"].split(',')]
    
    # if env_vars["BLOODHOUND_TOKEN_ID"] and env_vars["BLOODHOUND_TOKEN_KEY"]:
    #     token_ids = [tid.strip() for tid in env_vars["BLOODHOUND_TOKEN_ID"].split(',')]
    #     token_keys = [tkey.strip() for tkey in env_vars["BLOODHOUND_TOKEN_KEY"].split(',')]
    # else:
    #     token_ids, token_keys = get_token_lists(
    #         key_vault_url=env_vars["KEY_VAULT_URL"],
    #         token_ids_secret_name=env_vars["BLOODHOUND_TOKEN_ID_SECRET_NAME"],
    #         token_keys_secret_name=env_vars["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
    #     )

    token_ids, token_keys = get_token_lists(
            key_vault_url=env_vars["KEY_VAULT_URL"],
            token_ids_secret_name=env_vars["BLOODHOUND_TOKEN_ID_SECRET_NAME"],
            token_keys_secret_name=env_vars["BLOODHOUND_TOKEN_KEY_SECRET_NAME"]
        )

    if not (len(tenant_domains) == len(token_ids) == len(token_keys)):
        raise ValueError("Environment variable lists for domains, token IDs, and token keys have a mismatch in length")

    # Get the selected environments and finding types from environment variables
    selected_environments = env_vars.get("SELECTED_BLOODHOUND_ENVIRONMENTS")
    selected_finding_types = env_vars.get("SELECTED_FINDING_TYPES")

    env_configs = [
        EnvironmentConfig(
            domain, 
            tid, 
            tkey,
            selected_environments=selected_environments,
            selected_finding_types=selected_finding_types
        )
        for domain, tid, tkey in zip(tenant_domains, token_ids, token_keys)
    ]

    azure_config = AzureConfig(
        tenant_id=env_vars["MICROSOFT_ENTRA_ID_APPLICATION_TENANT_ID"],
        app_id=env_vars["MICROSOFT_ENTRA_ID_APPLICATION_APP_ID"],
        app_secret=env_vars["MICROSOFT_ENTRA_ID_APPLICATION_APP_SECRET"],
        dce_uri=env_vars["DCE_URI"],
        dcr_immutable_id=env_vars["DCR_IMMUTABLE_ID"],
        table_name=env_vars[table_name],
        key_vault_url=env_vars["KEY_VAULT_URL"]
    )

    return env_configs, azure_config
