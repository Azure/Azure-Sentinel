# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Base class for credentials using MSAL for interactive user authentication"""

import abc
import base64
import json
import logging
import time
from typing import TYPE_CHECKING

import msal
import six
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .msal_credentials import MsalCredential
from .._auth_record import AuthenticationRecord
from .._constants import KnownAuthorities
from .._exceptions import AuthenticationRequiredError, CredentialUnavailableError
from .._internal import wrap_exceptions

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports,unused-import
    from typing import Any, Optional

_LOGGER = logging.getLogger(__name__)

_DEFAULT_AUTHENTICATE_SCOPES = {
    "https://" + KnownAuthorities.AZURE_CHINA: ("https://management.core.chinacloudapi.cn//.default",),
    "https://" + KnownAuthorities.AZURE_GERMANY: ("https://management.core.cloudapi.de//.default",),
    "https://" + KnownAuthorities.AZURE_GOVERNMENT: ("https://management.core.usgovcloudapi.net//.default",),
    "https://" + KnownAuthorities.AZURE_PUBLIC_CLOUD: ("https://management.core.windows.net//.default",),
}


def _decode_client_info(raw):
    """Taken from msal.oauth2cli.oidc"""

    raw += "=" * (-len(raw) % 4)
    raw = str(raw)  # On Python 2.7, argument of urlsafe_b64decode must be str, not unicode.
    return base64.urlsafe_b64decode(raw).decode("utf-8")


def _build_auth_record(response):
    """Build an AuthenticationRecord from the result of an MSAL ClientApplication token request"""

    try:
        id_token = response["id_token_claims"]

        if "client_info" in response:
            client_info = json.loads(_decode_client_info(response["client_info"]))
            home_account_id = "{uid}.{utid}".format(**client_info)
        else:
            # MSAL uses the subject claim as home_account_id when the STS doesn't provide client_info
            home_account_id = id_token["sub"]

        # "iss" is the URL of the issuing tenant e.g. https://authority/tenant
        issuer = six.moves.urllib_parse.urlparse(id_token["iss"])

        # tenant which issued the token, not necessarily user's home tenant
        tenant_id = id_token.get("tid") or issuer.path.strip("/")

        # AAD returns "preferred_username", ADFS returns "upn"
        username = id_token.get("preferred_username") or id_token["upn"]

        return AuthenticationRecord(
            authority=issuer.netloc,
            client_id=id_token["aud"],
            home_account_id=home_account_id,
            tenant_id=tenant_id,
            username=username,
        )
    except (KeyError, ValueError) as ex:
        auth_error = ClientAuthenticationError(
            message="Failed to build AuthenticationRecord from unexpected identity token"
        )
        six.raise_from(auth_error, ex)


class InteractiveCredential(MsalCredential):
    def __init__(self, **kwargs):
        self._disable_automatic_authentication = kwargs.pop("_disable_automatic_authentication", False)
        self._auth_record = kwargs.pop("_authentication_record", None)  # type: Optional[AuthenticationRecord]
        if self._auth_record:
            kwargs.pop("client_id", None)  # authentication_record overrides client_id argument
            tenant_id = kwargs.pop("tenant_id", None) or self._auth_record.tenant_id
            super(InteractiveCredential, self).__init__(
                client_id=self._auth_record.client_id,
                authority=self._auth_record.authority,
                tenant_id=tenant_id,
                **kwargs
            )
        else:
            super(InteractiveCredential, self).__init__(**kwargs)

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
          required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason.
        """
        if not scopes:
            message = "'get_token' requires at least one scope"
            _LOGGER.warning("%s.get_token failed: %s", self.__class__.__name__, message)
            raise ValueError(message)

        allow_prompt = kwargs.pop("_allow_prompt", not self._disable_automatic_authentication)
        try:
            token = self._acquire_token_silent(*scopes, **kwargs)
            _LOGGER.info("%s.get_token succeeded", self.__class__.__name__)
            return token
        except Exception as ex:  # pylint:disable=broad-except
            if not (isinstance(ex, AuthenticationRequiredError) and allow_prompt):
                _LOGGER.warning(
                    "%s.get_token failed: %s",
                    self.__class__.__name__,
                    ex,
                    exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                )
                raise

        # silent authentication failed -> authenticate interactively
        now = int(time.time())

        try:
            result = self._request_token(*scopes, **kwargs)
            if "access_token" not in result:
                message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
                raise ClientAuthenticationError(message=message)

            # this may be the first authentication, or the user may have authenticated a different identity
            self._auth_record = _build_auth_record(result)
        except Exception as ex:  # pylint:disable=broad-except
            _LOGGER.warning(
                "%s.get_token failed: %s", self.__class__.__name__, ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

        _LOGGER.info("%s.get_token succeeded", self.__class__.__name__)
        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    def _authenticate(self, **kwargs):
        # type: (**Any) -> AuthenticationRecord
        """Interactively authenticate a user.

        :keyword Iterable[str] scopes: scopes to request during authentication, such as those provided by
          :func:`AuthenticationRequiredError.scopes`. If provided, successful authentication will cache an access token
          for these scopes.
        :rtype: ~azure.identity.AuthenticationRecord
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason.
        """

        scopes = kwargs.pop("scopes", None)
        if not scopes:
            if self._authority not in _DEFAULT_AUTHENTICATE_SCOPES:
                # the credential is configured to use a cloud whose ARM scope we can't determine
                raise CredentialUnavailableError(
                    message="Authenticating in this environment requires a value for the 'scopes' keyword argument."
                )

            scopes = _DEFAULT_AUTHENTICATE_SCOPES[self._authority]

        _ = self.get_token(*scopes, _allow_prompt=True, **kwargs)
        return self._auth_record  # type: ignore

    @wrap_exceptions
    def _acquire_token_silent(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        result = None
        if self._auth_record:
            app = self._get_app()
            for account in app.get_accounts(username=self._auth_record.username):
                if account.get("home_account_id") != self._auth_record.home_account_id:
                    continue

                now = int(time.time())
                result = app.acquire_token_silent_with_error(list(scopes), account=account, **kwargs)
                if result and "access_token" in result and "expires_in" in result:
                    return AccessToken(result["access_token"], now + int(result["expires_in"]))

        # if we get this far, result is either None or the content of an AAD error response
        if result:
            details = result.get("error_description") or result.get("error")
            raise AuthenticationRequiredError(scopes, error_details=details)
        raise AuthenticationRequiredError(scopes)

    def _get_app(self):
        # type: () -> msal.PublicClientApplication
        if not self._msal_app:
            self._msal_app = self._create_app(msal.PublicClientApplication)
        return self._msal_app

    @abc.abstractmethod
    def _request_token(self, *scopes, **kwargs):
        pass
