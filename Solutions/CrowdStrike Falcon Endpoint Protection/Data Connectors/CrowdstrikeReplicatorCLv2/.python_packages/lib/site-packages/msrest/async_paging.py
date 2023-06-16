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
import logging

_LOGGER = logging.getLogger(__name__)

class AsyncPagedMixin(AsyncIterator):

    def __init__(self, *args, **kwargs):
        """Bring async to Paging.

        "async_command" is mandatory keyword argument for this mixin to work.
        """
        self._async_get_next = kwargs.get("async_command")
        if not self._async_get_next:
            _LOGGER.debug("Paging async iterator protocol is not available for %s",
                          self.__class__.__name__)

    async def async_get(self, url):
        """Get an arbitrary page.

        This resets the iterator and then fully consumes it to return the
        specific page **only**.

        :param str url: URL to arbitrary page results.
        """
        self.reset()
        self.next_link = url
        return await self.async_advance_page()

    async def async_advance_page(self):
        if not self._async_get_next:
            raise NotImplementedError(
                "The class %s does not support async paging at the moment.",
                self.__class__.__name__
            )
        if self.next_link is None:
            raise StopAsyncIteration("End of paging")
        self._current_page_iter_index = 0
        self._response = await self._async_get_next(self.next_link)
        self._derserializer(self, self._response)
        return self.current_page

    async def __anext__(self):
        """Iterate through responses."""
        # Storing the list iterator might work out better, but there's no
        # guarantee that some code won't replace the list entirely with a copy,
        # invalidating an list iterator that might be saved between iterations.
        if self.current_page and self._current_page_iter_index < len(self.current_page):
            response = self.current_page[self._current_page_iter_index]
            self._current_page_iter_index += 1
            return response
        else:
            await self.async_advance_page()
            return await self.__anext__()
