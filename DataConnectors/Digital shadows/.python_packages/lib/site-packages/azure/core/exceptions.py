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

import json
import logging
import sys

from typing import Callable, Any, Dict, Optional, List, Union, Type, TYPE_CHECKING

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from azure.core.pipeline.transport._base import _HttpResponseBase


__all__ = [
    "AzureError",
    "ServiceRequestError",
    "ServiceResponseError",
    "HttpResponseError",
    "DecodeError",
    "ResourceExistsError",
    "ResourceNotFoundError",
    "ClientAuthenticationError",
    "ResourceModifiedError",
    "ResourceNotModifiedError",
    "TooManyRedirectsError",
    "ODataV4Format",
    "ODataV4Error",
]


def raise_with_traceback(exception, *args, **kwargs):
    # type: (Callable, Any, Any) -> None
    """Raise exception with a specified traceback.
    This MUST be called inside a "except" clause.

    :param Exception exception: Error type to be raised.
    :param args: Any additional args to be included with exception.
    :keyword str message: Message to be associated with the exception. If omitted, defaults to an empty string.
    """
    message = kwargs.pop("message", "")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    # If not called inside a "except", exc_type will be None. Assume it will not happen
    if exc_type is None:
        raise ValueError("raise_with_traceback can only be used in except clauses")
    exc_msg = "{}, {}: {}".format(message, exc_type.__name__, exc_value)
    error = exception(exc_msg, *args, **kwargs)
    try:
        raise error.with_traceback(exc_traceback)
    except AttributeError:
        error.__traceback__ = exc_traceback
        raise error

class ErrorMap(object):
    """Error Map class. To be used in map_error method, behaves like a dictionary.
    It returns the error type if it is found in custom_error_map. Or return default_error

    :param dict custom_error_map: User-defined error map, it is used to map status codes to error types.
    :keyword error default_error: Default error type. It is returned if the status code is not found in custom_error_map
    """
    def __init__(self, custom_error_map=None, **kwargs):
        self._custom_error_map = custom_error_map or {}
        self._default_error = kwargs.pop("default_error", None)

    def get(self, key):
        ret = self._custom_error_map.get(key)
        if ret:
            return ret
        return self._default_error

def map_error(status_code, response, error_map):
    if not error_map:
        return
    error_type = error_map.get(status_code)
    if not error_type:
        return
    error = error_type(response=response)
    raise error


class ODataV4Format(object):
    """Class to describe OData V4 error format.

    http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091

    :param dict json_object: A Python dict representing a ODataV4 JSON
    :ivar str ~.code: Its value is a service-defined error code.
     This code serves as a sub-status for the HTTP error code specified in the response.
    :ivar str message: Human-readable, language-dependent representation of the error.
    :ivar str target: The target of the particular error (for example, the name of the property in error).
     This field is optional and may be None.
    :ivar list[ODataV4Format] details: Array of ODataV4Format instances that MUST contain name/value pairs
     for code and message, and MAY contain a name/value pair for target, as described above.
    :ivar dict innererror: An object. The contents of this object are service-defined.
     Usually this object contains information that will help debug the service.
    """
    CODE_LABEL = "code"
    MESSAGE_LABEL = "message"
    TARGET_LABEL = "target"
    DETAILS_LABEL = "details"
    INNERERROR_LABEL = "innererror"

    def __init__(self, json_object):
        if "error" in json_object:
            json_object = json_object["error"]
        cls = self.__class__  # type: Type[ODataV4Format]

        # Required fields, but assume they could be missing still to be robust
        self.code = json_object.get(cls.CODE_LABEL)  # type: Optional[str]
        self.message = json_object.get(cls.MESSAGE_LABEL)  # type: Optional[str]

        if not (self.code or self.message):
            raise ValueError("Impossible to extract code/message from received JSON:\n"+json.dumps(json_object))

        # Optional fields
        self.target = json_object.get(cls.TARGET_LABEL)  # type: Optional[str]

        # details is recursive of this very format
        self.details = []  # type: List[ODataV4Format]
        for detail_node in json_object.get(cls.DETAILS_LABEL, []):
            try:
                self.details.append(self.__class__(detail_node))
            except Exception:  # pylint: disable=broad-except
                pass

        self.innererror = json_object.get(cls.INNERERROR_LABEL, {})  # type: Dict[str, Any]

    @property
    def error(self):
        import warnings

        warnings.warn(
            "error.error from azure exceptions is deprecated, just simply use 'error' once",
            DeprecationWarning,
        )
        return self

    def __str__(self):
        return "({}) {}".format(self.code, self.message)

    def message_details(self):
        """Return a detailled string of the error.
        """
        # () -> str
        error_str = "Code: {}".format(self.code)
        error_str += "\nMessage: {}".format(self.message)
        if self.target:
            error_str += "\nTarget: {}".format(self.target)

        if self.details:
            error_str += "\nException Details:"
            for error_obj in self.details:
                # Indent for visibility
                error_str += "\n".join("\t" + s for s in str(error_obj).splitlines())

        if self.innererror:
            error_str += "\nInner error: {}".format(
                json.dumps(self.innererror, indent=4)
            )
        return error_str


