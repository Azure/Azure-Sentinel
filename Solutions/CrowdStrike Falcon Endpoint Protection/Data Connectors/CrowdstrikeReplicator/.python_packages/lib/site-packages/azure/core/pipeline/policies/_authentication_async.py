# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncHTTPPolicy
from azure.core.pipeline.policies._authentication import _BearerTokenCredentialPolicyBase

from .._tools_async import await_result

if TYPE_CHECKING:
    from typing import Any, Awaitable, Optional, Union
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse


class AsyncBearerTokenCredentialPolicy(AsyncHTTPPolicy):
    """Adds a bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential: "AsyncTokenCredential", *scopes: str, **kwargs: "Any") -> None:
        # pylint:disable=unused-argument
        super().__init__()
        self._credential = credential
        self._lock = asyncio.Lock()
        self._scopes = scopes
        self._token = None  # type: Optional[AccessToken]

    async def on_request(self, request: "PipelineRequest") -> None:  # pylint:disable=invalid-overridden-method
        """Adds a bearer token Authorization header to request and sends request to next policy.

        :param request: The pipeline request object to be modified.
        :type request: ~azure.core.pipeline.PipelineRequest
        :raises: :class:`~azure.core.exceptions.ServiceRequestError`
        """
        _BearerTokenCredentialPolicyBase._enforce_https(request)  # pylint:disable=protected-access

        if self._token is None or self._need_new_token():
            async with self._lock:
                # double check because another coroutine may have acquired a token while we waited to acquire the lock
                if self._token is None or self._need_new_token():
                    self._token = await self._credential.get_token(*self._scopes)
        request.http_request.headers["Authorization"] = "Bearer " + self._token.token

    async def authorize_request(self, request: "PipelineRequest", *scopes: str, **kwargs: "Any") -> None:
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """
        async with self._lock:
            self._token = await self._credential.get_token(*scopes, **kwargs)
        request.http_request.headers["Authorization"] = "Bearer " + self._token.token

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        """Authorize request with a bearer token and send it to the next policy

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        await await_result(self.on_request, request)
        try:
            response = await self.next.send(request)
            await await_result(self.on_response, request, response)
        except Exception:  # pylint:disable=broad-except
            handled = await await_result(self.on_exception, request)
            if not handled:
                raise
        else:
            if response.http_response.status_code == 401:
                self._token = None  # any cached token is invalid
                if "WWW-Authenticate" in response.http_response.headers:
                    request_authorized = await self.on_challenge(request, response)
                    if request_authorized:
                        try:
                            response = await self.next.send(request)
                            await await_result(self.on_response, request, response)
                        except Exception:  # pylint:disable=broad-except
                            handled = await await_result(self.on_exception, request)
                            if not handled:
                                raise

        return response

    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        """
        # pylint:disable=unused-argument,no-self-use
        return False

    def on_response(self, request: "PipelineRequest", response: "PipelineResponse") -> "Union[None, Awaitable[None]]":
        """Executed after the request comes back from the next policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        """

    def on_exception(self, request: "PipelineRequest") -> None:
        """Executed when an exception is raised while executing the next policy.

        This method is executed inside the exception handler.

        :param request: The Pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        # pylint: disable=no-self-use,unused-argument
        return

    def _need_new_token(self) -> bool:
        return not self._token or self._token.expires_on - time.time() < 300
