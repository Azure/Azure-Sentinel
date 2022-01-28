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
import collections.abc
from typing import (
    AsyncIterable,
    Dict,
    Iterable,
    Tuple,
    Union,
    Callable,
    Optional,
    AsyncIterator as AsyncIteratorType
)
from ..exceptions import StreamConsumedError, StreamClosedError

from ._helpers import (
    _shared_set_content_body,
    HeadersType
)
ContentType = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]

def set_content_body(content: ContentType) -> Tuple[
    HeadersType, ContentType
]:
    headers, body = _shared_set_content_body(content)
    if body is not None:
        return headers, body
    if isinstance(content, collections.abc.AsyncIterable):
        return {}, content
    raise TypeError(
        "Unexpected type for 'content': '{}'. ".format(type(content)) +
        "We expect 'content' to either be str, bytes, or an Iterable / AsyncIterable"
    )

def _stream_download_helper(
    decompress: bool,
    stream_download_generator: Callable,
    response,
) -> AsyncIteratorType[bytes]:
    if response.is_stream_consumed:
        raise StreamConsumedError(response)
    if response.is_closed:
        raise StreamClosedError(response)

    response.is_stream_consumed = True
    return stream_download_generator(
        pipeline=None,
        response=response,
        decompress=decompress,
    )

async def iter_bytes_helper(
    stream_download_generator: Callable,
    response,
    content: Optional[bytes],
) -> AsyncIteratorType[bytes]:
    if content:
        chunk_size = response._connection_data_block_size  # pylint: disable=protected-access
        for i in range(0, len(content), chunk_size):
            yield content[i : i + chunk_size]
    else:
        async for part in _stream_download_helper(
            decompress=True,
            stream_download_generator=stream_download_generator,
            response=response,
        ):
            yield part

async def iter_raw_helper(
    stream_download_generator: Callable,
    response,
) -> AsyncIteratorType[bytes]:
    async for part in _stream_download_helper(
        decompress=False,
        stream_download_generator=stream_download_generator,
        response=response,
    ):
        yield part
