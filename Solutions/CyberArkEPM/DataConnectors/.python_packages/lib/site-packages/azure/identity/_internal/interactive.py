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
from typing import Any, Optional, Iterable, Dict
from urllib.parse import urlparse

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.exceptions import ClientAuthenticationError

from .msal_credentials import MsalCredential
from .._auth_record import AuthenticationRecord
from .._constants import KnownAuthorities
from .._exceptions import AuthenticationRequiredError, CredentialUnavailableError
from .._internal import wrap_exceptions

ABC = abc.ABC

_LOGGER = logging.getLogger(__name__)

_DEFAULT_AUTHENTICATE_SCOPES = {
    "https://" + KnownAuthorities.AZURE_CHINA: ("https://management.core.chinacloudapi.cn//.default",),
    "https://" + KnownAuthorities.AZURE_GOVERNMENT: ("https://management.core.usgovcloudapi.net//.default",),
    "https://" + KnownAuthorities.AZURE_PUBLIC_CLOUD: ("https://management.core.windows.net//.default",),
}


def _decode_client_info(raw) -> str:
    """Decode client info. Taken from msal.oauth2cli.oidc.

    :param str raw: base64-encoded client info
    :return: decoded client info
    :rtype: str
    """

    raw += "=" * (-len(raw) % 4)
    raw = str(raw)  # On Python 2.7, argument of urlsafe_b64decode must be str, not unicode.
    return base64.urlsafe_b64decode(raw).decode("utf-8")


def _build_auth_record(response):
    """Build an AuthenticationRecord from the result of an MSAL ClientApplication token request.

    :param response: The result of a token request
    :type response: dict[str, typing.Any]
    :return: An AuthenticationRecord
    :rtype: ~azure.identity.AuthenticationRecord
    :raises ~azure.core.exceptions.ClientAuthenticationError: If the response doesn't contain expected data
    """

    try:
        id_token = response["id_token_claims"]

        if "client_info" in response:
            client_info = json.loads(_decode_client_info(response["client_info"]))
            home_account_id = "{uid}.{utid}".format(**client_info)
        else:
            # MSAL uses the subject claim as home_account_id when the STS doesn't provide client_info
            home_account_id = id_token["sub"]

        # "iss" is the URL of the issuing tenant e.g. https://authority/tenant
        issuer = urlparse(id_token["iss"])

        # tenant which issued the token, not necessarily user's home tenant
        tenant_id = id_token.get("tid") or issuer.path.strip("/")

        # Microsoft Entra ID returns "preferred_username", ADFS returns "upn"
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
        raise auth_error from ex


