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
from .configuration import Configuration
from .pipeline import AsyncPipeline
from .pipeline.transport._base import PipelineClientBase
from .pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    RequestIdPolicy,
)

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import (
        List,
        Any,
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
    :keyword AsyncHttpTransport transport: If omitted, AioHttpTransport is used for synchronous transport.
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

        if policies is None:  # [] is a valid policy list
            per_call_policies = kwargs.get('per_call_policies', [])
            per_retry_policies = kwargs.get('per_retry_policies', [])
            policies = [
                RequestIdPolicy(**kwargs),
                config.headers_policy,
                config.user_agent_policy,
                config.proxy_policy,
                ContentDecodePolicy(**kwargs)
            ]
            if isinstance(per_call_policies, Iterable):
                for policy in per_call_policies:
                    policies.append(policy)
            else:
                policies.append(per_call_policies)

            policies = policies + [
                config.redirect_policy,
                config.retry_policy,
                config.authentication_policy,
                config.custom_hook_policy
            ]
            if isinstance(per_retry_policies, Iterable):
                for policy in per_retry_policies:
                    policies.append(policy)
            else:
                policies.append(per_retry_policies)

            policies = policies + [
                config.logging_policy,
                DistributedTracingPolicy(**kwargs),
                config.http_logging_policy or HttpLoggingPolicy(**kwargs)
            ]

        if not transport:
            from .pipeline.transport import AioHttpTransport
            transport = AioHttpTransport(**kwargs)

        return AsyncPipeline(transport, policies)
