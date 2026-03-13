# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Optional, Any

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.exceptions import ClientAuthenticationError

from .._internal.managed_identity_base import AsyncManagedIdentityBase
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from ..._credentials.service_fabric import _get_client_args, SERVICE_FABRIC_ERROR_MESSAGE


class ServiceFabricCredential(AsyncManagedIdentityBase):
    def get_client(self, **kwargs: Any) -> Optional[AsyncManagedIdentityClient]:
        client_args = _get_client_args(**kwargs)
        if client_args:
            return AsyncManagedIdentityClient(**client_args)
        return None

    def get_unavailable_message(self, desc: str = "") -> str:
        return f"Service Fabric managed identity configuration not found in environment. {desc}"

    async def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        if self._client and self._client._identity_config:  # pylint:disable=protected-access
            raise ClientAuthenticationError(message=SERVICE_FABRIC_ERROR_MESSAGE)
        return await super().get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:

        if self._client and self._client._identity_config:  # pylint:disable=protected-access
            raise ClientAuthenticationError(message=SERVICE_FABRIC_ERROR_MESSAGE)
        return await super().get_token_info(*scopes, options=options)
