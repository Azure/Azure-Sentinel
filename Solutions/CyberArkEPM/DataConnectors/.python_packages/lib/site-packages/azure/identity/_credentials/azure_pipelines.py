# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore oidcrequesturi
import os
from typing import Any, Optional

from azure.core.exceptions import ClientAuthenticationError
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.rest import HttpRequest, HttpResponse

from .client_assertion import ClientAssertionCredential
from .. import CredentialUnavailableError
from .._internal import validate_tenant_id
from .._internal.pipeline import build_pipeline


SYSTEM_OIDCREQUESTURI = "SYSTEM_OIDCREQUESTURI"
OIDC_API_VERSION = "7.1"
TROUBLESHOOTING_GUIDE = "https://aka.ms/azsdk/python/identity/azurepipelinescredential/troubleshoot"


def build_oidc_request(service_connection_id: str, access_token: str) -> HttpRequest:
    base_uri = os.environ[SYSTEM_OIDCREQUESTURI].rstrip("/")
    url = f"{base_uri}?api-version={OIDC_API_VERSION}&serviceConnectionId={service_connection_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        # Prevents the service from responding with a redirect HTTP status code (useful for automation).
        "X-TFS-FedAuthRedirect": "Suppress",
    }
    return HttpRequest("POST", url, headers=headers)


def validate_env_vars():
    if SYSTEM_OIDCREQUESTURI not in os.environ:
        raise CredentialUnavailableError(
            message=f"Missing value for the {SYSTEM_OIDCREQUESTURI} environment variable. "
            f"AzurePipelinesCredential is intended for use in Azure Pipelines where the "
            f"{SYSTEM_OIDCREQUESTURI} environment variable is set. Please refer to the "
            f"troubleshooting guide at {TROUBLESHOOTING_GUIDE}."
        )


class AzurePipelinesCredential:
    """Authenticates using Microsoft Entra Workload ID in Azure Pipelines.

    This credential enables authentication in Azure Pipelines using workload identity federation for Azure service
    connections.

    :keyword str tenant_id: The tenant ID for the service connection. Required.
    :keyword str client_id: The client ID for the service connection. Required.
    :keyword str service_connection_id: The service connection ID for the service connection associated with the
        pipeline. From the service connection's configuration page URL in the Azure DevOps web portal, the ID
        is the value of the "resourceId" query parameter. Required.
    :keyword str system_access_token: The pipeline's System.AccessToken value. It is recommended to assign the value
        of System.AccessToken to a secure variable in the Azure Pipelines environment. See
        https://learn.microsoft.com/azure/devops/pipelines/build/variables#systemaccesstoken for more info. Required.
    :keyword str authority: Authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_azure_pipelines_credential]
            :end-before: [END create_azure_pipelines_credential]
            :language: python
            :dedent: 4
            :caption: Create an AzurePipelinesCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: str,
        client_id: str,
        service_connection_id: str,
        system_access_token: str,
        **kwargs: Any,
    ) -> None:

        if not system_access_token or not tenant_id or not client_id or not service_connection_id:
            raise ValueError(
                "'tenant_id', 'client_id', 'service_connection_id', and 'system_access_token' must be passed in as "
                f"keyword arguments. Please refer to the troubleshooting guide at {TROUBLESHOOTING_GUIDE}."
            )
        validate_tenant_id(tenant_id)
        self._system_access_token = system_access_token
        self._service_connection_id = service_connection_id
        self._client_assertion_credential = ClientAssertionCredential(
            tenant_id=tenant_id, client_id=client_id, func=self._get_oidc_token, **kwargs
        )
        self._pipeline = build_pipeline(**kwargs)

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
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        validate_env_vars()
        return self._client_assertion_credential.get_token(
            *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
        )

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
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        validate_env_vars()
        return self._client_assertion_credential.get_token_info(*scopes, options=options)

    def _get_oidc_token(self) -> str:
        request = build_oidc_request(self._service_connection_id, self._system_access_token)
        response = self._pipeline.run(request, retry_on_methods=[request.method])
        http_response: HttpResponse = response.http_response
        if http_response.status_code not in [200]:
            raise ClientAuthenticationError(
                message="Unexpected response from OIDC token endpoint.", response=http_response
            )
        json_response = http_response.json()
        if "oidcToken" not in json_response:
            raise ClientAuthenticationError(message="OIDC token not found in response.")
        return json_response["oidcToken"]

    def __enter__(self):
        self._client_assertion_credential.__enter__()
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args):
        self._client_assertion_credential.__exit__(*args)
        self._pipeline.__exit__(*args)

    def close(self) -> None:
        """Close the credential's transport session."""
        self.__exit__()
