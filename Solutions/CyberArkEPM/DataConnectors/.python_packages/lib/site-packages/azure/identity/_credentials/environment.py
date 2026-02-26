# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import Optional, Union, Any, cast
import warnings
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions, SupportsTokenInfo

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal import within_dac
from .._internal.decorators import log_get_token
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential
from .user_password import UsernamePasswordCredential

EnvironmentCredentialTypes = Union[CertificateCredential, ClientSecretCredential, UsernamePasswordCredential]

_LOGGER = logging.getLogger(__name__)


class EnvironmentCredential:
    """A credential configured by environment variables.

    This credential is capable of authenticating as a service principal using a client secret or a certificate.
    Configuration is attempted in this order, using these environment variables:

    Service principal with secret:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_SECRET**: one of the service principal's client secrets
      - **AZURE_AUTHORITY_HOST**: authority of a Microsoft Entra endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default
        when no value is given.

    Service principal with certificate:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_CERTIFICATE_PATH**: path to a PEM or PKCS12 certificate file including the private key.
      - **AZURE_CLIENT_CERTIFICATE_PASSWORD**: (optional) password of the certificate file, if any.
      - **AZURE_CLIENT_SEND_CERTIFICATE_CHAIN**: (optional) If True, the credential will send the public certificate
        chain in the x5c header of each token request's JWT. This is required for Subject Name/Issuer (SNI)
        authentication. Defaults to False.
      - **AZURE_AUTHORITY_HOST**: authority of a Microsoft Entra endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud, which is the default
        when no value is given.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_environment_credential]
            :end-before: [END create_environment_credential]
            :language: python
            :dedent: 4
            :caption: Create an EnvironmentCredential.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._credential: Optional[EnvironmentCredentialTypes] = None

        if all(os.environ.get(v) is not None for v in EnvironmentVariables.CLIENT_SECRET_VARS):
            self._credential = ClientSecretCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                client_secret=os.environ[EnvironmentVariables.AZURE_CLIENT_SECRET],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                **kwargs
            )
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.CERT_VARS):
            self._credential = CertificateCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                tenant_id=os.environ[EnvironmentVariables.AZURE_TENANT_ID],
                certificate_path=os.environ[EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH],
                password=os.environ.get(EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PASSWORD),
                send_certificate_chain=bool(
                    os.environ.get(EnvironmentVariables.AZURE_CLIENT_SEND_CERTIFICATE_CHAIN, False)
                ),
                **kwargs
            )
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.USERNAME_PASSWORD_VARS):
            self._credential = UsernamePasswordCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                username=os.environ[EnvironmentVariables.AZURE_USERNAME],
                password=os.environ[EnvironmentVariables.AZURE_PASSWORD],
                tenant_id=os.environ.get(EnvironmentVariables.AZURE_TENANT_ID),  # optional for username/password auth
                _silence_deprecation_warning=True,  # avoid duplicate warning
                **kwargs
            )
            warnings.warn(
                "Environment is configured to use username and password authentication. "
                "This authentication method is deprecated, as it doesn't support multifactor authentication (MFA). "
                "For more details, see https://aka.ms/azsdk/identity/mfa.",
                DeprecationWarning,
                stacklevel=3 if within_dac.get() else 2,
            )

        if self._credential:
            _LOGGER.info("Environment is configured for %s", self._credential.__class__.__name__)
        else:
            expected_variables = set(
                EnvironmentVariables.CERT_VARS
                + EnvironmentVariables.CLIENT_SECRET_VARS
                + EnvironmentVariables.USERNAME_PASSWORD_VARS
            )
            set_variables = [v for v in expected_variables if v in os.environ]
            if set_variables:
                _LOGGER.log(
                    logging.INFO if kwargs.get("_within_dac") else logging.WARNING,
                    "Incomplete environment configuration for EnvironmentCredential. These variables are set: %s",
                    ", ".join(set_variables),
                )
            else:
                _LOGGER.info("No environment configuration found.")

    def __enter__(self) -> "EnvironmentCredential":
        if self._credential:
            self._credential.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._credential:
            self._credential.__exit__(*args)

    def close(self) -> None:
        """Close the credential's transport session."""
        self.__exit__()

    @log_get_token
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken

        :raises ~azure.identity.CredentialUnavailableError: environment variable configuration is incomplete
        """
        if not self._credential:
            message = (
                "EnvironmentCredential authentication unavailable. Environment variables are not fully configured.\n"
                "Visit https://aka.ms/azsdk/python/identity/environmentcredential/troubleshoot to troubleshoot "
                "this issue."
            )
            raise CredentialUnavailableError(message=message)
        return self._credential.get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    @log_get_token
    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes`.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.

        :raises ~azure.identity.CredentialUnavailableError: environment variable configuration is incomplete.
        """
        if not self._credential:
            message = (
                "EnvironmentCredential authentication unavailable. Environment variables are not fully configured.\n"
                "Visit https://aka.ms/azsdk/python/identity/environmentcredential/troubleshoot to troubleshoot "
                "this issue."
            )
            raise CredentialUnavailableError(message=message)
        return cast(SupportsTokenInfo, self._credential).get_token_info(*scopes, options=options)
