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
import base64
import json
from typing import TYPE_CHECKING, Optional, Any, Union

from ..exceptions import HttpResponseError, DecodeError
from . import PollingMethod
from ..pipeline.policies._utils import get_retry_after
from ..pipeline._tools import is_rest

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.transport import (
        HttpResponse,
        AsyncHttpResponse,
        HttpRequest,
    )

    ResponseType = Union[HttpResponse, AsyncHttpResponse]
    PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]


try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

_FINISHED = frozenset(["succeeded", "canceled", "failed"])
_FAILED = frozenset(["canceled", "failed"])
_SUCCEEDED = frozenset(["succeeded"])

def _finished(status):
    if hasattr(status, "value"):
        status = status.value
    return str(status).lower() in _FINISHED


def _failed(status):
    if hasattr(status, "value"):
        status = status.value
    return str(status).lower() in _FAILED


def _succeeded(status):
    if hasattr(status, "value"):
        status = status.value
    return str(status).lower() in _SUCCEEDED


class BadStatus(Exception):
    pass


class BadResponse(Exception):
    pass


class OperationFailed(Exception):
    pass


def _as_json(response):
    # type: (ResponseType) -> dict
    """Assuming this is not empty, return the content as JSON.

    Result/exceptions is not determined if you call this method without testing _is_empty.

    :raises: DecodeError if response body contains invalid json data.
    """
    try:
        return json.loads(response.text())
    except ValueError:
        raise DecodeError("Error occurred in deserializing the response body.")


def _raise_if_bad_http_status_and_method(response):
    # type: (ResponseType) -> None
    """Check response status code is valid.

    Must be 200, 201, 202, or 204.

    :raises: BadStatus if invalid status.
    """
    code = response.status_code
    if code in {200, 201, 202, 204}:
        return
    raise BadStatus(
        "Invalid return status {!r} for {!r} operation".format(
            code, response.request.method
        )
    )


def _is_empty(response):
    # type: (ResponseType) -> bool
    """Check if response body contains meaningful content.

    :rtype: bool
    """
    return not bool(response.body())


class LongRunningOperation(ABC):
    """LongRunningOperation
    Provides default logic for interpreting operation responses
    and status updates.

    :param azure.core.pipeline.PipelineResponse response: The initial pipeline response.
    :param callable deserialization_callback: The deserialization callaback.
    :param dict lro_options: LRO options.
    :param kwargs: Unused for now
    """

    @abc.abstractmethod
    def can_poll(self, pipeline_response):
        # type: (PipelineResponseType) -> bool
        """Answer if this polling method could be used.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Return the status string extracted from this response."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        raise NotImplementedError()


class OperationResourcePolling(LongRunningOperation):
    """Implements a operation resource polling, typically from Operation-Location.

    :param str operation_location_header: Name of the header to return operation format (default 'operation-location')
    """

    def __init__(self, operation_location_header="operation-location"):
        self._operation_location_header = operation_location_header

        # Store the initial URLs
        self._async_url = None
        self._location_url = None
        self._request = None

    def can_poll(self, pipeline_response):
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        return self._operation_location_header in response.headers

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._async_url

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            # https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md#target-resource-location
            resource_location = body.get("resourceLocation")
            if resource_location:
                return resource_location

        if self._request.method in {"PUT", "PATCH"}:
            return self._request.url

        if self._request.method == "POST" and self._location_url:
            return self._location_url

        return None

    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        self._request = pipeline_response.http_response.request
        response = pipeline_response.http_response

        self._set_async_url_if_present(response)

        if response.status_code in {200, 201, 202, 204} and self._async_url:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def _set_async_url_if_present(self, response):
        # type: (ResponseType) -> None
        self._async_url = response.headers[self._operation_location_header]

        location_url = response.headers.get("location")
        if location_url:
            self._location_url = location_url

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process the latest status update retrieved from an "Operation-Location" header.

        :param azure.core.pipeline.PipelineResponse response: The response to extract the status.
        :raises: BadResponse if response has no body, or body does not contain status.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse(
                "The response from long running operation does not contain a body."
            )

        body = _as_json(response)
        status = body.get("status")
        if not status:
            raise BadResponse("No status found in body")
        return status


class LocationPolling(LongRunningOperation):
    """Implements a Location polling.
    """

    def __init__(self):
        self._location_url = None

    def can_poll(self, pipeline_response):
        # type: (PipelineResponseType) -> bool
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        return "location" in response.headers

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._location_url

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        return None

    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        response = pipeline_response.http_response

        self._location_url = response.headers["location"]

        if response.status_code in {200, 201, 202, 204} and self._location_url:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse response: latest REST call response.
        :raises: BadResponse if response has no body and not status 202.
        """
        response = pipeline_response.http_response
        if "location" in response.headers:
            self._location_url = response.headers["location"]

        return "InProgress" if response.status_code == 202 else "Succeeded"


class StatusCheckPolling(LongRunningOperation):
    """Should be the fallback polling, that don't poll but exit successfully
    if not other polling are detected and status code is 2xx.
    """

    def can_poll(self, pipeline_response):
        # type: (PipelineResponseType) -> bool
        """Answer if this polling method could be used.
        """
        return True

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        raise ValueError("This polling doesn't support polling")

    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running
        operation and set self.status attribute.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        return "Succeeded"

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        return "Succeeded"

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        return None