class AzureError(Exception):
    """Base exception for all errors.

    :param message: The message object stringified as 'message' attribute
    :keyword error: The original exception if any
    :paramtype error: Exception

    :ivar inner_exception: The exception passed with the 'error' kwarg
    :vartype inner_exception: Exception
    :ivar exc_type: The exc_type from sys.exc_info()
    :ivar exc_value: The exc_value from sys.exc_info()
    :ivar exc_traceback: The exc_traceback from sys.exc_info()
    :ivar exc_msg: A string formatting of message parameter, exc_type and exc_value
    :ivar str message: A stringified version of the message parameter
    :ivar str continuation_token: A token reference to continue an incomplete operation. This value is optional
     and will be `None` where continuation is either unavailable or not applicable.
    """

    def __init__(self, message, *args, **kwargs):
        self.inner_exception = kwargs.get("error")
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        self.exc_type = (
            self.exc_type.__name__ if self.exc_type else type(self.inner_exception)
        )
        self.exc_msg = "{}, {}: {}".format(message, self.exc_type, self.exc_value)
        self.message = str(message)
        self.continuation_token = kwargs.get('continuation_token')
        super(AzureError, self).__init__(self.message, *args)

    def raise_with_traceback(self):
        try:
            raise super(AzureError, self).with_traceback(self.exc_traceback)
        except AttributeError:
            self.__traceback__ = self.exc_traceback
            raise self


class ServiceRequestError(AzureError):
    """An error occurred while attempt to make a request to the service.
    No request was sent.
    """


class ServiceResponseError(AzureError):
    """The request was sent, but the client failed to understand the response.
    The connection may have timed out. These errors can be retried for idempotent or
    safe operations"""

class ServiceRequestTimeoutError(ServiceRequestError):
    """Error raised when timeout happens"""

class ServiceResponseTimeoutError(ServiceResponseError):
    """Error raised when timeout happens"""

class HttpResponseError(AzureError):
    """A request was made, and a non-success status code was received from the service.

    :param message: HttpResponse's error message
    :type message: string
    :param response: The response that triggered the exception.
    :type response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse

    :ivar reason: The HTTP response reason
    :vartype reason: str
    :ivar status_code: HttpResponse's status code
    :vartype status_code: int
    :ivar response: The response that triggered the exception.
    :vartype response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
    :ivar model: The request body/response body model
    :vartype model: ~msrest.serialization.Model
    :ivar error: The formatted error
    :vartype error: ODataV4Format
    """

    def __init__(self, message=None, response=None, **kwargs):
        # Don't want to document this one yet.
        error_format = kwargs.get("error_format", ODataV4Format)

        self.reason = None
        self.status_code = None
        self.response = response
        if response:
            self.reason = response.reason
            self.status_code = response.status_code

        # old autorest are setting "error" before calling __init__, so it might be there already
        # transferring into self.model
        model = kwargs.pop("model", None)  # type: Optional[msrest.serialization.Model]
        if model is not None:  # autorest v5
            self.model = model
        else:  # autorest azure-core, for KV 1.0, Storage 12.0, etc.
            self.model = getattr(
                self, "error", None
            )  # type: Optional[msrest.serialization.Model]
        self.error = self._parse_odata_body(error_format, response)  # type: Optional[ODataV4Format]

        # By priority, message is:
        # - odatav4 message, OR
        # - parameter "message", OR
        # - generic meassage using "reason"
        if self.error:
            message = str(self.error)
        else:
            message = message or "Operation returned an invalid status '{}'".format(
                self.reason
            )

        super(HttpResponseError, self).__init__(message=message, **kwargs)

    @staticmethod
    def _parse_odata_body(error_format, response):
        # type: (Type[ODataV4Format], _HttpResponseBase) -> Optional[ODataV4Format]
        try:
            odata_json = json.loads(response.text())
            return error_format(odata_json)
        except Exception:  # pylint: disable=broad-except
            # If the body is not JSON valid, just stop now
            pass
        return None


