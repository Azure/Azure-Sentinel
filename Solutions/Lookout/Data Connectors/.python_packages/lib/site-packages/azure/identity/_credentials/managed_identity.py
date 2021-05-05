# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os

import six
from azure.core.configuration import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    RetryPolicy,
    UserAgentPolicy,
)

from .. import CredentialUnavailableError
from .._authn_client import AuthnClient
from .._constants import Endpoints, EnvironmentVariables
from .._internal.decorators import log_get_token
from .._internal.user_agent import USER_AGENT

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Type

_LOGGER = logging.getLogger(__name__)


class ManagedIdentityCredential(object):
    """Authenticates with an Azure managed identity in any hosting environment which supports managed identities.

    This credential defaults to using a system-assigned identity. To configure a user-assigned identity, use one of
    the keyword arguments.

    :keyword str client_id: a user-assigned identity's client ID. This is supported in all hosting environments.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._credential = None
        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            if os.environ.get(EnvironmentVariables.MSI_SECRET):
                _LOGGER.info("%s will use App Service managed identity", self.__class__.__name__)
                from .app_service import AppServiceCredential

                self._credential = AppServiceCredential(**kwargs)
            else:
                _LOGGER.info("%s will use MSI", self.__class__.__name__)
                self._credential = MsiCredential(**kwargs)
        elif os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT):
            if (
                os.environ.get(EnvironmentVariables.IDENTITY_HEADER)
                and os.environ.get(EnvironmentVariables.IDENTITY_SERVER_THUMBPRINT)
            ):
                _LOGGER.info("%s will use Service Fabric managed identity", self.__class__.__name__)
                from .service_fabric import ServiceFabricCredential

                self._credential = ServiceFabricCredential(**kwargs)
            elif os.environ.get(EnvironmentVariables.IMDS_ENDPOINT):
                _LOGGER.info("%s will use Azure Arc managed identity", self.__class__.__name__)
                from .azure_arc import AzureArcCredential

                self._credential = AzureArcCredential(**kwargs)
        else:
            _LOGGER.info("%s will use IMDS", self.__class__.__name__)
            self._credential = ImdsCredential(**kwargs)

    @log_get_token("ManagedIdentityCredential")
    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: managed identity isn't available in the hosting environment
        """

        if not self._credential:
            raise CredentialUnavailableError(message="No managed identity endpoint found.")
        return self._credential.get_token(*scopes, **kwargs)


