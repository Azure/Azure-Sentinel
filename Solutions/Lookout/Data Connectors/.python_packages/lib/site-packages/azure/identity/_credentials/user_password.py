# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .._internal import InteractiveCredential, wrap_exceptions

if TYPE_CHECKING:
    from typing import Any


class UsernamePasswordCredential(InteractiveCredential):
    """Authenticates a user with a username and password.

    In general, Microsoft doesn't recommend this kind of authentication, because it's less secure than other
    authentication flows.

    Authentication with this credential is not interactive, so it is **not compatible with any form of
    multi-factor authentication or consent prompting**. The application must already have consent from the user or
    a directory admin.

    This credential can only authenticate work and school accounts; Microsoft accounts are not supported.
    See this document for more information about account types:
    https://docs.microsoft.com/azure/active-directory/fundamentals/sign-up-organization

    :param str client_id: the application's client ID
    :param str username: the user's username (usually an email address)
    :param str password: the user's password

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword str tenant_id: tenant ID or a domain associated with a tenant. If not provided, defaults to the
          'organizations' tenant, which supports only Azure Active Directory work or school accounts.
    """

    def __init__(self, client_id, username, password, **kwargs):
        # type: (str, str, str, Any) -> None

        # The base class will accept an AuthenticationRecord, allowing this credential to authenticate silently the
        # first time it's asked for a token. However, we want to ensure this first authentication is not silent, to
        # validate the given password. This class therefore doesn't document the authentication_record argument, and we
        # discard it here.
        kwargs.pop("_authentication_record", None)
        super(UsernamePasswordCredential, self).__init__(client_id=client_id, **kwargs)
        self._username = username
        self._password = password

    @wrap_exceptions
    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> dict
        app = self._get_app()
        return app.acquire_token_by_username_password(
            username=self._username, password=self._password, scopes=list(scopes)
        )
