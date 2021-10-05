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

import logging
import sys

from typing import Callable, Any, Optional, TYPE_CHECKING


_LOGGER = logging.getLogger(__name__)


def raise_with_traceback(exception, message="", *args, **kwargs):
    # type: (Callable, str, Any, Any) -> None
    """Raise exception with a specified traceback.

    This MUST be called inside a "except" clause.

    :param Exception exception: Error type to be raised.
    :param str message: Message to include with error, empty by default.
    :param args: Any additional args to be included with exception.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    # If not called inside a "except", exc_type will be None. Assume it will not happen
    exc_msg = "{}, {}: {}".format(message, exc_type.__name__, exc_value)  # type: ignore
    error = exception(exc_msg, *args, **kwargs)
    try:
        raise error.with_traceback(exc_traceback)
    except AttributeError:
        error.__traceback__ = exc_traceback
        raise error


class ClientException(Exception):
    """Base exception for all Client Runtime exceptions.

    :param str message: Description of exception.
    :param Exception inner_exception: Nested exception (optional).
    """

    def __init__(self, message, inner_exception=None, *args, **kwargs):
        # type: (str, Any, str, str) -> None
        self.inner_exception = inner_exception
        _LOGGER.debug(message)
        super(ClientException, self).__init__(message, *args, **kwargs)  # type: ignore


class SerializationError(ClientException):
    """Error raised during request serialization."""
    pass


class DeserializationError(ClientException):
    """Error raised during response deserialization."""
    pass


class TokenExpiredError(ClientException):
    """OAuth token expired, request failed."""
    pass


class ValidationError(ClientException):
    """Request parameter validation failed.

    :param str rule: Validation rule.
    :param str target: Target value for the rule.
    :param str value: Value that was invalid.
    """

    _messages = {
        "min_length": "must have length greater than {!r}.",
        "max_length": "must have length less than {!r}.",
        "minimum_ex": "must be greater than {!r}.",
        "maximum_ex": "must be less than {!r}.",
        "minimum": "must be equal to or greater than {!r}.",
        "maximum": "must be equal to or less than {!r}.",
        "min_items": "must contain at least {!r} items.",
        "max_items": "must contain at most {!r} items.",
        "pattern": "must conform to the following pattern: {!r}.",
        "unique": "must contain only unique items.",
        "multiple": "must be a multiple of {!r}.",
        "required": "can not be None.",
        "type": "must be of type {!r}"
    }

    @staticmethod
    def _format_message(rule, reason, value):
        if rule == "type" and value.startswith(r"{"):
            internal_type = value.strip(r"{}")
            value = "dict[str, {}]".format(internal_type)
        return reason.format(value)

    def __init__(self, rule, target, value, *args, **kwargs):
        # type: (str, str, str, str, str) -> None
        self.rule = rule
        self.target = target
        message = "Parameter {!r} ".format(target)
        reason = self._messages.get(
            rule, "failed to meet validation requirement.")
        message += self._format_message(rule, reason, value)
        super(ValidationError, self).__init__(message, *args, **kwargs)


class ClientRequestError(ClientException):
    """Client request failed."""
    pass


class AuthenticationError(ClientException):
    """Client request failed to authenticate."""
    pass


# Needed only here for type checking
if TYPE_CHECKING:
    import requests
    from .serialization import Deserializer

class HttpOperationError(ClientException):
    """Client request failed due to server-specified HTTP operation error.
    Attempts to deserialize response into specific error object.

    :param Deserializer deserialize: Deserializer with data on custom
     error objects.
    :param requests.Response response: Server response
    :param str resp_type: Objects type to deserialize response.
    :param args: Additional args to pass to exception object.
    :ivar Model error: Deserialized error model.
    """
    _DEFAULT_MESSAGE = "Unknown error"

    def __str__(self):
        # type: () -> str
        return str(self.message)

    def __init__(self, deserialize, response,
                 resp_type=None, *args, **kwargs):
        # type: (Deserializer, Any, Optional[str], str, str) -> None
        self.error = None
        self.message = self._DEFAULT_MESSAGE
        if hasattr(response, 'internal_response'):
            self.response = response.internal_response
        else:
            self.response = response
        try:
            if resp_type:
                self.error = deserialize(resp_type, response)
                if self.error is None:
                    self.error = deserialize.dependencies[resp_type]()
                # ARM uses OData v4, try that by default
                # http://docs.oasis-open.org/odata/odata-json-format/v4.0/os/odata-json-format-v4.0-os.html#_Toc372793091
                # Code and Message are REQUIRED
                try:
                    self.message = "({}) {}".format(
                        self.error.error.code,
                        self.error.error.message
                    )
                except AttributeError:
                    # Try the default for Autorest if not available (compat)
                    if self.error.message:
                        self.message = self.error.message
        except (DeserializationError, AttributeError, KeyError):
            pass

        if not self.error or self.message == self._DEFAULT_MESSAGE:
            try:
                response.raise_for_status()
            # Two possible raises here:
            # - Attribute error if response is not ClientResponse. Do not catch.
            # - Any internal exception, take it.
            except AttributeError:
                raise
            except Exception as err:  # pylint: disable=broad-except
                if not self.error:
                    self.error = err

                if self.message == self._DEFAULT_MESSAGE:
                    msg = "Operation returned an invalid status code {!r}"
                    self.message = msg.format(response.reason)
            else:
                if not self.error:
                    self.error = response

        # We can't type hint, but at least we can check that
        assert self.message is not None

        super(HttpOperationError, self).__init__(
            self.message, self.error, *args, **kwargs)
