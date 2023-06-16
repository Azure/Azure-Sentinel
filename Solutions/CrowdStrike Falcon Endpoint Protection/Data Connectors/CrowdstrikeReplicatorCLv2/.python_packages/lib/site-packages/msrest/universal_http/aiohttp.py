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
from typing import Any, Callable, AsyncIterator, Optional

import aiohttp
from multidict import CIMultiDict

from . import AsyncHTTPSender, ClientRequest, AsyncClientResponse

# Matching requests, because why not?
CONTENT_CHUNK_SIZE = 10 * 1024


class AioHTTPSender(AsyncHTTPSender):
    """AioHttp HTTP sender implementation.
    """

    def __init__(self, *, loop=None):
        self._session = aiohttp.ClientSession(loop=loop)

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        await self._session.__aexit__(*exc_details)

    async def send(self, request: ClientRequest, **config: Any) -> AsyncClientResponse:
        """Send the request using this HTTP sender.

        Will pre-load the body into memory to be available with a sync method.
        pass stream=True to avoid this behavior.
        """
        result = await self._session.request(
            request.method,
            request.url,
            **config
        )
        response = AioHttpClientResponse(request, result)
        if not config.get("stream", False):
            await response.load_body()
        return response


class AioHttpClientResponse(AsyncClientResponse):
    def __init__(self, request: ClientRequest, aiohttp_response: aiohttp.ClientResponse) -> None:
        super(AioHttpClientResponse, self).__init__(request, aiohttp_response)
        # https://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientResponse
        self.status_code = aiohttp_response.status
        self.headers = CIMultiDict(aiohttp_response.headers)
        self.reason = aiohttp_response.reason
        self._body = None

    def body(self) -> bytes:
        """Return the whole body as bytes in memory.
        """
        if not self._body:
            raise ValueError("Body is not available. Call async method load_body, or do your call with stream=False.")
        return self._body

    async def load_body(self) -> None:
        """Load in memory the body, so it could be accessible from sync methods."""
        self._body = await self.internal_response.read()

    def raise_for_status(self):
        self.internal_response.raise_for_status()

    def stream_download(self, chunk_size: Optional[int] = None, callback: Optional[Callable] = None) -> AsyncIterator[bytes]:
        """Generator for streaming request body data.
        """
        chunk_size = chunk_size or CONTENT_CHUNK_SIZE
        async def async_gen(resp):
            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                callback(chunk, resp)
        return async_gen(self.internal_response)