class DecodeError(HttpResponseError):
    """Error raised during response deserialization."""


class ResourceExistsError(HttpResponseError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ResourceNotFoundError(HttpResponseError):
    """ An error response, typically triggered by a 412 response (for update) or 404 (for get/post)
    """


class ClientAuthenticationError(HttpResponseError):
    """An error response with status code 4xx.
    This will not be raised directly by the Azure core pipeline."""


class ResourceModifiedError(HttpResponseError):
    """An error response with status code 4xx, typically 412 Conflict.
    This will not be raised directly by the Azure core pipeline."""


class ResourceNotModifiedError(HttpResponseError):
    """An error response with status code 304.
    This will not be raised directly by the Azure core pipeline."""


class TooManyRedirectsError(HttpResponseError):
    """Reached the maximum number of redirect attempts."""

    def __init__(self, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum redirect attempts."
        super(TooManyRedirectsError, self).__init__(message, *args, **kwargs)


class ODataV4Error(HttpResponseError):
    """An HTTP response error where the JSON is decoded as OData V4 error format.

    http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091

    :ivar dict odata_json: The parsed JSON body as attribute for convenience.
    :ivar str ~.code: Its value is a service-defined error code.
     This code serves as a sub-status for the HTTP error code specified in the response.
    :ivar str message: Human-readable, language-dependent representation of the error.
    :ivar str target: The target of the particular error (for example, the name of the property in error).
     This field is optional and may be None.
    :ivar list[ODataV4Format] details: Array of ODataV4Format instances that MUST contain name/value pairs
     for code and message, and MAY contain a name/value pair for target, as described above.
    :ivar dict innererror: An object. The contents of this object are service-defined.
     Usually this object contains information that will help debug the service.
    """

    _ERROR_FORMAT = ODataV4Format

    def __init__(self, response, **kwargs):
        # type: (_HttpResponseBase, Any) -> None

        # Ensure field are declared, whatever can happen afterwards
        self.odata_json = None  # type: Optional[Dict[str, Any]]
        try:
            self.odata_json = json.loads(response.text())
            odata_message = self.odata_json.setdefault("error", {}).get("message")
        except Exception:  # pylint: disable=broad-except
            # If the body is not JSON valid, just stop now
            odata_message = None

        self.code = None  # type: Optional[str]
        self.message = kwargs.get("message", odata_message)  # type: Optional[str]
        self.target = None  # type: Optional[str]
        self.details = []  # type: Optional[List[Any]]
        self.innererror = {}  # type: Optional[Dict[str, Any]]

        if self.message and "message" not in kwargs:
            kwargs["message"] = self.message

        super(ODataV4Error, self).__init__(response=response, **kwargs)

        self._error_format = None  # type: Optional[Union[str, ODataV4Format]]
        if self.odata_json:
            try:
                error_node = self.odata_json["error"]
                self._error_format = self._ERROR_FORMAT(error_node)
                self.__dict__.update(
                    {
                        k: v
                        for k, v in self._error_format.__dict__.items()
                        if v is not None
                    }
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.info("Received error message was not valid OdataV4 format.")
                self._error_format = "JSON was invalid for format " + str(
                    self._ERROR_FORMAT
                )

    def __str__(self):
        if self._error_format:
            return str(self._error_format)
        return super(ODataV4Error, self).__str__()
