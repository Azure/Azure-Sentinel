# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Credentials for Azure SDK clients."""

from ._exceptions import CredentialUnavailableError
from ._constants import AzureAuthorityHosts, KnownAuthorities
from ._credentials import (
    AzureCliCredential,
    AuthorizationCodeCredential,
    CertificateCredential,
    ChainedTokenCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    DeviceCodeCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    UsernamePasswordCredential,
    VisualStudioCodeCredential,
)


__all__ = [
    "AuthorizationCodeCredential",
    "AzureAuthorityHosts",
    "AzureCliCredential",
    "CertificateCredential",
    "ChainedTokenCredential",
    "ClientSecretCredential",
    "CredentialUnavailableError",
    "DefaultAzureCredential",
    "DeviceCodeCredential",
    "EnvironmentCredential",
    "InteractiveBrowserCredential",
    "KnownAuthorities",
    "ManagedIdentityCredential",
    "SharedTokenCacheCredential",
    "UsernamePasswordCredential",
    "VisualStudioCodeCredential",
]

from ._version import VERSION

__version__ = VERSION
