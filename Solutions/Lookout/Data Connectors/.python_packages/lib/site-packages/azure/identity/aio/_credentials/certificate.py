# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .._internal import AadClient, AsyncContextManager
from .._internal.decorators import log_get_token_async
from ..._internal import CertificateCredentialBase

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken


class CertificateCredential(CertificateCredentialBase, AsyncContextManager):
    """Authenticates as a service principal using a certificate.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str certificate_path: path to a PEM-encoded certificate file including the private key

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword password: The certificate's password. If a unicode string, it will be encoded as UTF-8. If the certificate
          requires a different encoding, pass appropriately encoded bytes instead.
    :paramtype password: str or bytes
    """

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        await self._client.__aexit__()

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason. Any error response from Azure Active Directory is available as the error's
          ``response`` attribute.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        token = self._client.get_cached_access_token(scopes, query={"client_id": self._client_id})
        if not token:
            token = await self._client.obtain_token_by_client_certificate(scopes, self._certificate, **kwargs)
        elif self._client.should_refresh(token):
            try:
                await self._client.obtain_token_by_client_certificate(scopes, self._certificate, **kwargs)
            except Exception:  # pylint: disable=broad-except
                pass
        return token

    def _get_auth_client(self, tenant_id, client_id, **kwargs):
        return AadClient(tenant_id, client_id, **kwargs)
