# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import os
import platform
import logging
from contextvars import ContextVar
from string import ascii_letters, digits
from typing import List, Optional

from urllib.parse import urlparse

from azure.core.exceptions import ClientAuthenticationError
from .._constants import EnvironmentVariables, KnownAuthorities

within_credential_chain = ContextVar("within_credential_chain", default=False)
within_dac = ContextVar("within_dac", default=False)

_LOGGER = logging.getLogger(__name__)

VALID_TENANT_ID_CHARACTERS = frozenset(ascii_letters + digits + "-.")
VALID_SCOPE_CHARACTERS = frozenset(ascii_letters + digits + "_-.:/")
VALID_SUBSCRIPTION_CHARACTERS = frozenset(ascii_letters + digits + "_-. ")


def normalize_authority(authority: str) -> str:
    """Ensure authority uses https, strip trailing spaces and /.

    :param str authority: authority to normalize
    :return: normalized authority
    :rtype: str
    :raises: ValueError if authority is not a valid https URL
    """

    parsed = urlparse(authority)
    if not parsed.scheme:
        return "https://" + authority.rstrip(" /")
    if parsed.scheme != "https":
        raise ValueError(
            "'{}' is an invalid authority. The value must be a TLS protected (https) URL.".format(authority)
        )

    return authority.rstrip(" /")


def get_default_authority() -> str:
    authority = os.environ.get(EnvironmentVariables.AZURE_AUTHORITY_HOST, KnownAuthorities.AZURE_PUBLIC_CLOUD)
    return normalize_authority(authority)


def validate_scope(scope: str) -> None:
    """Raise ValueError if scope is empty or contains a character invalid for a scope

    :param str scope: scope to validate
    :raises: ValueError if scope is empty or contains a character invalid for a scope.
    """
    if not scope or any(c not in VALID_SCOPE_CHARACTERS for c in scope):
        raise ValueError(
            "An invalid scope was provided. Only alphanumeric characters, '.', '-', '_', ':', and '/' are allowed."
        )


def validate_tenant_id(tenant_id: str) -> None:
    """Raise ValueError if tenant_id is empty or contains a character invalid for a tenant ID.

    :param str tenant_id: tenant ID to validate
    :raises: ValueError if tenant_id is empty or contains a character invalid for a tenant ID.
    """
    if not tenant_id or any(c not in VALID_TENANT_ID_CHARACTERS for c in tenant_id):
        raise ValueError(
            "Invalid tenant ID provided. You can locate your tenant ID by following the instructions here: "
            "https://learn.microsoft.com/partner-center/find-ids-and-domain-names"
        )


def validate_subscription(subscription: str) -> None:
    """Raise ValueError if subscription is empty or contains a character invalid for a subscription name/ID.

    :param str subscription: subscription ID to validate
    :raises: ValueError if subscription is empty or contains a character invalid for a subscription ID.
    """
    if not subscription or any(c not in VALID_SUBSCRIPTION_CHARACTERS for c in subscription):
        raise ValueError(
            f"Subscription '{subscription}' contains invalid characters. If this is the name of a subscription, use "
            "its ID instead. You can locate your subscription by following the instructions listed here: "
            "https://learn.microsoft.com/azure/azure-portal/get-subscription-tenant-id"
        )


def resolve_tenant(
    default_tenant: str,
    tenant_id: Optional[str] = None,
    *,
    additionally_allowed_tenants: Optional[List[str]] = None,
    **_,
) -> str:
    """Returns the correct tenant for a token request given a credential's configuration.

    :param str default_tenant: The tenant ID configured on the credential.
    :param str tenant_id: The tenant ID requested by the user.
    :keyword list[str] additionally_allowed_tenants: The list of additionally allowed tenants.
    :return: The tenant ID to use for the token request.
    :rtype: str
    :raises: ~azure.core.exceptions.ClientAuthenticationError
    """
    if tenant_id is None or tenant_id == default_tenant:
        return default_tenant
    if default_tenant == "adfs" or os.environ.get(EnvironmentVariables.AZURE_IDENTITY_DISABLE_MULTITENANTAUTH):
        _LOGGER.info(
            "A token was request for a different tenant than was configured on the credential, "
            "but the configured value was used since multi tenant authentication has been disabled. "
            "Configured tenant ID: %s, Requested tenant ID %s",
            default_tenant,
            tenant_id,
        )
        return default_tenant
    if not default_tenant:
        return tenant_id
    if additionally_allowed_tenants is None:
        additionally_allowed_tenants = []
    if "*" in additionally_allowed_tenants or tenant_id in additionally_allowed_tenants:
        _LOGGER.info(
            "A token was requested for a different tenant than was configured on the credential, "
            "and the requested tenant ID was used to authenticate. Configured tenant ID: %s, "
            "Requested tenant ID %s",
            default_tenant,
            tenant_id,
        )
        return tenant_id
    # Some dev credentials commonly default to the "organizations" special tenant which can authenticate users against
    # multiple tenants that the user belongs to. If an allowed tenant list was not provided and the credential's
    # tenant is set to 'organizations', allow the request with the specified tenant ID.
    if not additionally_allowed_tenants and default_tenant == "organizations":
        return tenant_id
    raise ClientAuthenticationError(
        message="The current credential is not configured to acquire tokens for tenant {}. "
        "To enable acquiring tokens for this tenant add it to the additionally_allowed_tenants "
        'when creating the credential, or add "*" to additionally_allowed_tenants to allow '
        "acquiring tokens for any tenant.".format(tenant_id)
    )


