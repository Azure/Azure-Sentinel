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
from enum import Enum
from typing import (
    Optional,
    Any,
    Tuple,
    Callable,
    Dict,
    Mapping,
    Sequence,
    Generic,
    TypeVar,
    cast,
    Union,
)

from ..exceptions import HttpResponseError, DecodeError
from . import PollingMethod
from ..pipeline.policies._utils import get_retry_after
from ..pipeline._tools import is_rest
from .._enum_meta import CaseInsensitiveEnumMeta
from .. import PipelineClient
from ..pipeline import PipelineResponse, PipelineContext
from ..rest._helpers import decode_to_text, get_charset_encoding
from ..utils._utils import case_insensitive_dict
from ..pipeline.transport import (
    HttpTransport,
    HttpRequest as LegacyHttpRequest,
    HttpResponse as LegacyHttpResponse,
    AsyncHttpResponse as LegacyAsyncHttpResponse,
)
from ..rest import HttpRequest, HttpResponse, AsyncHttpResponse
from ._utils import (
    _encode_continuation_token,
    _decode_continuation_token,
    _filter_sensitive_headers,
)


HttpRequestType = Union[LegacyHttpRequest, HttpRequest]
HttpResponseType = Union[LegacyHttpResponse, HttpResponse]  # Sync only
AllHttpResponseType = Union[
    LegacyHttpResponse, HttpResponse, LegacyAsyncHttpResponse, AsyncHttpResponse
]  # Sync or async
LegacyPipelineResponseType = PipelineResponse[LegacyHttpRequest, LegacyHttpResponse]
NewPipelineResponseType = PipelineResponse[HttpRequest, HttpResponse]
PipelineResponseType = PipelineResponse[HttpRequestType, HttpResponseType]
HttpRequestTypeVar = TypeVar("HttpRequestTypeVar", bound=HttpRequestType)
HttpResponseTypeVar = TypeVar("HttpResponseTypeVar", bound=HttpResponseType)  # Sync only
AllHttpResponseTypeVar = TypeVar("AllHttpResponseTypeVar", bound=AllHttpResponseType)  # Sync or async

ABC = abc.ABC
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)
PipelineClientType = TypeVar("PipelineClientType")
HTTPResponseType_co = TypeVar("HTTPResponseType_co", covariant=True)
HTTPRequestType_co = TypeVar("HTTPRequestType_co", covariant=True)


_FINISHED = frozenset(["succeeded", "canceled", "failed"])
_FAILED = frozenset(["canceled", "failed"])
_SUCCEEDED = frozenset(["succeeded"])


class _ContinuationTokenHttpResponse:
    """A minimal HTTP response class for reconstructing responses from continuation tokens.

    This class provides just enough interface to be used with LRO polling operations
    when restoring from a continuation token.

    :param request: The HTTP request (optional, may be None if not available in the continuation token)
    :type request: ~azure.core.rest.HttpRequest or None
    :param status_code: The HTTP status code
    :type status_code: int
    :param headers: The response headers
    :type headers: dict
    :param content: The response content
    :type content: bytes
    """

    def __init__(
        self,
        request: Optional[HttpRequest],
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
    ):
        self.request = request
        self.status_code = status_code
        self.headers = case_insensitive_dict(headers)
        self._content = content

    @property
    def content(self) -> bytes:
        """Return the response content.

        :return: The response content
        :rtype: bytes
        """
        return self._content

    def text(self) -> str:
        """Return the response content as text.

        Uses the charset from Content-Type header if available, otherwise falls back
        to UTF-8 with replacement for invalid characters.

        :return: The response content as text
        :rtype: str
        """
        encoding = get_charset_encoding(self)
        return decode_to_text(encoding, self._content)


def _get_content(response: AllHttpResponseType) -> bytes:
    """Get the content of this response. This is designed specifically to avoid
    a warning of mypy for body() access, as this method is deprecated.

    :param response: The response object.
    :type response: any
    :return: The content of this response.
    :rtype: bytes
    """
    if isinstance(response, (LegacyHttpResponse, LegacyAsyncHttpResponse)):
        return response.body()
    return response.content


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
    """Exception raised when status is invalid."""


class BadResponse(Exception):
    """Exception raised when response is invalid."""


class OperationFailed(Exception):
    """Exception raised when operation failed or canceled."""


