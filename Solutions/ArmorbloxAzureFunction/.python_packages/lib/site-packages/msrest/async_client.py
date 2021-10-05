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

import functools
import logging

from typing import Any, Dict, List, Union, TYPE_CHECKING

from .universal_http import ClientRequest
from .universal_http.async_requests import AsyncRequestsHTTPSender
from .pipeline import Request, AsyncPipeline, AsyncHTTPPolicy, SansIOHTTPPolicy
from .pipeline.async_requests import (
    AsyncPipelineRequestsHTTPSender,
    AsyncRequestsCredentialsPolicy
)
from .pipeline.universal import (
    HTTPLogger,
    RawDeserializer,
)

from .service_client import _ServiceClientCore

if TYPE_CHECKING:
    from .configuration import Configuration  # pylint: disable=unused-import

_LOGGER = logging.getLogger(__name__)


class SDKClientAsync:
    """The base class of all generated SDK async client.
    """

    def __init__(self, config: 'Configuration') -> None:
        self._client = ServiceClientAsync(config)

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        await self._client.__aexit__(*exc_details)


class ServiceClientAsync(_ServiceClientCore):

    def __init__(self, config: 'Configuration') -> None:
        super(ServiceClientAsync, self).__init__(config)

        self.config.pipeline = self._create_default_pipeline()  # type: ignore

    def _create_default_pipeline(self):
        creds = self.config.credentials

        policies = [
            self.config.user_agent_policy,  # UserAgent policy
            RawDeserializer(),         # Deserialize the raw bytes
            self.config.http_logger_policy  # HTTP request/response log
        ]  # type: List[Union[AsyncHTTPPolicy, SansIOHTTPPolicy]]
        if creds:
            if isinstance(creds, (AsyncHTTPPolicy, SansIOHTTPPolicy)):
                policies.insert(1, creds)
            else:
                # Assume this is the old credentials class, and then requests. Wrap it.
                policies.insert(1, AsyncRequestsCredentialsPolicy(creds))

        return AsyncPipeline(
            policies,
            AsyncPipelineRequestsHTTPSender(
                AsyncRequestsHTTPSender(self.config)  # Send HTTP request using requests
            )
        )

    async def __aenter__(self):
        await self.config.pipeline.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        await self.config.pipeline.__aexit__(*exc_details)

    async def async_send(self, request, **kwargs):
        """Prepare and send request object according to configuration.

        :param ClientRequest request: The request object to be sent.
        :param dict headers: Any headers to add to the request.
        :param content: Any body data to add to the request.
        :param config: Any specific config overrides
        """
        kwargs.setdefault('stream', True)
        # In the current backward compatible implementation, return the HTTP response
        # and plug context inside. Could be remove if we modify Autorest,
        # but we still need it to be backward compatible
        pipeline_response = await self.config.pipeline.run(request, **kwargs)
        response = pipeline_response.http_response
        response.context = pipeline_response.context
        return response

    def stream_download_async(self, response, user_callback):
        """Async Generator for streaming request body data.

        :param response: The initial response
        :param user_callback: Custom callback for monitoring progress.
        """
        block = self.config.connection.data_block_size
        return response.stream_download(block, user_callback)
