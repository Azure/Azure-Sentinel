# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy

from .._authentication import _HttpChallenge

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineResponse, PipelineRequest  # pylint: disable=ungrouped-imports


class AsyncBearerTokenChallengePolicy(AsyncBearerTokenCredentialPolicy):
    """Adds a bearer token Authorization header to requests, for the tenant provided in authentication challenges.

    See https://docs.microsoft.com/azure/active-directory/develop/claims-challenge for documentation on AAD
    authentication challenges.

    :param credential: The credential.
    :type credential: ~azure.core.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :keyword bool discover_tenant: Determines if tenant discovery should be enabled. Defaults to True.
    :keyword bool discover_scopes: Determines if scopes from authentication challenges should be provided to token
        requests, instead of the scopes given to the policy's constructor, if any are present. Defaults to True.
    :raises: :class:`~azure.core.exceptions.ServiceRequestError`
    """

    def __init__(
        self,
        credential: "AsyncTokenCredential",
        *scopes: str,
        discover_tenant: bool = True,
        discover_scopes: bool = True,
        **kwargs: "Any"
    ) -> None:
        self._discover_tenant = discover_tenant
        self._discover_scopes = discover_scopes
        super().__init__(credential, *scopes, **kwargs)

    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        """
        if not self._discover_tenant and not self._discover_scopes:
            # We can't discover the tenant or use a different scope; the request will fail because it hasn't changed
            return False

        try:
            challenge = _HttpChallenge(response.http_response.headers.get("WWW-Authenticate"))
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            # if no scopes are included in the challenge, challenge.scope and challenge.resource will both be ''
            scope = challenge.scope or challenge.resource + "/.default" if self._discover_scopes else self._scopes
            if scope == "/.default":
                scope = self._scopes
        except ValueError:
            return False

        if self._discover_tenant:
            await self.authorize_request(request, scope, tenant_id=challenge.tenant_id)
        else:
            await self.authorize_request(request, scope)
        return True