def _as_json(response: AllHttpResponseType) -> Dict[str, Any]:
    """Assuming this is not empty, return the content as JSON.

    Result/exceptions is not determined if you call this method without testing _is_empty.

    :param response: The response object.
    :type response: any
    :return: The content of this response as dict.
    :rtype: dict
    :raises DecodeError: If response body contains invalid json data.
    """
    try:
        return json.loads(response.text())
    except ValueError as err:
        raise DecodeError("Error occurred in deserializing the response body.") from err


def _raise_if_bad_http_status_and_method(response: AllHttpResponseType) -> None:
    """Check response status code is valid.

    Must be 200, 201, 202, or 204.

    :param response: The response object.
    :type response: any
    :raises ~azure.core.polling.base_polling.BadStatus: If invalid status.
    """
    code = response.status_code
    if code in {200, 201, 202, 204}:
        return
    raise BadStatus("Invalid return status {!r} for {!r} operation".format(code, response.request.method))


def _is_empty(response: AllHttpResponseType) -> bool:
    """Check if response body contains meaningful content.

    :param response: The response object.
    :type response: any
    :return: True if response body is empty, False otherwise.
    :rtype: bool
    """
    return not bool(_get_content(response))


class LongRunningOperation(ABC, Generic[HTTPRequestType_co, HTTPResponseType_co]):
    """Protocol to implement for a long running operation algorithm."""

    @abc.abstractmethod
    def can_poll(
        self,
        pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co],
    ) -> bool:
        """Answer if this polling method could be used.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: True if this polling method could be used, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_polling_url(self) -> str:
        """Return the polling URL.

        :return: The polling URL.
        :rtype: str
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set_initial_status(
        self,
        pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co],
    ) -> str:
        """Process first response after initiating long running operation.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The initial status.
        :rtype: str
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_status(
        self,
        pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co],
    ) -> str:
        """Return the status string extracted from this response.

        :param pipeline_response: The response object.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The status string.
        :rtype: str
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_final_get_url(
        self,
        pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co],
    ) -> Optional[str]:
        """If a final GET is needed, returns the URL.

        :param pipeline_response: Success REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The URL to the final GET, or None if no final GET is needed.
        :rtype: str or None
        """
        raise NotImplementedError()


class _LroOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Known LRO options from Swagger."""

    FINAL_STATE_VIA = "final-state-via"


class _FinalStateViaOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Possible final-state-via options."""

    AZURE_ASYNC_OPERATION_FINAL_STATE = "azure-async-operation"
    LOCATION_FINAL_STATE = "location"
    OPERATION_LOCATION_FINAL_STATE = "operation-location"


class OperationResourcePolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):
    """Implements a operation resource polling, typically from Operation-Location.

    :param str operation_location_header: Name of the header to return operation format (default 'operation-location')
    :keyword dict[str, any] lro_options: Additional options for LRO. For more information, see
     https://aka.ms/azsdk/autorest/openapi/lro-options
    """

    _async_url: str
    """Url to resource monitor (AzureAsyncOperation or Operation-Location)"""

    _location_url: Optional[str]
    """Location header if present"""

    _request: Any
    """The initial request done"""

    def __init__(
        self, operation_location_header: str = "operation-location", *, lro_options: Optional[Dict[str, Any]] = None
    ):
        self._operation_location_header = operation_location_header
        self._location_url = None
        self._lro_options = lro_options or {}

    def can_poll(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> bool:
        """Check if status monitor header (e.g. Operation-Location) is present.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: True if this polling method could be used, False otherwise.
        :rtype: bool
        """
        response = pipeline_response.http_response
        return self._operation_location_header in response.headers

    def get_polling_url(self) -> str:
        """Return the polling URL.

        Will extract it from the defined header to read (e.g. Operation-Location)

        :return: The polling URL.
        :rtype: str
        """
        return self._async_url

    def get_final_get_url(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> Optional[str]:
        """If a final GET is needed, returns the URL.

        :param pipeline_response: Success REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The URL to the final GET, or None if no final GET is needed.
        :rtype: str or None
        """
        if (
            self._lro_options.get(_LroOption.FINAL_STATE_VIA) == _FinalStateViaOption.LOCATION_FINAL_STATE
            and self._location_url
        ):
            return self._location_url
        if (
            self._lro_options.get(_LroOption.FINAL_STATE_VIA)
            in [
                _FinalStateViaOption.AZURE_ASYNC_OPERATION_FINAL_STATE,
                _FinalStateViaOption.OPERATION_LOCATION_FINAL_STATE,
            ]
            and self._request.method == "POST"
        ):
            return None
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

    def set_initial_status(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> str:
        """Process first response after initiating long running operation.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The initial status.
        :rtype: str
        """
        self._request = pipeline_response.http_response.request
        response = pipeline_response.http_response

        self._set_async_url_if_present(response)

        if response.status_code in {200, 201, 202, 204} and self._async_url:
            # Check if we can extract status from initial response, if present
            try:
                return self.get_status(pipeline_response)
            # Wide catch, it may not even be JSON at all, deserialization is lenient
            except Exception:  # pylint: disable=broad-except
                pass
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def _set_async_url_if_present(self, response: AllHttpResponseTypeVar) -> None:
        self._async_url = response.headers[self._operation_location_header]

        location_url = response.headers.get("location")
        if location_url:
            self._location_url = location_url

    def get_status(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> str:
        """Process the latest status update retrieved from an "Operation-Location" header.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The status string.
        :rtype: str
        :raises ~azure.core.polling.base_polling.BadResponse: if response has no body, or body does not contain status.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse("The response from long running operation does not contain a body.")

        body = _as_json(response)
        status = body.get("status")
        if not status:
            raise BadResponse("No status found in body")
        return status


class LocationPolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):
    """Implements a Location polling."""

    _location_url: str
    """Location header"""

    def can_poll(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> bool:
        """True if contains a Location header

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: True if this polling method could be used, False otherwise.
        :rtype: bool
        """
        response = pipeline_response.http_response
        return "location" in response.headers

    def get_polling_url(self) -> str:
        """Return the Location header value.

        :return: The polling URL.
        :rtype: str
        """
        return self._location_url

    def get_final_get_url(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> Optional[str]:
        """If a final GET is needed, returns the URL.

        Always return None for a Location polling.

        :param pipeline_response: Success REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: Always None for this implementation.
        :rtype: None
        """
        return None

    def set_initial_status(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> str:
        """Process first response after initiating long running operation.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The initial status.
        :rtype: str
        """
        response = pipeline_response.http_response

        self._location_url = response.headers["location"]

        if response.status_code in {200, 201, 202, 204} and self._location_url:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def get_status(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> str:
        """Return the status string extracted from this response.

        For Location polling, it means the status monitor returns 202.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The status string.
        :rtype: str
        """
        response = pipeline_response.http_response
        if "location" in response.headers:
            self._location_url = response.headers["location"]

        return "InProgress" if response.status_code == 202 else "Succeeded"


class StatusCheckPolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):
    """Should be the fallback polling, that don't poll but exit successfully
    if not other polling are detected and status code is 2xx.
    """

    def can_poll(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> bool:
        """Answer if this polling method could be used.

        For this implementation, always True.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: True if this polling method could be used, False otherwise.
        :rtype: bool
        """
        return True

    def get_polling_url(self) -> str:
        """Return the polling URL.

        This is not implemented for this polling, since we're never supposed to loop.

        :return: The polling URL.
        :rtype: str
        """
        raise ValueError("This polling doesn't support polling url")

    def set_initial_status(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> str:
        """Process first response after initiating long running operation.

        Will succeed immediately.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The initial status.
        :rtype: str
        """
        return "Succeeded"

    def get_status(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> str:
        """Return the status string extracted from this response.

        Only possible status is success.

        :param pipeline_response: Initial REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The status string.
        :rtype: str
        """
        return "Succeeded"

    def get_final_get_url(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> Optional[str]:
        """If a final GET is needed, returns the URL.

        :param pipeline_response: Success REST call response.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :rtype: str
        :return: Always None for this implementation.
        """
        return None


class _SansIOLROBasePolling(
    Generic[
        PollingReturnType_co,
        PipelineClientType,
        HttpRequestTypeVar,
        AllHttpResponseTypeVar,
    ]
):  # pylint: disable=too-many-instance-attributes
    """A base class that has no opinion on IO, to help mypy be accurate.

    :param float timeout: Default polling internal in absence of Retry-After header, in seconds.
    :param list[LongRunningOperation] lro_algorithms: Ordered list of LRO algorithms to use.
    :param lro_options: Additional options for LRO. For more information, see the algorithm's docstring.
    :type lro_options: dict[str, any]
    :param path_format_arguments: A dictionary of the format arguments to be used to format the URL.
    :type path_format_arguments: dict[str, str]
    """

    _deserialization_callback: Callable[[Any], PollingReturnType_co]
    """The deserialization callback that returns the final instance."""

    _operation: LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]
    """The algorithm this poller has decided to use. Will loop through 'can_poll' of the input algorithms to decide."""

    _status: str
    """Hold the current status of this poller"""

    _client: PipelineClientType
    """The Azure Core Pipeline client used to make request."""

    def __init__(
        self,
        timeout: float = 30,
        lro_algorithms: Optional[Sequence[LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]]] = None,
        lro_options: Optional[Dict[str, Any]] = None,
        path_format_arguments: Optional[Dict[str, str]] = None,
        **operation_config: Any
    ):
        self._lro_algorithms = lro_algorithms or [
            OperationResourcePolling(lro_options=lro_options),
            LocationPolling(),
            StatusCheckPolling(),
        ]

        self._timeout = timeout
        self._operation_config = operation_config
        self._lro_options = lro_options
        self._path_format_arguments = path_format_arguments

    def initialize(
        self,
        client: PipelineClientType,
        initial_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
        deserialization_callback: Callable[
            [PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]],
            PollingReturnType_co,
        ],
    ) -> None:
        """Set the initial status of this LRO.

        :param client: The Azure Core Pipeline client used to make request.
        :type client: ~azure.core.pipeline.PipelineClient
        :param initial_response: The initial response for the call.
        :type initial_response: ~azure.core.pipeline.PipelineResponse
        :param deserialization_callback: A callback function to deserialize the final response.
        :type deserialization_callback: callable
        :raises ~azure.core.HttpResponseError: If initial status is incorrect LRO state
        """
        self._client = client
        self._pipeline_response = (  # pylint: disable=attribute-defined-outside-init
            self._initial_response  # pylint: disable=attribute-defined-outside-init
        ) = initial_response
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
            raise HttpResponseError(response=initial_response.http_response, error=err) from err
        except BadResponse as err:
            self._status = "Failed"
            raise HttpResponseError(response=initial_response.http_response, message=str(err), error=err) from err
        except OperationFailed as err:
            raise HttpResponseError(response=initial_response.http_response, error=err) from err

    def _filter_headers_for_continuation_token(self, headers: Mapping[str, str]) -> Dict[str, str]:
        """Filter headers to include in the continuation token.

        Subclasses can override this method to include additional headers needed
        for their specific LRO implementation.

        :param headers: The response headers to filter.
        :type headers: Mapping[str, str]
        :return: A filtered dictionary of headers to include in the continuation token.
        :rtype: dict[str, str]
        """
        return _filter_sensitive_headers(headers)

    def get_continuation_token(self) -> str:
        """Get a continuation token that can be used to recreate this poller.

        :rtype: str
        :return: An opaque continuation token.
        :raises ValueError: If the initial response is not set.
        """
        response = self._initial_response.http_response
        request = response.request
        # Serialize the essential parts of the PipelineResponse to JSON.
        if request:
            request_headers = {}
            # Preserve x-ms-client-request-id for request correlation
            if "x-ms-client-request-id" in request.headers:
                request_headers["x-ms-client-request-id"] = request.headers["x-ms-client-request-id"]
            request_state = {
                "method": request.method,
                "url": request.url,
                "headers": request_headers,
            }
        else:
            request_state = None
        # Get response content, handling the case where it might not be read yet
        try:
            content = _get_content(response) or b""
        except Exception:  # pylint: disable=broad-except
            content = b""
        # Get deserialized data from context if available (optimization).
        # If context doesn't have it, fall back to parsing the response body directly.
        # Note: deserialized_data is only included if it's JSON-serializable.
        # Non-JSON-serializable types (e.g., XML ElementTree) are skipped and set to None.
        # In such cases, the data can still be re-parsed from the raw content bytes.
        deserialized_data = None
        raw_deserialized = None
        if self._initial_response.context is not None:
            raw_deserialized = self._initial_response.context.get("deserialized_data")
        # Fallback: try to get deserialized data from the response body if context didn't have it
        if raw_deserialized is None and content:
            try:
                raw_deserialized = json.loads(content)
            except (json.JSONDecodeError, ValueError, TypeError):
                # Response body is not valid JSON, leave as None
                pass
        if raw_deserialized is not None:
            try:
                # Test if the data is JSON-serializable
                json.dumps(raw_deserialized)
                deserialized_data = raw_deserialized
            except (TypeError, ValueError):
                # Skip non-JSON-serializable data (e.g., XML ElementTree objects)
                deserialized_data = None
        state = {
            "request": request_state,
            "response": {
                "status_code": response.status_code,
                "headers": self._filter_headers_for_continuation_token(response.headers),
                "content": base64.b64encode(content).decode("ascii"),
            },
            "context": {
                "deserialized_data": deserialized_data,
            },
        }
        return _encode_continuation_token(state)

    @classmethod
    def from_continuation_token(
        cls, continuation_token: str, **kwargs: Any
    ) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]:
        """Recreate the poller from a continuation token.

        :param continuation_token: The continuation token to recreate the poller.
        :type continuation_token: str
        :return: A tuple containing the client, the initial response, and the deserialization callback.
        :rtype: tuple[~azure.core.PipelineClient, ~azure.core.pipeline.PipelineResponse, callable]
        :raises ValueError: If the continuation token is invalid or if 'client' or
            'deserialization_callback' are not provided.
        """
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from None

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from None

        state = _decode_continuation_token(continuation_token)
        # Reconstruct HttpRequest if present
        request_state = state.get("request")
        http_request = None
        if request_state is not None:
            http_request = HttpRequest(
                method=request_state["method"],
                url=request_state["url"],
                headers=request_state.get("headers", {}),
            )
        # Reconstruct HttpResponse using the minimal response class
        response_state = state["response"]
        http_response = _ContinuationTokenHttpResponse(
            request=http_request,
            status_code=response_state["status_code"],
            headers=response_state["headers"],
            content=base64.b64decode(response_state["content"]),
        )
        # Reconstruct PipelineResponse
        context = PipelineContext(client._pipeline._transport)  # pylint: disable=protected-access
        context_state = state.get("context", {})
        if context_state.get("deserialized_data") is not None:
            context["deserialized_data"] = context_state["deserialized_data"]
        initial_response = PipelineResponse(
            http_request=http_request,
            http_response=http_response,
            context=context,
        )
        return client, initial_response, deserialization_callback

    def status(self) -> str:
        """Return the current status as a string.

        :rtype: str
        :return: The current status.
        """
        if not self._operation:
            raise ValueError("set_initial_status was never called. Did you give this instance to a poller?")
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?

        :rtype: bool
        :return: True if finished, False otherwise.
        """
        return _finished(self.status())

    def resource(self) -> PollingReturnType_co:
        """Return the built resource.

        :rtype: any
        :return: The built resource.
        """
        return self._parse_resource(self._pipeline_response)

    def _parse_resource(
        self,
        pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar],
    ) -> PollingReturnType_co:
        """Assuming this response is a resource, use the deserialization callback to parse it.
        If body is empty, assuming no resource to return.

        :param pipeline_response: The response object.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The parsed resource.
        :rtype: any
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            return self._deserialization_callback(pipeline_response)

        # This "type ignore" has been discussed with architects.
        # We have a typing problem that if the Swagger/TSP describes a return type (PollingReturnType_co is not None),
        # BUT the returned payload is actually empty, we don't want to fail, but return None.
        # To be clean, we would have to make the polling return type Optional "just in case the Swagger/TSP is wrong".
        # This is reducing the quality and the value of the typing annotations
        # for a case that is not supposed to happen in the first place. So we decided to ignore the type error here.
        return None  # type: ignore

    def _get_request_id(self) -> str:
        return self._pipeline_response.http_response.request.headers["x-ms-client-request-id"]

    def _extract_delay(self) -> float:
        delay = get_retry_after(self._pipeline_response)
        if delay:
            return delay
        return self._timeout


class LROBasePolling(
    _SansIOLROBasePolling[
        PollingReturnType_co,
        PipelineClient[HttpRequestTypeVar, HttpResponseTypeVar],
        HttpRequestTypeVar,
        HttpResponseTypeVar,
    ],
    PollingMethod[PollingReturnType_co],
):
    """A base LRO poller.

    This assumes a basic flow:
    - I analyze the response to decide the polling approach
    - I poll
    - I ask the final resource depending of the polling approach

    If your polling need are more specific, you could implement a PollingMethod directly
    """

    _initial_response: PipelineResponse[HttpRequestTypeVar, HttpResponseTypeVar]
    """Store the initial response."""

    _pipeline_response: PipelineResponse[HttpRequestTypeVar, HttpResponseTypeVar]
    """Store the latest received HTTP response, initialized by the first answer."""

    @property
    def _transport(self) -> HttpTransport[HttpRequestTypeVar, HttpResponseTypeVar]:
        return self._client._pipeline._transport  # pylint: disable=protected-access

    def __getattribute__(self, name: str) -> Any:
        """Find the right method for the job.

        This contains a workaround for azure-mgmt-core 1.0.0 to 1.4.0, where the MRO
        is changing when azure-core was refactored in 1.27.0. The MRO change was causing
        AsyncARMPolling to look-up the wrong methods and find the non-async ones.

        :param str name: The name of the attribute to retrieve.
        :rtype: Any
        :return: The attribute value.
        """
        cls = object.__getattribute__(self, "__class__")
        if cls.__name__ == "AsyncARMPolling" and name in [
            "run",
            "update_status",
            "request_status",
            "_sleep",
            "_delay",
            "_poll",
        ]:
            return getattr(super(LROBasePolling, self), name)
        return super().__getattribute__(name)

    def run(self) -> None:
        try:
            self._poll()

        except BadStatus as err:
            self._status = "Failed"
            raise HttpResponseError(response=self._pipeline_response.http_response, error=err) from err

        except BadResponse as err:
            self._status = "Failed"
            raise HttpResponseError(
                response=self._pipeline_response.http_response,
                message=str(err),
                error=err,
            ) from err

        except OperationFailed as err:
            raise HttpResponseError(response=self._pipeline_response.http_response, error=err) from err

    def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises ~azure.core.polling.base_polling.OperationFailed: If operation status 'Failed' or 'Canceled'.
        :raises ~azure.core.polling.base_polling.BadStatus: If response status invalid.
        :raises ~azure.core.polling.base_polling.BadResponse: If response invalid.
        """
        if not self.finished():
            self.update_status()
        while not self.finished():
            self._delay()
            self.update_status()

        if _failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)

    def _sleep(self, delay: float) -> None:
        self._transport.sleep(delay)

    def _delay(self) -> None:
        """Check for a 'retry-after' header to set timeout,
        otherwise use configured timeout.
        """
        delay = self._extract_delay()
        self._sleep(delay)

    def update_status(self) -> None:
        """Update the current status of the LRO."""
        self._pipeline_response = self.request_status(self._operation.get_polling_url())
        _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)
        self._status = self._operation.get_status(self._pipeline_response)

    def request_status(self, status_link: str) -> PipelineResponse[HttpRequestTypeVar, HttpResponseTypeVar]:
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :param str status_link: The URL to poll.
        :rtype: azure.core.pipeline.PipelineResponse
        :return: The response of the status request.
        """
        if self._path_format_arguments:
            status_link = self._client.format_url(status_link, **self._path_format_arguments)
        # Re-inject 'x-ms-client-request-id' while polling
        if "request_id" not in self._operation_config:
            self._operation_config["request_id"] = self._get_request_id()

        if is_rest(self._initial_response.http_response):
            rest_request = cast(HttpRequestTypeVar, HttpRequest("GET", status_link))
            # Need a cast, as "_return_pipeline_response" mutate the return type, and that return type is not
            # declared in the typing of "send_request"
            return cast(
                PipelineResponse[HttpRequestTypeVar, HttpResponseTypeVar],
                self._client.send_request(rest_request, _return_pipeline_response=True, **self._operation_config),
            )

        # Legacy HttpRequest and HttpResponse from azure.core.pipeline.transport
        # casting things here, as we don't want the typing system to know
        # about the legacy APIs.
        request = cast(HttpRequestTypeVar, self._client.get(status_link))
        return cast(
            PipelineResponse[HttpRequestTypeVar, HttpResponseTypeVar],
            self._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **self._operation_config
            ),
        )


__all__ = [
    "BadResponse",
    "BadStatus",
    "OperationFailed",
    "LongRunningOperation",
    "OperationResourcePolling",
    "LocationPolling",
    "StatusCheckPolling",
    "LROBasePolling",
]
