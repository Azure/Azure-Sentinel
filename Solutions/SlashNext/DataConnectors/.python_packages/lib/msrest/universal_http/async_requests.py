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
import asyncio
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Callable, Optional, AsyncIterator as AsyncIteratorType

from oauthlib import oauth2
import requests
from requests.models import CONTENT_CHUNK_SIZE

from ..exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback)
from . import AsyncHTTPSender, ClientRequest, AsyncClientResponse
from .requests import (
    BasicRequestsHTTPSender,
    RequestsHTTPSender,
    HTTPRequestsClientResponse
)


_LOGGER = logging.getLogger(__name__)


class AsyncBasicRequestsHTTPSender(BasicRequestsHTTPSender, AsyncHTTPSender):  # type: ignore

    async def __aenter__(self):
        return super(AsyncBasicRequestsHTTPSender, self).__enter__()

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        return super(AsyncBasicRequestsHTTPSender, self).__exit__()

    async def send(self, request: ClientRequest, **kwargs: Any) -> AsyncClientResponse:  # type: ignore
        """Send the request using this HTTP sender.
        """
        # It's not recommended to provide its own session, and is mostly
        # to enable some legacy code to plug correctly
        session = kwargs.pop('session', self.session)

        loop = kwargs.get("loop", asyncio.get_event_loop())
        future = loop.run_in_executor(
            None,
            functools.partial(
                session.request,
                request.method,
                request.url,
                **kwargs
            )
        )
        try:
            return AsyncRequestsClientResponse(
                request,
                await future
            )
        except requests.RequestException as err:
            msg = "Error occurred in request."
            raise_with_traceback(ClientRequestError, msg, err)

class AsyncRequestsHTTPSender(AsyncBasicRequestsHTTPSender, RequestsHTTPSender):  # type: ignore

    async def send(self, request: ClientRequest, **kwargs: Any) -> AsyncClientResponse:  # type: ignore
        """Send the request using this HTTP sender.
        """
        requests_kwargs = self._configure_send(request, **kwargs)
        return await super(AsyncRequestsHTTPSender, self).send(request, **requests_kwargs)


class _MsrestStopIteration(Exception):
    pass

def _msrest_next(iterator):
    """"To avoid:
    TypeError: StopIteration interacts badly with generators and cannot be raised into a Future
    """
    try:
        return next(iterator)
    except StopIteration:
        raise _MsrestStopIteration()

class StreamDownloadGenerator(AsyncIterator):

    def __init__(self, response: requests.Response, user_callback: Optional[Callable] = None, block: Optional[int] = None) -> None:
        self.response = response
        self.block = block or CONTENT_CHUNK_SIZE
        self.user_callback = user_callback
        self.iter_content_func = self.response.iter_content(self.block)

    async def __anext__(self):
        loop = asyncio.get_event_loop()
        try:
            chunk = await loop.run_in_executor(
                None,
                _msrest_next,
                self.iter_content_func,
            )
            if not chunk:
                raise _MsrestStopIteration()
            if self.user_callback and callable(self.user_callback):
                self.user_callback(chunk, self.response)
            return chunk
        except _MsrestStopIteration:
            self.response.close()
            raise StopAsyncIteration()
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            self.response.close()
            raise

class AsyncRequestsClientResponse(AsyncClientResponse, HTTPRequestsClientResponse):

    def stream_download(self, chunk_size: Optional[int] = None, callback: Optional[Callable] = None) -> AsyncIteratorType[bytes]:
        """Generator for streaming request body data.

        :param callback: Custom callback for monitoring progress.
        :param int chunk_size:
        """
        return StreamDownloadGenerator(
            self.internal_response,
            callback,
            chunk_size
        )


# Trio support
try:
    import trio

    class TrioStreamDownloadGenerator(AsyncIterator):

        def __init__(self, response: requests.Response, user_callback: Optional[Callable] = None, block: Optional[int] = None) -> None:
            self.response = response
            self.block = block or CONTENT_CHUNK_SIZE
            self.user_callback = user_callback
            self.iter_content_func = self.response.iter_content(self.block)

        async def __anext__(self):
            try:
                chunk = await trio.to_thread.run_sync(
                    _msrest_next,
                    self.iter_content_func,
                )
                if not chunk:
                    raise _MsrestStopIteration()
                if self.user_callback and callable(self.user_callback):
                    self.user_callback(chunk, self.response)
                return chunk
            except _MsrestStopIteration:
                self.response.close()
                raise StopAsyncIteration()
            except Exception as err:
                _LOGGER.warning("Unable to stream download: %s", err)
                self.response.close()
                raise

    class TrioAsyncRequestsClientResponse(AsyncClientResponse, HTTPRequestsClientResponse):

        def stream_download(self, chunk_size: Optional[int] = None, callback: Optional[Callable] = None) -> AsyncIteratorType[bytes]:
            """Generator for streaming request body data.

            :param callback: Custom callback for monitoring progress.
            :param int chunk_size:
            """
            return TrioStreamDownloadGenerator(
                self.internal_response,
                callback,
                chunk_size
            )


    class AsyncTrioBasicRequestsHTTPSender(BasicRequestsHTTPSender, AsyncHTTPSender):  # type: ignore

        async def __aenter__(self):
            return super(AsyncTrioBasicRequestsHTTPSender, self).__enter__()

        async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
            return super(AsyncTrioBasicRequestsHTTPSender, self).__exit__()

        async def send(self, request: ClientRequest, **kwargs: Any) -> AsyncClientResponse:  # type: ignore
            """Send the request using this HTTP sender.
            """
            # It's not recommended to provide its own session, and is mostly
            # to enable some legacy code to plug correctly
            session = kwargs.pop('session', self.session)

            trio_limiter = kwargs.get("trio_limiter", None)
            future = trio.to_thread.run_sync(
                functools.partial(
                    session.request,
                    request.method,
                    request.url,
                    **kwargs
                ),
                limiter=trio_limiter
            )
            try:
                return TrioAsyncRequestsClientResponse(
                    request,
                    await future
                )
            except requests.RequestException as err:
                msg = "Error occurred in request."
                raise_with_traceback(ClientRequestError, msg, err)

    class AsyncTrioRequestsHTTPSender(AsyncTrioBasicRequestsHTTPSender, RequestsHTTPSender):  # type: ignore

        async def send(self, request: ClientRequest, **kwargs: Any) -> AsyncClientResponse:  # type: ignore
            """Send the request using this HTTP sender.
            """
            requests_kwargs = self._configure_send(request, **kwargs)
            return await super(AsyncTrioRequestsHTTPSender, self).send(request, **requests_kwargs)

except ImportError:
    # trio not installed
    pass