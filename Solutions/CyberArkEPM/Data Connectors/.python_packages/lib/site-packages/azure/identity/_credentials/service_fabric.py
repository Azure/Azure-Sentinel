# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Dict, Optional, Any

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.exceptions import ClientAuthenticationError
from azure.core.rest import HttpRequest

from .._constants import EnvironmentVariables
from .._internal.msal_managed_identity_client import MsalManagedIdentityClient


SERVICE_FABRIC_ERROR_MESSAGE = (
    "Specifying a client_id or identity_config is not supported by the Service Fabric managed identity environment. "
    "The managed identity configuration is determined by the Service Fabric cluster resource configuration. "
    "See https://aka.ms/servicefabricmi for more information."
)


class ServiceFabricCredential(MsalManagedIdentityClient):
    def get_unavailable_message(self, desc: str = "") -> str:
        return f"Service Fabric managed identity configuration not found in environment. {desc}"

    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        if self._settings.get("client_id") or self._settings.get("identity_config"):
            raise ClientAuthenticationError(message=SERVICE_FABRIC_ERROR_MESSAGE)
        return super().get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        if self._settings.get("client_id") or self._settings.get("identity_config"):
            raise ClientAuthenticationError(message=SERVICE_FABRIC_ERROR_MESSAGE)
        return super().get_token_info(*scopes, options=options)


def _get_client_args(**kwargs: Any) -> Optional[Dict]:
    url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
    secret = os.environ.get(EnvironmentVariables.IDENTITY_HEADER)
    thumbprint = os.environ.get(EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT)
    if not (url and secret and thumbprint):
        # Service Fabric managed identity isn't available in this environment
        return None

    return dict(
        kwargs,
        base_headers={"Secret": secret},
        connection_verify=False,  # pylint: disable=do-not-hardcode-connection-verify
        request_factory=functools.partial(_get_request, url),
    )


def _get_request(url: str, scope: str, identity_config: Dict) -> HttpRequest:
    return HttpRequest(
        "GET", url, params=dict({"api-version": "2019-07-01-preview", "resource": scope}, **identity_config)
    )
