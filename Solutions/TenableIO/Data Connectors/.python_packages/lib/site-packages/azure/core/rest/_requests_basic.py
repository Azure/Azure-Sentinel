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
from typing import TYPE_CHECKING, cast

from ..exceptions import ResponseNotReadError, StreamConsumedError, StreamClosedError
from ._rest import _HttpResponseBase, HttpResponse
from ..pipeline.transport._requests_basic import StreamDownloadGenerator

if TYPE_CHECKING:
    from typing import Iterator, Optional

def _has_content(response):
    try:
        response.content  # pylint: disable=pointless-statement
        return True
    except ResponseNotReadError:
        return False

class _RestRequestsTransportResponseBase(_HttpResponseBase):
    def __init__(self, **kwargs):
        super(_RestRequestsTransportResponseBase, self).__init__(**kwargs)
        self.status_code = self._internal_response.status_code
        self.headers = self._internal_response.headers
        self.reason = self._internal_response.reason
        self.content_type = self._internal_response.headers.get('content-type')

    @property
    def content(self):
        # type: () -> bytes
        if not self._internal_response._content_consumed:  # pylint: disable=protected-access
            # if we just call .content, requests will read in the content.
            # we want to read it in our own way
            raise ResponseNotReadError(self)

        try:
            return self._internal_response.content
        except RuntimeError:
            # requests throws a RuntimeError if the content for a response is already consumed
            raise ResponseNotReadError(self)

    @property
    def encoding(self):
        # type: () -> Optional[str]
        retval = super(_RestRequestsTransportResponseBase, self).encoding
        if not retval:
            # There is a few situation where "requests" magic doesn't fit us:
            # - https://github.com/psf/requests/issues/654
            # - https://github.com/psf/requests/issues/1737
            # - https://github.com/psf/requests/issues/2086
            from codecs import BOM_UTF8
            if self._internal_response.content[:3] == BOM_UTF8:
                retval = "utf-8-sig"
        if retval:
            if retval == "utf-8":
                retval = "utf-8-sig"
        return retval

    @encoding.setter  # type: ignore
    def encoding(self, value):
        # type: (str) -> None
        # ignoring setter bc of known mypy issue https://github.com/python/mypy/issues/1465
        self._encoding = value
        self._internal_response.encoding = value

    @property
    def text(self):
        # this will trigger errors if response is not read in
        self.content  # pylint: disable=pointless-statement
        return self._internal_response.text

def _stream_download_helper(decompress, response):
    if response.is_stream_consumed:
        raise StreamConsumedError(response)
    if response.is_closed:
        raise StreamClosedError(response)

    response.is_stream_consumed = True
    stream_download = StreamDownloadGenerator(
        pipeline=None,
        response=response,
        decompress=decompress,
    )
    for part in stream_download:
        yield part

class RestRequestsTransportResponse(HttpResponse, _RestRequestsTransportResponseBase):

    def iter_bytes(self):
        # type: () -> Iterator[bytes]
        """Iterates over the response's bytes. Will decompress in the process
        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        if _has_content(self):
            chunk_size = cast(int, self._connection_data_block_size)
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i : i + chunk_size]
        else:
            for part in _stream_download_helper(
                decompress=True,
                response=self,
            ):
                yield part
        self.close()

    def iter_raw(self):
        # type: () -> Iterator[bytes]
        """Iterates over the response's bytes. Will not decompress in the process
        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        for raw_bytes in _stream_download_helper(
            decompress=False,
            response=self,
        ):
            yield raw_bytes
        self.close()

    def read(self):
        # type: () -> bytes
        """Read the response's bytes.

        :return: The read in bytes
        :rtype: bytes
        """
        if not _has_content(self):
            self._internal_response._content = b"".join(self.iter_bytes())  # pylint: disable=protected-access
        return self.content
