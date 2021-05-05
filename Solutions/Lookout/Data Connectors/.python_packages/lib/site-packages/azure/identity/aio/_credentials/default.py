# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import TYPE_CHECKING

from ..._constants import EnvironmentVariables
from ..._internal import get_default_authority, normalize_authority
from .azure_cli import AzureCliCredential
from .chained import ChainedTokenCredential
from .environment import EnvironmentCredential
from .managed_identity import ManagedIdentityCredential
from .shared_cache import SharedTokenCacheCredential
from .vscode import VisualStudioCodeCredential

if TYPE_CHECKING:
    from typing import Any

_LOGGER = logging.getLogger(__name__)


class DefaultAzureCredential(ChainedTokenCredential):
    """A default credential capable of handling most Azure SDK authentication scenarios.

    The identity it uses depends on the environment. When an access token is needed, it requests one using these
    identities in turn, stopping when one provides a token:

    1. A service principal configured by environment variables. See :class:`~azure.identity.aio.EnvironmentCredential`
       for more details.
    2. An Azure managed identity. See :class:`~azure.identity.aio.ManagedIdentityCredential` for more details.
    3. On Windows only: a user who has signed in with a Microsoft application, such as Visual Studio. If multiple
       identities are in the cache, then the value of  the environment variable ``AZURE_USERNAME`` is used to select
       which identity to use. See :class:`~azure.identity.aio.SharedTokenCacheCredential` for more details.
    4. The user currently signed in to Visual Studio Code.
    5. The identity currently logged in to the Azure CLI.

    This default behavior is configurable with keyword arguments.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds. Managed identities ignore this because they reside in a single cloud.
    :keyword bool exclude_cli_credential: Whether to exclude the Azure CLI from the credential. Defaults to **False**.
    :keyword bool exclude_environment_credential: Whether to exclude a service principal configured by environment
        variables from the credential. Defaults to **False**.
    :keyword bool exclude_visual_studio_code_credential: Whether to exclude stored credential from VS Code.
        Defaults to **False**.
    :keyword bool exclude_managed_identity_credential: Whether to exclude managed identity from the credential.
        Defaults to **False**.
    :keyword bool exclude_shared_token_cache_credential: Whether to exclude the shared token cache. Defaults to
        **False**.
    :keyword str managed_identity_client_id: The client ID of a user-assigned managed identity. Defaults to the value
        of the environment variable AZURE_CLIENT_ID, if any. If not specified, a system-assigned identity will be used.
    :keyword str shared_cache_username: Preferred username for :class:`~azure.identity.SharedTokenCacheCredential`.
        Defaults to the value of environment variable AZURE_USERNAME, if any.
    :keyword str shared_cache_tenant_id: Preferred tenant for :class:`~azure.identity.SharedTokenCacheCredential`.
        Defaults to the value of environment variable AZURE_TENANT_ID, if any.
    :keyword str visual_studio_code_tenant_id: Tenant ID to use when authenticating with
        :class:`~azure.identity.VisualStudioCodeCredential`.
    """

    def __init__(self, **kwargs: "Any") -> None:
        authority = kwargs.pop("authority", None)
        authority = normalize_authority(authority) if authority else get_default_authority()

        shared_cache_username = kwargs.pop("shared_cache_username", os.environ.get(EnvironmentVariables.AZURE_USERNAME))
        shared_cache_tenant_id = kwargs.pop(
            "shared_cache_tenant_id", os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        )

        managed_identity_client_id = kwargs.pop(
            "managed_identity_client_id", os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)
        )

        vscode_tenant_id = kwargs.pop(
            "visual_studio_code_tenant_id", os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        )

        exclude_visual_studio_code_credential = kwargs.pop("exclude_visual_studio_code_credential", False)
        exclude_cli_credential = kwargs.pop("exclude_cli_credential", False)
        exclude_environment_credential = kwargs.pop("exclude_environment_credential", False)
        exclude_managed_identity_credential = kwargs.pop("exclude_managed_identity_credential", False)
        exclude_shared_token_cache_credential = kwargs.pop("exclude_shared_token_cache_credential", False)

        credentials = []
        if not exclude_environment_credential:
            credentials.append(EnvironmentCredential(authority=authority, **kwargs))
        if not exclude_managed_identity_credential:
            credentials.append(
                ManagedIdentityCredential(client_id=managed_identity_client_id, **kwargs)
            )
        if not exclude_shared_token_cache_credential and SharedTokenCacheCredential.supported():
            try:
                # username and/or tenant_id are only required when the cache contains tokens for multiple identities
                shared_cache = SharedTokenCacheCredential(
                    username=shared_cache_username, tenant_id=shared_cache_tenant_id, authority=authority, **kwargs
                )
                credentials.append(shared_cache)
            except Exception as ex:  # pylint:disable=broad-except
                # transitive dependency pywin32 doesn't support 3.8 (https://github.com/mhammond/pywin32/issues/1431)
                _LOGGER.info("Shared token cache is unavailable: '%s'", ex)
        if not exclude_visual_studio_code_credential:
            credentials.append(VisualStudioCodeCredential(tenant_id=vscode_tenant_id))
        if not exclude_cli_credential:
            credentials.append(AzureCliCredential())

        super().__init__(*credentials)

    async def get_token(self, *scopes: str, **kwargs: "Any"):
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The exception has a
          `message` attribute listing each authentication attempt and its error message.
        """
        if self._successful_credential:
            return await self._successful_credential.get_token(*scopes, **kwargs)

        return await super().get_token(*scopes, **kwargs)
