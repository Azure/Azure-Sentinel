# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from typing import TYPE_CHECKING

from .._internal.decorators import log_get_token_async

from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from .._internal import AsyncContextManager
from .certificate import CertificateCredential
from .client_secret import ClientSecretCredential

if TYPE_CHECKING:
    from typing import Any, Optional, Union
    from azure.core.credentials import AccessToken

_LOGGER = logging.getLogger(__name__)


class EnvironmentCredential(AsyncContextManager):
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
    """

    def __init__(self, **kwargs: "Any") -> None:
        self._credential = None  # type: Optional[Union[CertificateCredential, ClientSecretCredential]]

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

        if self._credential:
            _LOGGER.info("Environment is configured for %s", self._credential.__class__.__name__)
        else:
            expected_variables = set(EnvironmentVariables.CERT_VARS + EnvironmentVariables.CLIENT_SECRET_VARS)
            set_variables = [v for v in expected_variables if v in os.environ]
            if set_variables:
                _LOGGER.warning("Incomplete environment configuration. Set variables: %s", ", ".join(set_variables))
            else:
                _LOGGER.info("No environment configuration found.")

    async def __aenter__(self):
        if self._credential:
            await self._credential.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._credential:
            await self._credential.__aexit__()

    @log_get_token_async
    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        """Asynchronously request an access token for `scopes`.

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
        return await self._credential.get_token(*scopes, **kwargs)
