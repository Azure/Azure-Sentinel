# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import Any, Optional, Callable, Union, Dict

import msal

from azure.core.credentials import AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError

from .certificate import get_client_credential
from .._internal.decorators import wrap_exceptions
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.interactive import _build_auth_record
from .._internal.msal_credentials import MsalCredential
from .. import AuthenticationRecord


class OnBehalfOfCredential(MsalCredential, GetTokenMixin):
    """Authenticates a service principal via the on-behalf-of flow.

    This flow is typically used by middle-tier services that authorize requests to other services with a delegated
    user identity. Because this is not an interactive authentication flow, an application using it must have admin
    consent for any delegated permissions before requesting tokens for them. See `Microsoft Entra ID documentation
    <https://learn.microsoft.com/entra/identity-platform/v2-oauth2-on-behalf-of-flow>`__ for a more detailed
    description of the on-behalf-of flow.

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: The service principal's client ID.
    :keyword str client_secret: Optional. A client secret to authenticate the service principal.
        One of **client_secret**, **client_certificate**, or **client_assertion_func** must be provided.
    :keyword bytes client_certificate: Optional. The bytes of a certificate in PEM or PKCS12 format including
        the private key to authenticate the service principal. One of **client_secret**, **client_certificate**,
        or **client_assertion_func** must be provided.
    :keyword client_assertion_func: Optional. Function that returns client assertions that authenticate the
        application to Microsoft Entra ID. This function is called each time the credential requests a token. It must
        return a valid assertion for the target resource.
    :paramtype client_assertion_func: Callable[[], str]
    :keyword str user_assertion: Required. The access token the credential will use as the user assertion when
        requesting on-behalf-of tokens.

    :keyword str authority: Authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword password: A certificate password. Used only when **client_certificate** is provided. If this value
        is a unicode string, it will be encoded as UTF-8. If the certificate requires a different encoding, pass
        appropriately encoded bytes instead.
    :paramtype password: str or bytes
    :keyword bool send_certificate_chain: If True when **client_certificate** is provided, the credential will send
        the public certificate chain in the x5c header of each token request's JWT. This is required for Subject
        Name/Issuer (SNI) authentication. Defaults to False.
    :keyword bool disable_instance_discovery: Determines whether or not instance discovery is performed when attempting
        to authenticate. Setting this to true will completely disable both instance discovery and authority validation.
        This functionality is intended for use in scenarios where the metadata endpoint cannot be reached, such as in
        private clouds or Azure Stack. The process of instance discovery entails retrieving authority metadata from
        https://login.microsoft.com/ to validate the authority. By setting this to **True**, the validation of the
        authority is disabled. As a result, it is crucial to ensure that the configured authority host is valid and
        trustworthy.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_on_behalf_of_credential]
            :end-before: [END create_on_behalf_of_credential]
            :language: python
            :dedent: 4
            :caption: Create an OnBehalfOfCredential.
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        *,
        client_certificate: Optional[bytes] = None,
        client_secret: Optional[str] = None,
        client_assertion_func: Optional[Callable[[], str]] = None,
        user_assertion: str,
        password: Optional[Union[bytes, str]] = None,
        send_certificate_chain: bool = False,
        **kwargs: Any
    ) -> None:
        self._assertion = user_assertion
        if not self._assertion:
            raise TypeError('"user_assertion" must not be empty.')

        if client_assertion_func:
            if client_certificate or client_secret:
                raise ValueError(
                    "It is invalid to specify more than one of the following: "
                    '"client_assertion_func", "client_certificate" or "client_secret".'
                )
            credential: Union[str, Dict[str, Any]] = {
                "client_assertion": client_assertion_func,
            }
        elif client_certificate:
            if client_secret:
                raise ValueError('Specifying both "client_certificate" and "client_secret" is not valid.')
            try:
                credential = get_client_credential(
                    certificate_path=None,
                    password=password,
                    certificate_data=client_certificate,
                    send_certificate_chain=send_certificate_chain,
                )
            except ValueError as ex:
                # client_certificate isn't a valid cert.
                message = '"client_certificate" is not a valid certificate in PEM or PKCS12 format'
                raise ValueError(message) from ex
        elif client_secret:
            credential = client_secret
        else:
            raise TypeError('Either "client_certificate", "client_secret", or "client_assertion_func" must be provided')

        super(OnBehalfOfCredential, self).__init__(
            client_id=client_id, client_credential=credential, tenant_id=tenant_id, **kwargs
        )
        self._auth_record: Optional[AuthenticationRecord] = None

    @wrap_exceptions
    def _acquire_token_silently(self, *scopes: str, **kwargs: Any) -> Optional[AccessTokenInfo]:
        if self._auth_record:
            claims = kwargs.get("claims")
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

        return None

    @wrap_exceptions
    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:
        app: msal.ConfidentialClientApplication = self._get_app(**kwargs)
        request_time = int(time.time())
        result = app.acquire_token_on_behalf_of(self._assertion, list(scopes), claims_challenge=kwargs.get("claims"))
        if "access_token" not in result or "expires_in" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            response = self._client.get_error_response(result)
            raise ClientAuthenticationError(message=message, response=response)

        try:
            self._auth_record = _build_auth_record(result)
        except ClientAuthenticationError:
            pass  # non-fatal; we'll use the assertion again next time instead of a refresh token

        refresh_on = int(result["refresh_on"]) if "refresh_on" in result else None
        return AccessTokenInfo(
            result["access_token"],
            request_time + int(result["expires_in"]),
            token_type=result.get("token_type", "Bearer"),
            refresh_on=refresh_on,
        )
