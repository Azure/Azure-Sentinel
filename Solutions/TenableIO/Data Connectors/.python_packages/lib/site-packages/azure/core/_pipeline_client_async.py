# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import logging
from collections.abc import Iterable
from typing import Any, Awaitable
from .configuration import Configuration
from .pipeline import AsyncPipeline
from .pipeline.transport._base import PipelineClientBase
from .pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    RequestIdPolicy,
    AsyncRetryPolicy,
)
from ._pipeline_client import _prepare_request
from .pipeline._tools_async import to_rest_response as _to_rest_response

try:
    from typing import TYPE_CHECKING, TypeVar
except ImportError:
    TYPE_CHECKING = False

HTTPRequestType = TypeVar("HTTPRequestType")
AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType")

if TYPE_CHECKING:
    from typing import (
        List,
        Dict,
        Union,
        IO,
        Tuple,
        Optional,
        Callable,
        Iterator,
        cast,
    )  # pylint: disable=unused-import

_LOGGER = logging.getLogger(__name__)


class AsyncPipelineClient(PipelineClientBase):
    """Service client core methods.

    Builds an AsyncPipeline client.

    :param str base_url: URL for the request.
    :keyword ~azure.core.configuration.Configuration config: If omitted, the standard configuration is used.
    :keyword Pipeline pipeline: If omitted, a Pipeline object is created and returned.
    :keyword list[AsyncHTTPPolicy] policies: If omitted, the standard policies of the configuration object is used.
    :keyword per_call_policies: If specified, the policies will be added into the policy list before RetryPolicy
    :paramtype per_call_policies: Union[AsyncHTTPPolicy, SansIOHTTPPolicy,
        list[AsyncHTTPPolicy], list[SansIOHTTPPolicy]]
    :keyword per_retry_policies: If specified, the policies will be added into the policy list after RetryPolicy
    :paramtype per_retry_policies: Union[AsyncHTTPPolicy, SansIOHTTPPolicy,
        list[AsyncHTTPPolicy], list[SansIOHTTPPolicy]]
    :keyword AsyncHttpTransport transport: If omitted, AioHttpTransport is used for asynchronous transport.
    :return: An async pipeline object.
    :rtype: ~azure.core.pipeline.AsyncPipeline

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_async.py
            :start-after: [START build_async_pipeline_client]
            :end-before: [END build_async_pipeline_client]
            :language: python
            :dedent: 4
            :caption: Builds the async pipeline client.
    """

    def __init__(self, base_url, **kwargs):
        super(AsyncPipelineClient, self).__init__(base_url)
        self._config = kwargs.pop("config", None) or Configuration(**kwargs)
        self._base_url = base_url
        if kwargs.get("pipeline"):
            self._pipeline = kwargs["pipeline"]
        else:
            self._pipeline = self._build_pipeline(self._config, **kwargs)

    async def __aenter__(self):
        await self._pipeline.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        await self._pipeline.__aexit__()

    def _build_pipeline(self, config, **kwargs): # pylint: disable=no-self-use
        transport = kwargs.get('transport')
        policies = kwargs.get('policies')
        per_call_policies = kwargs.get('per_call_policies', [])
        per_retry_policies = kwargs.get('per_retry_policies', [])

        if policies is None:  # [] is a valid policy list
            policies = [
                RequestIdPolicy(**kwargs),
                config.headers_policy,
                config.user_agent_policy,
                config.proxy_policy,
                ContentDecodePolicy(**kwargs)
            ]
            if isinstance(per_call_policies, Iterable):
                policies.extend(per_call_policies)
            else:
                policies.append(per_call_policies)

            policies.extend([config.redirect_policy,
                             config.retry_policy,
                             config.authentication_policy,
                             config.custom_hook_policy])
            if isinstance(per_retry_policies, Iterable):
                policies.extend(per_retry_policies)
            else:
                policies.append(per_retry_policies)

            policies.extend([config.logging_policy,
                             DistributedTracingPolicy(**kwargs),
                             config.http_logging_policy or HttpLoggingPolicy(**kwargs)])
        else:
            if isinstance(per_call_policies, Iterable):
                per_call_policies_list = list(per_call_policies)
            else:
                per_call_policies_list = [per_call_policies]
            per_call_policies_list.extend(policies)
            policies = per_call_policies_list
            if isinstance(per_retry_policies, Iterable):
                per_retry_policies_list = list(per_retry_policies)
            else:
                per_retry_policies_list = [per_retry_policies]
            if len(per_retry_policies_list) > 0:
                index_of_retry = -1
                for index, policy in enumerate(policies):
                    if isinstance(policy, AsyncRetryPolicy):
                        index_of_retry = index
                if index_of_retry == -1:
                    raise ValueError("Failed to add per_retry_policies; "
                                     "no RetryPolicy found in the supplied list of policies. ")
                policies_1 = policies[:index_of_retry + 1]
                policies_2 = policies[index_of_retry + 1:]
                policies_1.extend(per_retry_policies_list)
                policies_1.extend(policies_2)
                policies = policies_1

        if not transport:
            from .pipeline.transport import AioHttpTransport
            transport = AioHttpTransport(**kwargs)

        return AsyncPipeline(transport, policies)

    async def _make_pipeline_call(self, request, **kwargs):
        rest_request, request_to_run = _prepare_request(request)
        return_pipeline_response = kwargs.pop("_return_pipeline_response", False)
        pipeline_response = await self._pipeline.run(
            request_to_run, **kwargs  # pylint: disable=protected-access
        )
        response = pipeline_response.http_response
        if rest_request:
            rest_response = _to_rest_response(response)
            if not kwargs.get("stream"):
                try:
                    # in this case, the pipeline transport response already called .load_body(), so
                    # the body is loaded. instead of doing response.read(), going to set the body
                    # to the internal content
                    rest_response._content = response.body()  # pylint: disable=protected-access
                    await rest_response.close()
                except Exception as exc:
                    await rest_response.close()
                    raise exc
            response = rest_response
        if return_pipeline_response:
            pipeline_response.http_response = response
            pipeline_response.http_request = request
            return pipeline_response
        return response

    def send_request(
        self,
        request: HTTPRequestType,
        *,
        stream: bool = False,
        **kwargs: Any
    ) -> Awaitable[AsyncHTTPResponseType]:
        """**Provisional** method that runs the network request through the client's chained policies.

        This method is marked as **provisional**, meaning it may be changed in a future release.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest('GET', 'http://www.example.com')
        <HttpRequest [GET], url: 'http://www.example.com'>
        >>> response = await client.send_request(request)
        <AsyncHttpResponse: 200 OK>

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        from .rest._rest_py3 import _AsyncContextManager
        wrapped = self._make_pipeline_call(request, stream=stream, **kwargs)
        return _AsyncContextManager(wrapped=wrapped)
