# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time

from msal.application import PublicClientApplication

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._constants import DEVELOPER_SIGN_ON_CLIENT_ID
from .._internal import AadClient, validate_tenant_id
from .._internal.decorators import log_get_token, wrap_exceptions
from .._internal.msal_client import MsalClient
from .._internal.shared_token_cache import NO_TOKEN, SharedTokenCacheBase

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Optional
    from .._auth_record import AuthenticationRecord
    from .._internal import AadClientBase


class SharedTokenCacheCredential(SharedTokenCacheBase):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is used when the local cache
        contains tokens for multiple identities.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Used to select an account when the cache contains
        tokens for multiple identities.
    """

    def __init__(self, username=None, **kwargs):
        # type: (Optional[str], **Any) -> None

        self._auth_record = kwargs.pop("_authentication_record", None)  # type: Optional[AuthenticationRecord]
        if self._auth_record:
            # authenticate in the tenant that produced the record unless "tenant_id" specifies another
            self._tenant_id = kwargs.pop("tenant_id", None) or self._auth_record.tenant_id
            validate_tenant_id(self._tenant_id)
            self._cache = kwargs.pop("_cache", None)
            self._app = None
            self._client_kwargs = kwargs
            self._initialized = False
        else:
            super(SharedTokenCacheCredential, self).__init__(username=username, **kwargs)

    @log_get_token("SharedTokenCacheCredential")
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type (*str, **Any) -> AccessToken
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the cache is unavailable or contains insufficient user
            information
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        if not self._initialized:
            self._initialize()

        if not self._cache:
            raise CredentialUnavailableError(message="Shared token cache unavailable")

        if self._auth_record:
            return self._acquire_token_silent(*scopes)

        account = self._get_account(self._username, self._tenant_id)

        token = self._get_cached_access_token(scopes, account)
        if token:
            return token

        # try each refresh token, returning the first access token acquired
        for refresh_token in self._get_refresh_tokens(account):
            token = self._client.obtain_token_by_refresh_token(scopes, refresh_token)
            return token

        raise CredentialUnavailableError(message=NO_TOKEN.format(account.get("username")))

    def _get_auth_client(self, **kwargs):
        # type: (**Any) -> AadClientBase
        return AadClient(client_id=DEVELOPER_SIGN_ON_CLIENT_ID, **kwargs)

    def _initialize(self):
        if self._initialized:
            return

        if not self._auth_record:
            super(SharedTokenCacheCredential, self)._initialize()
            return

        self._load_cache()
        if self._cache:
            self._app = PublicClientApplication(
                client_id=self._auth_record.client_id,
                authority="https://{}/{}".format(self._auth_record.authority, self._tenant_id),
                token_cache=self._cache,
                http_client=MsalClient(**self._client_kwargs),
            )

        self._initialized = True

    @wrap_exceptions
    def _acquire_token_silent(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Silently acquire a token from MSAL. Requires an AuthenticationRecord."""

        result = None

        accounts_for_user = self._app.get_accounts(username=self._auth_record.username)
        if not accounts_for_user:
            raise CredentialUnavailableError("The cache contains no account matching the given AuthenticationRecord.")

        for account in accounts_for_user:
            if account.get("home_account_id") != self._auth_record.home_account_id:
                continue

            now = int(time.time())
            result = self._app.acquire_token_silent_with_error(list(scopes), account=account, **kwargs)
            if result and "access_token" in result and "expires_in" in result:
                return AccessToken(result["access_token"], now + int(result["expires_in"]))

        # if we get this far, the cache contained a matching account but MSAL failed to authenticate it silently
        if result:
            # cache contains a matching refresh token but STS returned an error response when MSAL tried to use it
            message = "Token acquisition failed"
            details = result.get("error_description") or result.get("error")
            if details:
                message += ": {}".format(details)
            raise ClientAuthenticationError(message=message)

        # cache doesn't contain a matching refresh (or access) token
        raise CredentialUnavailableError(message=NO_TOKEN.format(self._auth_record.username))
