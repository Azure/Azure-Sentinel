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

import copy
import time

from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import HttpRequest

from .http_challenge import HttpChallenge
from . import http_challenge_cache as ChallengeCache

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Optional
    from azure.core.credentials import AccessToken, TokenCredential
    from azure.core.pipeline.transport import HttpResponse


def _enforce_tls(request):
    # type: (PipelineRequest) -> None
    if not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )


def _get_challenge_request(request):
    # type: (PipelineRequest) -> PipelineRequest

    # The challenge request is intended to provoke an authentication challenge from Key Vault, to learn how the
    # service request should be authenticated. It should be identical to the service request but with no body.
    challenge_request = HttpRequest(
        request.http_request.method, request.http_request.url, headers=request.http_request.headers
    )
    challenge_request.headers["Content-Length"] = "0"

    options = copy.deepcopy(request.context.options)
    context = PipelineContext(request.context.transport, **options)

    return PipelineRequest(http_request=challenge_request, context=context)


def _update_challenge(request, challenger):
    # type: (HttpRequest, HttpResponse) -> HttpChallenge
    """parse challenge from challenger, cache it, return it"""

    challenge = HttpChallenge(
        request.http_request.url,
        challenger.http_response.headers.get("WWW-Authenticate"),
        response_headers=challenger.http_response.headers,
    )
    ChallengeCache.set_challenge_for_url(request.http_request.url, challenge)
    return challenge


class ChallengeAuthPolicyBase(object):
    """Sans I/O base for challenge authentication policies"""

    def __init__(self, **kwargs):
        self._token = None  # type: Optional[AccessToken]
        super(ChallengeAuthPolicyBase, self).__init__(**kwargs)

    @property
    def _need_new_token(self):
        # type: () -> bool
        return not self._token or self._token.expires_on - time.time() < 300


class ChallengeAuthPolicy(ChallengeAuthPolicyBase, HTTPPolicy):
    """policy for handling HTTP authentication challenges"""

    def __init__(self, credential, **kwargs):
        # type: (TokenCredential, **Any) -> None
        self._credential = credential
        super(ChallengeAuthPolicy, self).__init__(**kwargs)

    def send(self, request):
        # type: (PipelineRequest) -> HttpResponse
        _enforce_tls(request)

        challenge = ChallengeCache.get_challenge_for_url(request.http_request.url)
        if not challenge:
            challenge_request = _get_challenge_request(request)
            challenger = self.next.send(challenge_request)
            try:
                challenge = _update_challenge(request, challenger)
            except ValueError:
                # didn't receive the expected challenge -> nothing more this policy can do
                return challenger

        self._handle_challenge(request, challenge)
        response = self.next.send(request)

        if response.http_response.status_code == 401:
            # any cached token must be invalid
            self._token = None

            # cached challenge could be outdated; maybe this response has a new one?
            try:
                challenge = _update_challenge(request, response)
            except ValueError:
                # 401 with no legible challenge -> nothing more this policy can do
                return response

            self._handle_challenge(request, challenge)
            response = self.next.send(request)

        return response

    def _handle_challenge(self, request, challenge):
        # type: (PipelineRequest, HttpChallenge) -> None
        """authenticate according to challenge, add Authorization header to request"""

        if self._need_new_token:
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            scope = challenge.get_scope() or challenge.get_resource() + "/.default"
            self._token = self._credential.get_token(scope)

        # ignore mypy's warning because although self._token is Optional, get_token raises when it fails to get a token
        request.http_request.headers["Authorization"] = "Bearer {}".format(self._token.token)  # type: ignore
