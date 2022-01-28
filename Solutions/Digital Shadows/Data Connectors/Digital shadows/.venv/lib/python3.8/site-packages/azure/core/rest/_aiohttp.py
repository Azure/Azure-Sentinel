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
import asyncio
from itertools import groupby
from typing import AsyncIterator
from multidict import CIMultiDict
from . import HttpRequest, AsyncHttpResponse
from ._helpers_py3 import iter_raw_helper, iter_bytes_helper
from ..pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator

class _ItemsView(collections.abc.ItemsView):
    def __init__(self, ref):
        super().__init__(ref)
        self._ref = ref

    def __iter__(self):
        for key, groups in groupby(self._ref.__iter__(), lambda x: x[0]):
            yield tuple([key, ", ".join(group[1] for group in groups)])

    def __contains__(self, item):
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            return False
        for k, v in self.__iter__():
            if item[0].lower() == k.lower() and item[1] == v:
                return True
        return False

    def __repr__(self):
        return f"dict_items({list(self.__iter__())})"

class _KeysView(collections.abc.KeysView):
    def __init__(self, items):
        super().__init__(items)
        self._items = items

    def __iter__(self):
        for key, _ in self._items:
            yield key

    def __contains__(self, key):
        for k in self.__iter__():
            if key.lower() == k.lower():
                return True
        return False
    def __repr__(self):
        return f"dict_keys({list(self.__iter__())})"

class _ValuesView(collections.abc.ValuesView):
    def __init__(self, items):
        super().__init__(items)
        self._items = items

    def __iter__(self):
        for _, value in self._items:
            yield value

    def __contains__(self, value):
        for v in self.__iter__():
            if value == v:
                return True
        return False

    def __repr__(self):
        return f"dict_values({list(self.__iter__())})"


class _CIMultiDict(CIMultiDict):
    """Dictionary with the support for duplicate case-insensitive keys."""

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        """Return a new view of the dictionary's keys."""
        return _KeysView(self.items())

    def items(self):
        """Return a new view of the dictionary's items."""
        return _ItemsView(super().items())

    def values(self):
        """Return a new view of the dictionary's values."""
        return _ValuesView(self.items())

    def __getitem__(self, key: str) -> str:
        return ", ".join(self.getall(key, []))

    def get(self, key, default=None):
        values = self.getall(key, None)
        if values:
            values = ", ".join(values)
        return values or default

class RestAioHttpTransportResponse(AsyncHttpResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        internal_response,
    ):
        super().__init__(request=request, internal_response=internal_response)
        self.status_code = internal_response.status
        self.headers = _CIMultiDict(internal_response.headers)  # type: ignore
        self.reason = internal_response.reason
        self.content_type = internal_response.headers.get('content-type')

    async def iter_raw(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will not decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in iter_raw_helper(AioHttpStreamDownloadGenerator, self):
            yield part
        await self.close()

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Asynchronously iterates over the response's bytes. Will decompress in the process

        :return: An async iterator of bytes from the response
        :rtype: AsyncIterator[bytes]
        """
        async for part in iter_bytes_helper(
            AioHttpStreamDownloadGenerator,
            self,
            content=self._content
        ):
            yield part
        await self.close()

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        state['internal_response'] = None  # aiohttp response are not pickable (see headers comments)
        state['headers'] = CIMultiDict(self.headers)  # MultiDictProxy is not pickable
        return state

    async def close(self) -> None:
        """Close the response.

        :return: None
        :rtype: None
        """
        self.is_closed = True
        self._internal_response.close()
        await asyncio.sleep(0)
