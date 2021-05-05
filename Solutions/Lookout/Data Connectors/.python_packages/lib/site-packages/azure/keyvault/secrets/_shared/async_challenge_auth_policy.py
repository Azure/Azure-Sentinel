# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Policy implementing Key Vault's challenge authentication protocol.

Normally the protocol is only used for the client's first service request, upon which:
1. The challenge authentication policy sends a copy of the request, without authorization or content.
2. Key Vault responds 401 with a header (the 'challenge') detailing how the client should authenticate such a request.
3. The policy authenticates according to the challenge and sends the original request with authorization.

The policy caches the challenge and thus knows how to authenticate future requests. However, authentication
requirements can change. For example, a vault may move to a new tenant. In such a case the policy will attempt the
protocol again.
"""
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncHTTPPolicy

from . import HttpChallengeCache
from .challenge_auth_policy import _enforce_tls, _get_challenge_request, _update_challenge, ChallengeAuthPolicyBase

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest
    from azure.core.pipeline.transport import AsyncHttpResponse
    from . import HttpChallenge


class AsyncChallengeAuthPolicy(ChallengeAuthPolicyBase, AsyncHTTPPolicy):
    """policy for handling HTTP authentication challenges"""

    def __init__(self, credential: "AsyncTokenCredential", **kwargs: "Any") -> None:
        self._credential = credential
        super(AsyncChallengeAuthPolicy, self).__init__(**kwargs)

    async def send(self, request: "PipelineRequest") -> "AsyncHttpResponse":
        _enforce_tls(request)

        challenge = HttpChallengeCache.get_challenge_for_url(request.http_request.url)
        if not challenge:
            challenge_request = _get_challenge_request(request)
            challenger = await self.next.send(challenge_request)
            try:
                challenge = _update_challenge(request, challenger)
            except ValueError:
                # didn't receive the expected challenge -> nothing more this policy can do
                return challenger

        await self._handle_challenge(request, challenge)
        response = await self.next.send(request)

        if response.http_response.status_code == 401:
            # any cached token must be invalid
            self._token = None

            # cached challenge could be outdated; maybe this response has a new one?
            try:
                challenge = _update_challenge(request, response)
            except ValueError:
                # 401 with no legible challenge -> nothing more this policy can do
                return response

            await self._handle_challenge(request, challenge)
            response = await self.next.send(request)

        return response

    async def _handle_challenge(self, request: "PipelineRequest", challenge: "HttpChallenge") -> None:
        """authenticate according to challenge, add Authorization header to request"""

        if self._need_new_token:
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
            self._token = await self._credential.get_token(scope)

        # ignore mypy's warning because although self._token is Optional, get_token raises when it fails to get a token
        request.http_request.headers["Authorization"] = "Bearer {}".format(self._token.token)  # type: ignore
