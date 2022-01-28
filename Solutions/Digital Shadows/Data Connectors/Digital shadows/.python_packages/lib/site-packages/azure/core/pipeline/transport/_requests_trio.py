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
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Callable, Union, Optional, AsyncIterator as AsyncIteratorType
import trio
import urllib3

import requests

from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError
)
from azure.core.pipeline import Pipeline
from ._base import HttpRequest
from ._base_async import (
    AsyncHttpResponse,
    _ResponseStopIteration,
    _iterate_response_content)
from ._requests_basic import RequestsTransportResponse
from ._base_requests_async import RequestsAsyncTransportBase


_LOGGER = logging.getLogger(__name__)


class TrioStreamDownloadGenerator(AsyncIterator):
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    """
    def __init__(self, pipeline: Pipeline, response: AsyncHttpResponse) -> None:
        self.pipeline = pipeline
        self.request = response.request
        self.response = response
        self.block_size = response.block_size
        self.iter_content_func = self.response.internal_response.iter_content(self.block_size)
        self.content_length = int(response.headers.get('Content-Length', 0))
        self.downloaded = 0

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        try:
            try:
                chunk = await trio.to_thread.run_sync(
                    _iterate_response_content,
                    self.iter_content_func,
                )
            except AttributeError:  # trio < 0.12.1
                chunk = await trio.run_sync_in_worker_thread(  # pylint: disable=no-member
                    _iterate_response_content,
                    self.iter_content_func,
                )
            if not chunk:
                raise _ResponseStopIteration()
            return chunk
        except _ResponseStopIteration:
            self.response.internal_response.close()
            raise StopAsyncIteration()
        except requests.exceptions.StreamConsumedError:
            raise
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            self.response.internal_response.close()
            raise

class TrioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse):  # type: ignore
    """Asynchronous streaming of data from the response.
    """
    def stream_download(self, pipeline) -> AsyncIteratorType[bytes]:  # type: ignore
        """Generator for streaming response data.
        """
        return TrioStreamDownloadGenerator(pipeline, self)


class TrioRequestsTransport(RequestsAsyncTransportBase):  # type: ignore
    """Identical implementation as the synchronous RequestsTransport wrapped in a class with
    asynchronous methods. Uses the third party trio event loop.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_async.py
            :start-after: [START trio]
            :end-before: [END trio]
            :language: python
            :dedent: 4
            :caption: Asynchronous transport with trio.
    """
    async def __aenter__(self):
        return super(TrioRequestsTransport, self).__enter__()

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        return super(TrioRequestsTransport, self).__exit__()

    async def sleep(self, duration):  # pylint:disable=invalid-overridden-method
        await trio.sleep(duration)

    async def send(self, request: HttpRequest, **kwargs: Any) -> AsyncHttpResponse:  # type: ignore # pylint:disable=invalid-overridden-method
        """Send the request using this HTTP sender.

        :param request: The HttpRequest
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: The AsyncHttpResponse
        :rtype: ~azure.core.pipeline.transport.AsyncHttpResponse

        :keyword requests.Session session: will override the driver session and use yours.
         Should NOT be done unless really required. Anything else is sent straight to requests.
        :keyword dict proxies: will define the proxy to use. Proxy is a dict (protocol, url)
        """
        self.open()
        trio_limiter = kwargs.get("trio_limiter", None)
        response = None
        error = None # type: Optional[Union[ServiceRequestError, ServiceResponseError]]
        data_to_send = await self._retrieve_request_data(request)
        try:
            try:
                response = await trio.to_thread.run_sync(
                    functools.partial(
                        self.session.request,
                        request.method,
                        request.url,
                        headers=request.headers,
                        data=data_to_send,
                        files=request.files,
                        verify=kwargs.pop('connection_verify', self.connection_config.verify),
                        timeout=kwargs.pop('connection_timeout', self.connection_config.timeout),
                        cert=kwargs.pop('connection_cert', self.connection_config.cert),
                        allow_redirects=False,
                        **kwargs),
                    limiter=trio_limiter)
            except AttributeError:  # trio < 0.12.1
                response = await trio.run_sync_in_worker_thread(  # pylint: disable=no-member
                    functools.partial(
                        self.session.request,
                        request.method,
                        request.url,
                        headers=request.headers,
                        data=request.data,
                        files=request.files,
                        verify=kwargs.pop('connection_verify', self.connection_config.verify),
                        timeout=kwargs.pop('connection_timeout', self.connection_config.timeout),
                        cert=kwargs.pop('connection_cert', self.connection_config.cert),
                        allow_redirects=False,
                        **kwargs),
                    limiter=trio_limiter)

        except urllib3.exceptions.NewConnectionError as err:
            error = ServiceRequestError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error

        return TrioRequestsTransportResponse(request, response, self.connection_config.data_block_size)