class LROBasePolling(PollingMethod):  # pylint: disable=too-many-instance-attributes
    """A base LRO poller.

    This assumes a basic flow:
    - I analyze the response to decide the polling approach
    - I poll
    - I ask the final resource depending of the polling approach

    If your polling need are more specific, you could implement a PollingMethod directly
    """

    def __init__(
        self,
        timeout=30,
        lro_algorithms=None,
        lro_options=None,
        path_format_arguments=None,
        **operation_config
    ):
        self._lro_algorithms = lro_algorithms or [
            OperationResourcePolling(),
            LocationPolling(),
            StatusCheckPolling(),
        ]

        self._timeout = timeout
        self._client = None  # Will hold the Pipelineclient
        self._operation = None  # Will hold an instance of LongRunningOperation
        self._initial_response = None  # Will hold the initial response
        self._pipeline_response = None  # Will hold latest received response
        self._deserialization_callback = None  # Will hold the deserialization callback
        self._operation_config = operation_config
        self._lro_options = lro_options
        self._path_format_arguments = path_format_arguments
        self._status = None

    def status(self):
        """Return the current status as a string.
        :rtype: str
        """
        if not self._operation:
            raise ValueError(
                "set_initial_status was never called. Did you give this instance to a poller?"
            )
        return self._status

    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return _finished(self.status())

    def resource(self):
        """Return the built resource.
        """
        return self._parse_resource(self._pipeline_response)

    @property
    def _transport(self):
        return self._client._pipeline._transport  # pylint: disable=protected-access

    def initialize(self, client, initial_response, deserialization_callback):
        """Set the initial status of this LRO.

        :param initial_response: The initial response of the poller
        :raises: HttpResponseError if initial status is incorrect LRO state
        """
        self._client = client
        self._pipeline_response = self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback

        for operation in self._lro_algorithms:
            if operation.can_poll(initial_response):
                self._operation = operation
                break
        else:
            raise BadResponse("Unable to find status link for polling.")

        try:
            _raise_if_bad_http_status_and_method(self._initial_response.http_response)
            self._status = self._operation.set_initial_status(initial_response)

        except BadStatus as err:
            self._status = "Failed"
            raise HttpResponseError(response=initial_response.http_response, error=err)
        except BadResponse as err:
            self._status = "Failed"
            raise HttpResponseError(
                response=initial_response.http_response, message=str(err), error=err
            )
        except OperationFailed as err:
            raise HttpResponseError(response=initial_response.http_response, error=err)

    def get_continuation_token(self):
        # type() -> str
        import pickle
        return base64.b64encode(pickle.dumps(self._initial_response)).decode('ascii')

    @classmethod
    def from_continuation_token(cls, continuation_token, **kwargs):
        # type(str, Any) -> Tuple
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token")

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token")

        import pickle
        initial_response = pickle.loads(base64.b64decode(continuation_token))   # nosec
        # Restore the transport in the context
        initial_response.context.transport = client._pipeline._transport  # pylint: disable=protected-access
        return client, initial_response, deserialization_callback

    def run(self):
        try:
            self._poll()

        except BadStatus as err:
            self._status = "Failed"
            raise HttpResponseError(
                response=self._pipeline_response.http_response,
                error=err
            )

        except BadResponse as err:
            self._status = "Failed"
            raise HttpResponseError(
                response=self._pipeline_response.http_response,
                message=str(err),
                error=err
            )

        except OperationFailed as err:
            raise HttpResponseError(
                response=self._pipeline_response.http_response,
                error=err
            )

    def _poll(self):
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            self._delay()
            self.update_status()

        if _failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)

    def _parse_resource(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[Any]
        """Assuming this response is a resource, use the deserialization callback to parse it.
        If body is empty, assuming no resource to return.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            return self._deserialization_callback(pipeline_response)
        return None

    def _sleep(self, delay):
        self._transport.sleep(delay)

    def _extract_delay(self):
        if self._pipeline_response is None:
            return None
        delay = get_retry_after(self._pipeline_response)
        if delay:
            return delay
        return self._timeout

    def _delay(self):
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        delay = self._extract_delay()
        self._sleep(delay)

    def update_status(self):
        """Update the current status of the LRO.
        """
        self._pipeline_response = self.request_status(self._operation.get_polling_url())
        _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)
        self._status = self._operation.get_status(self._pipeline_response)

    def _get_request_id(self):
        return self._pipeline_response.http_response.request.headers[
            "x-ms-client-request-id"
        ]

    def request_status(self, status_link):
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
            return self._client.send_request(
                request, _return_pipeline_response=True, **self._operation_config
            )
        # if I am a azure.core.pipeline.transport.HttpResponse
        request = self._client.get(status_link)
        return self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )


__all__ = [
    'BadResponse',
    'BadStatus',
    'OperationFailed',
    'LongRunningOperation',
    'OperationResourcePolling',
    'LocationPolling',
    'StatusCheckPolling',
    'LROBasePolling',
]
