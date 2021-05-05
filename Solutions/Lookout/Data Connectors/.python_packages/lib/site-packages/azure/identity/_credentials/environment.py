# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os


from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal.decorators import log_get_token
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential
from .user_password import UsernamePasswordCredential


try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Mapping, Optional, Union
    from azure.core.credentials import AccessToken

    EnvironmentCredentialTypes = Union["CertificateCredential", "ClientSecretCredential", "UsernamePasswordCredential"]

_LOGGER = logging.getLogger(__name__)


class EnvironmentCredential(object):
    """A credential configured by environment variables.

    This credential is capable of authenticating as a service principal using a client secret or a certificate, or as
    a user with a username and password. Configuration is attempted in this order, using these environment variables:

    Service principal with secret:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_SECRET**: one of the service principal's client secrets

    Service principal with certificate:
      - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
      - **AZURE_CLIENT_ID**: the service principal's client ID
      - **AZURE_CLIENT_CERTIFICATE_PATH**: path to a PEM-encoded certificate file including the private key. The
        certificate must not be password-protected.

    User with username and password:
      - **AZURE_CLIENT_ID**: the application's client ID
      - **AZURE_USERNAME**: a username (usually an email address)
      - **AZURE_PASSWORD**: that user's password
      - **AZURE_TENANT_ID**: (optional) ID of the service principal's tenant. Also called its 'directory' ID.
        If not provided, defaults to the 'organizations' tenant, which supports only Azure Active Directory work or
        school accounts.
    """

    def __init__(self, **kwargs):
        # type: (Mapping[str, Any]) -> None
        self._credential = None  # type: Optional[EnvironmentCredentialTypes]

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
                **kwargs
            )
        elif all(os.environ.get(v) is not None for v in EnvironmentVariables.USERNAME_PASSWORD_VARS):
            self._credential = UsernamePasswordCredential(
                client_id=os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
                username=os.environ[EnvironmentVariables.AZURE_USERNAME],
                password=os.environ[EnvironmentVariables.AZURE_PASSWORD],
                tenant_id=os.environ.get(EnvironmentVariables.AZURE_TENANT_ID),  # optional for username/password auth
                **kwargs
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
                _LOGGER.warning("Incomplete environment configuration. Set variables: %s", ", ".join(set_variables))
            else:
                _LOGGER.info("No environment configuration found.")

    @log_get_token("EnvironmentCredential")
    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: environment variable configuration is incomplete
        """
        if not self._credential:
            message = (
                "EnvironmentCredential authentication unavailable. Environment variables are not fully configured."
            )
            raise CredentialUnavailableError(message=message)
        return self._credential.get_token(*scopes, **kwargs)
