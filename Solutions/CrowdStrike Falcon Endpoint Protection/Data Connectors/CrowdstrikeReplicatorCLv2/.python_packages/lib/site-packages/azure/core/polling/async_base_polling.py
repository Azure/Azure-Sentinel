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
from ..exceptions import HttpResponseError
from .base_polling import (
    _failed,
    BadStatus,
    BadResponse,
    OperationFailed,
    LROBasePolling,
    _raise_if_bad_http_status_and_method,
)
from ..pipeline._tools import is_rest

__all__ = ["AsyncLROBasePolling"]


class AsyncLROBasePolling(LROBasePolling):
    """A subclass or LROBasePolling that redefine "run" as async."""

    async def run(self):  # pylint:disable=invalid-overridden-method
        try:
            await self._poll()

        except BadStatus as err:
            self._status = "Failed"
            raise HttpResponseError(response=self._pipeline_response.http_response, error=err)

        except BadResponse as err:
            self._status = "Failed"
            raise HttpResponseError(
                response=self._pipeline_response.http_response,
                message=str(err),
                error=err,
            )

        except OperationFailed as err:
            raise HttpResponseError(response=self._pipeline_response.http_response, error=err)

    async def _poll(self):  # pylint:disable=invalid-overridden-method
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """
        if not self.finished():
            await self.update_status()
        while not self.finished():
            await self._delay()
            await self.update_status()

        if _failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = await self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)

    async def _sleep(self, delay):  # pylint:disable=invalid-overridden-method
        await self._transport.sleep(delay)

    async def _delay(self):  # pylint:disable=invalid-overridden-method
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        delay = self._extract_delay()
        await self._sleep(delay)

    async def update_status(self):  # pylint:disable=invalid-overridden-method
        """Update the current status of the LRO."""
        self._pipeline_response = await self.request_status(self._operation.get_polling_url())
        _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)
        self._status = self._operation.get_status(self._pipeline_response)

    async def request_status(self, status_link):  # pylint:disable=invalid-overridden-method
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: azure.core.pipeline.PipelineResponse
        """
        if self._path_format_arguments:
            status_link = self._client.format_url(status_link, **self._path_format_arguments)
        # Re-inject 'x-ms-client-request-id' while polling
        if "request_id" not in self._operation_config:
            self._operation_config["request_id"] = self._get_request_id()
        if is_rest(self._initial_response.http_response):
            # if I am a azure.core.rest.HttpResponse
            # want to keep making azure.core.rest calls
            from azure.core.rest import HttpRequest as RestHttpRequest

            request = RestHttpRequest("GET", status_link)
            return await self._client.send_request(request, _return_pipeline_response=True, **self._operation_config)
        # if I am a azure.core.pipeline.transport.HttpResponse
        request = self._client.get(status_link)

        return await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )


__all__ = ["AsyncLROBasePolling"]