def process_credential_exclusions(credential_config: dict, exclude_flags: dict, user_excludes: dict) -> dict:
    """Process credential exclusions based on environment variable and user overrides.

    This method handles the AZURE_TOKEN_CREDENTIALS environment variable to determine
    which credentials should be excluded from the credential chain, and then applies
    any user-provided exclude overrides which take precedence over environment settings.

    :param credential_config: Configuration mapping for all available credentials, containing
        exclude parameter names, environment names, and default exclude settings
    :type credential_config: dict
    :param exclude_flags: Dictionary of exclude flags for each credential (will be modified)
    :type exclude_flags: dict
    :param user_excludes: User-provided exclude overrides from constructor kwargs
    :type user_excludes: dict

    :return: Dictionary of final exclude flags for each credential
    :rtype: dict

    :raises ValueError: If token_credentials_env contains an invalid credential name
    """
    # Handle AZURE_TOKEN_CREDENTIALS environment variable
    token_credentials_env = os.environ.get(EnvironmentVariables.AZURE_TOKEN_CREDENTIALS, "").strip().lower()

    if token_credentials_env == "dev":
        # In dev mode, use only developer credentials
        dev_credentials = {"visual_studio_code", "cli", "developer_cli", "powershell", "shared_token_cache", "broker"}
        for cred_key in credential_config:
            exclude_flags[cred_key] = cred_key not in dev_credentials
    elif token_credentials_env == "prod":
        # In prod mode, use only production credentials
        prod_credentials = {"environment", "workload_identity", "managed_identity"}
        for cred_key in credential_config:
            exclude_flags[cred_key] = cred_key not in prod_credentials
    elif token_credentials_env:
        # If a specific credential is specified, exclude all others except the specified one
        valid_credentials = {config["env_name"] for config in credential_config.values() if "env_name" in config}

        if token_credentials_env not in valid_credentials:
            valid_values = ["dev", "prod"] + sorted(valid_credentials)
            raise ValueError(
                f"Invalid value for {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS}: {token_credentials_env}. "
                f"Valid values are: {', '.join(valid_values)}."
            )

        # Find which credential was selected and exclude all others
        selected_cred_key = None
        for cred_key, config in credential_config.items():
            if config.get("env_name") == token_credentials_env:
                selected_cred_key = cred_key
                break

        for cred_key in credential_config:
            exclude_flags[cred_key] = cred_key != selected_cred_key

    # Apply user-provided exclude flags (these override environment variable settings)
    for cred_key, user_value in user_excludes.items():
        if user_value is not None:
            exclude_flags[cred_key] = user_value

    return exclude_flags


def get_broker_credential() -> Optional[type]:
    """Return the InteractiveBrowserBrokerCredential class if available, otherwise None.

    :return: InteractiveBrowserBrokerCredential class or None
    :rtype: Optional[type]
    """
    try:
        from azure.identity.broker import InteractiveBrowserBrokerCredential

        return InteractiveBrowserBrokerCredential
    except ImportError:
        return None


def is_wsl() -> bool:
    # This is how MSAL checks for WSL.
    uname = platform.uname()
    platform_name = getattr(uname, "system", uname[0]).lower()
    release = getattr(uname, "release", uname[2]).lower()
    return platform_name == "linux" and "microsoft" in release


def encode_base64(s: str) -> str:
    encoded = base64.b64encode(s.encode("utf-8"))
    return encoded.decode("utf-8")
