# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Optional, Any

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from .._internal import AsyncContextManager
from .._internal.decorators import log_get_token_async
from ..._credentials.vscode import VisualStudioCodeCredential as SyncVSCodeCredential


class VisualStudioCodeCredential(AsyncContextManager):
    """Authenticates as the Azure user signed in to Visual Studio Code via the 'Azure Resources' extension.

    This currently only works in Windows/WSL environments and requires the 'azure-identity-broker'
    package to be installed.

    :keyword str tenant_id: A Microsoft Entra tenant ID. Defaults to the tenant specified in the authentication
        record file used by the Azure Resources extension.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._sync_credential = SyncVSCodeCredential(**kwargs)

    async def __aenter__(self) -> "VisualStudioCodeCredential":
        self._sync_credential.__enter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""
        self._sync_credential.close()

    @log_get_token_async
    async def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
            Studio Code
        """
        return self._sync_credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes` as the user currently signed in to Visual Studio Code.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises ~azure.identity.CredentialUnavailableError: the credential cannot retrieve user details from Visual
          Studio Code.
        """
        return self._sync_credential.get_token_info(*scopes, options=options)
