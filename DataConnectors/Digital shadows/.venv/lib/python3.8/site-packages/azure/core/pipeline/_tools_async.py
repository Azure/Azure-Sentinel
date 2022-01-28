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
from ._tools import to_rest_request

async def await_result(func, *args, **kwargs):
    """If func returns an awaitable, await it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        # type ignore on await: https://github.com/python/mypy/issues/7587
        return await result  # type: ignore
    return result

def _get_response_type(pipeline_transport_response):
    try:
        from .transport import AioHttpTransportResponse
        from ..rest._aiohttp import RestAioHttpTransportResponse
        if isinstance(pipeline_transport_response, AioHttpTransportResponse):
            return RestAioHttpTransportResponse
    except ImportError:
        pass
    try:
        from .transport import AsyncioRequestsTransportResponse
        from ..rest._requests_asyncio import RestAsyncioRequestsTransportResponse
        if isinstance(pipeline_transport_response, AsyncioRequestsTransportResponse):
            return RestAsyncioRequestsTransportResponse
    except ImportError:
        pass
    try:
        from .transport import TrioRequestsTransportResponse
        from ..rest._requests_trio import RestTrioRequestsTransportResponse
        if isinstance(pipeline_transport_response, TrioRequestsTransportResponse):
            return RestTrioRequestsTransportResponse
    except ImportError:
        pass
    from ..rest import AsyncHttpResponse
    return AsyncHttpResponse

def to_rest_response(pipeline_transport_response):
    response_type = _get_response_type(pipeline_transport_response)
    response = response_type(
        request=to_rest_request(pipeline_transport_response.request),
        internal_response=pipeline_transport_response.internal_response,
    )
    response._connection_data_block_size = pipeline_transport_response.block_size  # pylint: disable=protected-access
    return response