class _ManagedIdentityBase(object):
    def __init__(self, endpoint, client_cls, config=None, client_id=None, **kwargs):
        # type: (str, Type, Optional[Configuration], Optional[str], **Any) -> None
        self._identity_config = kwargs.pop("_identity_config", None) or {}
        if client_id:
            if os.environ.get(EnvironmentVariables.MSI_ENDPOINT) and os.environ.get(EnvironmentVariables.MSI_SECRET):
                # App Service: version 2017-09-1 accepts client ID as parameter "clientid"
                if "clientid" not in self._identity_config:
                    self._identity_config["clientid"] = client_id
            elif "client_id" not in self._identity_config:
                self._identity_config["client_id"] = client_id

        config = config or self._create_config(**kwargs)
        policies = [
            ContentDecodePolicy(),
            config.headers_policy,
            config.user_agent_policy,
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        self._client = client_cls(endpoint=endpoint, config=config, policies=policies, **kwargs)

    @staticmethod
    def _create_config(**kwargs):
        # type: (**Any) -> Configuration
        """Build a default configuration for the credential's HTTP pipeline."""

        timeout = kwargs.pop("connection_timeout", 2)
        config = Configuration(connection_timeout=timeout, **kwargs)

        # retry is the only IO policy, so its class is a kwarg to increase async code sharing
        retry_policy = kwargs.pop("retry_policy", RetryPolicy)  # type: ignore
        args = kwargs.copy()  # combine kwargs and default retry settings in a Python 2-compatible way
        args.update(_ManagedIdentityBase._retry_settings)  # type: ignore
        config.retry_policy = retry_policy(**args)  # type: ignore

        # Metadata header is required by IMDS and in Cloud Shell; App Service ignores it
        config.headers_policy = HeadersPolicy(base_headers={"Metadata": "true"}, **kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)

        return config

    # given RetryPolicy's implementation, these settings most closely match the documented guidance for IMDS
    # https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#retry-guidance
    _retry_settings = {
        "retry_total": 5,
        "retry_status": 5,
        "retry_backoff_factor": 4,
        "retry_backoff_max": 60,
        "retry_on_status_codes": [404, 429] + list(range(500, 600)),
    }


class ImdsCredential(_ManagedIdentityBase):
    """Authenticates with a managed identity via the IMDS endpoint.

    :keyword str client_id: ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        super(ImdsCredential, self).__init__(endpoint=Endpoints.IMDS, client_cls=AuthnClient, **kwargs)
        self._endpoint_available = None  # type: Optional[bool]

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the IMDS endpoint is unreachable
        """
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (missing a required header),
            # setting a short timeout.
            try:
                self._client.request_token(scopes, method="GET", connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError:
                # received a response, choked on it
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False
                _LOGGER.info("No response from the IMDS endpoint.")

        if not self._endpoint_available:
            message = "ManagedIdentityCredential authentication unavailable, no managed identity endpoint found."
            raise CredentialUnavailableError(message=message)

        if len(scopes) != 1:
            raise ValueError("This credential requires exactly one scope per token request.")

        token = self._client.get_cached_token(scopes)
        if not token:
            token = self._refresh_token(*scopes)
        elif self._client.should_refresh(token):
            try:
                token = self._refresh_token(*scopes)
            except Exception:  # pylint: disable=broad-except
                pass

        return token

    def _refresh_token(self, *scopes):
        resource = scopes[0]
        if resource.endswith("/.default"):
            resource = resource[: -len("/.default")]
        params = dict({"api-version": "2018-02-01", "resource": resource}, **self._identity_config)

        try:
            token = self._client.request_token(scopes, method="GET", params=params)
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                self._endpoint_available = False
                message = "ManagedIdentityCredential authentication unavailable. "
                if self._identity_config:
                    message += "The requested identity has not been assigned to this resource."
                else:
                    message += "No identity has been assigned to this resource."
                six.raise_from(CredentialUnavailableError(message=message), ex)

            # any other error is unexpected
            six.raise_from(ClientAuthenticationError(message=ex.message, response=ex.response), None)
        return token


class MsiCredential(_ManagedIdentityBase):
    """Authenticates via the MSI endpoint in an App Service or Cloud Shell environment.

    :keyword str client_id: ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __init__(self, **kwargs):
        # type: (**Any) -> None
        self._endpoint = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        if self._endpoint:
            super(MsiCredential, self).__init__(endpoint=self._endpoint, client_cls=AuthnClient, **kwargs)

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This credential allows only one scope per request.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the MSI endpoint is unavailable
        """

        if not self._endpoint:
            message = "ManagedIdentityCredential authentication unavailable, no managed identity endpoint found."
            raise CredentialUnavailableError(message=message)

        if len(scopes) != 1:
            raise ValueError("This credential requires exactly one scope per token request.")

        token = self._client.get_cached_token(scopes)
        if not token:
            token = self._refresh_token(*scopes)
        elif self._client.should_refresh(token):
            try:
                token = self._refresh_token(*scopes)
            except Exception:  # pylint: disable=broad-except
                pass
        return token

    def _refresh_token(self, *scopes):
        resource = scopes[0]
        if resource.endswith("/.default"):
            resource = resource[: -len("/.default")]
        secret = os.environ.get(EnvironmentVariables.MSI_SECRET)
        if secret:
            # MSI_ENDPOINT and MSI_SECRET set -> App Service
            token = self._request_app_service_token(scopes=scopes, resource=resource, secret=secret)
        else:
            # only MSI_ENDPOINT set -> legacy-style MSI (Cloud Shell)
            token = self._request_legacy_token(scopes=scopes, resource=resource)
        return token

    def _request_app_service_token(self, scopes, resource, secret):
        params = dict({"api-version": "2017-09-01", "resource": resource}, **self._identity_config)
        return self._client.request_token(scopes, method="GET", headers={"secret": secret}, params=params)

    def _request_legacy_token(self, scopes, resource):
        form_data = dict({"resource": resource}, **self._identity_config)
        return self._client.request_token(scopes, method="POST", form_data=form_data)
