# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError
from .._internal import AadClient, AsyncContextManager
from .._internal.decorators import log_get_token_async

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, Optional
    from azure.core.credentials import AccessToken


class AuthorizationCodeCredential(AsyncContextManager):
    """Authenticates by redeeming an authorization code previously obtained from Azure Active Directory.

    See https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-auth-code-flow for more information
    about the authentication flow.

    :param str tenant_id: ID of the application's Azure Active Directory tenant. Also called its 'directory' ID.
    :param str client_id: the application's client ID
    :param str authorization_code: the authorization code from the user's log-in
    :param str redirect_uri: The application's redirect URI. Must match the URI used to request the authorization code.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword str client_secret: One of the application's client secrets. Required only for web apps and web APIs.
    """

    async def __aenter__(self):
        if self._client:
            await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._client:
            await self._client.__aexit__()

    def __init__(
        self, tenant_id: str, client_id: str, authorization_code: str, redirect_uri: str, **kwargs: "Any"
    ) -> None:
        self._authorization_code = authorization_code  # type: Optional[str]
        self._client_id = client_id
        self._client_secret = kwargs.pop("client_secret", None)
        self._client = kwargs.pop("client", None) or AadClient(tenant_id, client_id, **kwargs)
        self._redirect_uri = redirect_uri

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        The first time this method is called, the credential will redeem its authorization code. On subsequent calls
        the credential will return a cached access token or redeem a refresh token, if it acquired a refresh token upon
        redeeming the authorization code.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason. Any error response from Azure Active Directory is available as the error's
          ``response`` attribute.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        if self._authorization_code:
            token = await self._client.obtain_token_by_authorization_code(
                scopes=scopes, code=self._authorization_code, redirect_uri=self._redirect_uri, **kwargs
            )

            self._authorization_code = None  # auth codes are single-use
            return token

        token = self._client.get_cached_access_token(scopes)
        if not token:
            token = await self._redeem_refresh_token(scopes, **kwargs)
        elif self._client.should_refresh(token):
            try:
                await self._redeem_refresh_token(scopes, **kwargs)
            except Exception:  # pylint: disable=broad-except
                pass
        if not token:
            raise ClientAuthenticationError(
                message="No authorization code, cached access token, or refresh token available."
            )

        return token

    async def _redeem_refresh_token(self, scopes: "Iterable[str]", **kwargs: "Any") -> "Optional[AccessToken]":
        for refresh_token in self._client.get_cached_refresh_tokens(scopes):
            if "secret" not in refresh_token:
                continue
            token = await self._client.obtain_token_by_refresh_token(scopes, refresh_token["secret"], **kwargs)
            if token:
                return token
        return None