class InteractiveCredential(MsalCredential, ABC):
    def __init__(
        self,
        *,
        authentication_record: Optional[AuthenticationRecord] = None,
        disable_automatic_authentication: bool = False,
        **kwargs: Any,
    ) -> None:
        self._disable_automatic_authentication = disable_automatic_authentication
        self._auth_record = authentication_record
        if self._auth_record:
            kwargs.pop("client_id", None)  # authentication_record overrides client_id argument
            tenant_id = kwargs.pop("tenant_id", None) or self._auth_record.tenant_id
            super(InteractiveCredential, self).__init__(
                client_id=self._auth_record.client_id,
                authority=self._auth_record.authority,
                tenant_id=tenant_id,
                **kwargs,
            )
        else:
            super(InteractiveCredential, self).__init__(**kwargs)

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.
        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        :raises AuthenticationRequiredError: user interaction is necessary to acquire a token, and the credential is
            configured not to begin this automatically. Call :func:`authenticate` to begin interactive authentication.
        """
        options: TokenRequestOptions = {}
        if claims:
            options["claims"] = claims
        if tenant_id:
            options["tenant_id"] = tenant_id
        options["enable_cae"] = enable_cae

        token_info = self._get_token_base(*scopes, options=options, base_method_name="get_token", **kwargs)
        return AccessToken(token_info.token, token_info.expires_on)

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.

        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        :raises AuthenticationRequiredError: user interaction is necessary to acquire a token, and the credential is
            configured not to begin this automatically. Call :func:`authenticate` to begin interactive authentication.
        """
        return self._get_token_base(*scopes, options=options, base_method_name="get_token_info")

    def _get_token_base(
        self,
        *scopes: str,
        options: Optional[TokenRequestOptions] = None,
        base_method_name: str = "get_token_info",
        **kwargs: Any,
    ) -> AccessTokenInfo:
        if not scopes:
            message = f"'{base_method_name}' requires at least one scope"
            _LOGGER.warning("%s.%s failed: %s", self.__class__.__name__, base_method_name, message)
            raise ValueError(message)

        allow_prompt = kwargs.pop("_allow_prompt", not self._disable_automatic_authentication)
        options = options or {}
        claims = options.get("claims")
        tenant_id = options.get("tenant_id")
        enable_cae = options.get("enable_cae", False)

        # Check for arbitrary additional options to enable intermediary support for PoP tokens.
        for key in options:
            if key not in TokenRequestOptions.__annotations__:  # pylint:disable=no-member
                kwargs.setdefault(key, options[key])  # type: ignore

        try:
            token = self._acquire_token_silent(
                *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
            )
            _LOGGER.info("%s.%s succeeded", self.__class__.__name__, base_method_name)
            return token
        except Exception as ex:  # pylint:disable=broad-except
            if not (isinstance(ex, AuthenticationRequiredError) and allow_prompt):
                _LOGGER.warning(  # pylint: disable=do-not-log-raised-errors
                    "%s.%s failed: %s",
                    self.__class__.__name__,
                    base_method_name,
                    ex,
                    exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                )
                raise

        # silent authentication failed -> authenticate interactively
        now = int(time.time())

        try:
            result = self._request_token(*scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs)
            if "access_token" not in result:
                message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
                response = self._client.get_error_response(result)
                raise ClientAuthenticationError(message=message, response=response)

            # this may be the first authentication, or the user may have authenticated a different identity
            self._auth_record = _build_auth_record(result)
        except Exception as ex:
            _LOGGER.warning(  # pylint: disable=do-not-log-raised-errors
                "%s.%s failed: %s",
                self.__class__.__name__,
                base_method_name,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

        _LOGGER.info("%s.%s succeeded", self.__class__.__name__, base_method_name)
        refresh_on = int(result["refresh_on"]) if "refresh_on" in result else None
        return AccessTokenInfo(
            result["access_token"],
            now + int(result["expires_in"]),
            token_type=result.get("token_type", "Bearer"),
            refresh_on=refresh_on,
        )

    def authenticate(
        self,
        *,
        scopes: Optional[Iterable[str]] = None,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AuthenticationRecord:
        """Interactively authenticate a user. This method will always generate a challenge to the user.

        :keyword Iterable[str] scopes: scopes to request during authentication, such as those provided by
          :func:`AuthenticationRequiredError.scopes`. If provided, successful authentication will cache an access token
          for these scopes.
        :keyword str claims: additional claims required in the token, such as those provided by
          :func:`AuthenticationRequiredError.claims`
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Access tokens retrieved with CAE enabled will be cached separately from other tokens.
            Defaults to False.
        :return: An AuthenticationRecord containing the authenticated user's information.
        :rtype: ~azure.identity.AuthenticationRecord
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason.
        """

        if not scopes:
            if self._authority not in _DEFAULT_AUTHENTICATE_SCOPES:
                # the credential is configured to use a cloud whose ARM scope we can't determine
                raise CredentialUnavailableError(
                    message="Authenticating in this environment requires a value for the 'scopes' keyword argument."
                )

            scopes = _DEFAULT_AUTHENTICATE_SCOPES[self._authority]

        _ = self.get_token(
            *scopes, _allow_prompt=True, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
        )
        return self._auth_record  # type: ignore

    @wrap_exceptions
    def _acquire_token_silent(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:
        result = None
        claims = kwargs.get("claims")
        if self._auth_record:
            app = self._get_app(**kwargs)
            for account in app.get_accounts(username=self._auth_record.username):
                if account.get("home_account_id") != self._auth_record.home_account_id:
                    continue

                now = int(time.time())
                result = app.acquire_token_silent_with_error(list(scopes), account=account, claims_challenge=claims)
                if result and "access_token" in result and "expires_in" in result:
                    refresh_on = int(result["refresh_on"]) if "refresh_on" in result else None
                    return AccessTokenInfo(
                        result["access_token"],
                        now + int(result["expires_in"]),
                        token_type=result.get("token_type", "Bearer"),
                        refresh_on=refresh_on,
                    )

        # if we get this far, result is either None or the content of a Microsoft Entra ID error response
        if result:
            response = self._client.get_error_response(result)
            raise AuthenticationRequiredError(scopes, claims=claims, response=response)
        raise AuthenticationRequiredError(scopes, claims=claims)

    @abc.abstractmethod
    def _request_token(self, *scopes, **kwargs) -> Dict:
        pass
