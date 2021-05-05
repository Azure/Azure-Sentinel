# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from six.moves.urllib_parse import urlparse

from .._constants import EnvironmentVariables, KnownAuthorities


def normalize_authority(authority):
    # type: (str) -> str
    """Ensure authority uses https, strip trailing spaces and /"""

    parsed = urlparse(authority)
    if not parsed.scheme:
        return "https://" + authority.rstrip(" /")
    if parsed.scheme != "https":
        raise ValueError(
            "'{}' is an invalid authority. The value must be a TLS protected (https) URL.".format(authority)
        )

    return authority.rstrip(" /")


def get_default_authority():
    # type: () -> str
    authority = os.environ.get(EnvironmentVariables.AZURE_AUTHORITY_HOST, KnownAuthorities.AZURE_PUBLIC_CLOUD)
    return normalize_authority(authority)


VALID_TENANT_ID_CHARACTERS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789" + "-.")


def validate_tenant_id(tenant_id):
    """Raise ValueError if tenant_id is empty or contains a character invalid for a tenant id"""
    # type: (str) -> None
    if not tenant_id or any(c not in VALID_TENANT_ID_CHARACTERS for c in tenant_id):
        raise ValueError(
            "Invalid tenant id provided. You can locate your tenant id by following the instructions here: "
            + "https://docs.microsoft.com/partner-center/find-ids-and-domain-names"
        )


# pylint:disable=wrong-import-position
from .aad_client import AadClient
from .aad_client_base import AadClientBase
from .auth_code_redirect_handler import AuthCodeRedirectServer
from .aadclient_certificate import AadClientCertificate
from .certificate_credential_base import CertificateCredentialBase
from .client_secret_credential_base import ClientSecretCredentialBase
from .decorators import wrap_exceptions
from .interactive import InteractiveCredential


def _scopes_to_resource(*scopes):
    """Convert an AADv2 scope to an AADv1 resource"""

    if len(scopes) != 1:
        raise ValueError("This credential requires exactly one scope per token request.")

    resource = scopes[0]
    if resource.endswith("/.default"):
        resource = resource[: -len("/.default")]

    return resource


__all__ = [
    "_scopes_to_resource",
    "AadClient",
    "AadClientBase",
    "AuthCodeRedirectServer",
    "AadClientCertificate",
    "CertificateCredentialBase",
    "ClientSecretCredentialBase",
    "get_default_authority",
    "InteractiveCredential",
    "normalize_authority",
    "wrap_exceptions",
]
