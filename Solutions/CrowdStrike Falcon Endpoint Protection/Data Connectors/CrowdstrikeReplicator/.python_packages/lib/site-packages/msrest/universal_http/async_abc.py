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
import abc

from typing import Any, List, Union, Callable, AsyncIterator, Optional

try:
    from contextlib import AbstractAsyncContextManager  # type: ignore
except ImportError: # Python <= 3.7
    class AbstractAsyncContextManager(object):  # type: ignore
        async def __aenter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        async def __aexit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None

from . import ClientRequest, HTTPClientResponse


class AsyncClientResponse(HTTPClientResponse):

    def stream_download(self, chunk_size: Optional[int] = None, callback: Optional[Callable] = None) -> AsyncIterator[bytes]:
        """Generator for streaming request body data.

        Should be implemented by sub-classes if streaming download
        is supported.

        :param callback: Custom callback for monitoring progress.
        :param int chunk_size:
        """
        pass


class AsyncHTTPSender(AbstractAsyncContextManager, abc.ABC):
    """An http sender ABC.
    """

    @abc.abstractmethod
    async def send(self, request: ClientRequest, **config: Any) -> AsyncClientResponse:
        """Send the request using this HTTP sender.
        """
        pass

    def build_context(self) -> Any:
        """Allow the sender to build a context that will be passed
        across the pipeline with the request.

        Return type has no constraints. Implementation is not
        required and None by default.
        """
        return None

    def __enter__(self):
        raise TypeError("Use 'async with' instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover


__all__ = [
    'AsyncHTTPSender',
    'AsyncClientResponse'
]