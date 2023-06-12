# pylint: disable=no-self-use
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
"""
This module is the requests implementation of Pipeline ABC
"""
from io import SEEK_SET, UnsupportedOperation
import logging
import time
from enum import Enum
from azure.core.pipeline import PipelineResponse
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    ServiceResponseError,
    ServiceRequestError,
    ServiceRequestTimeoutError,
    ServiceResponseTimeoutError,
)

from ._base import HTTPPolicy, RequestHistory
from . import _utils
from ..._enum_meta import CaseInsensitiveEnumMeta

_LOGGER = logging.getLogger(__name__)


class RetryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    # pylint: disable=enum-must-be-uppercase
    Exponential = "exponential"
    Fixed = "fixed"


class RetryPolicyBase:
    # pylint: disable=too-many-instance-attributes
    #: Maximum backoff time.
    BACKOFF_MAX = 120
    _SAFE_CODES = set(range(506)) - set([408, 429, 500, 502, 503, 504])
    _RETRY_CODES = set(range(999)) - _SAFE_CODES

    def __init__(self, **kwargs):
        self.total_retries = kwargs.pop("retry_total", 10)
        self.connect_retries = kwargs.pop("retry_connect", 3)
        self.read_retries = kwargs.pop("retry_read", 3)
        self.status_retries = kwargs.pop("retry_status", 3)
        self.backoff_factor = kwargs.pop("retry_backoff_factor", 0.8)
        self.backoff_max = kwargs.pop("retry_backoff_max", self.BACKOFF_MAX)
        self.retry_mode = kwargs.pop("retry_mode", RetryMode.Exponential)
        self.timeout = kwargs.pop("timeout", 604800)

        retry_codes = self._RETRY_CODES
        status_codes = kwargs.pop("retry_on_status_codes", [])
        self._retry_on_status_codes = set(status_codes) | retry_codes
        self._method_whitelist = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
        self._respect_retry_after_header = True
        super(RetryPolicyBase, self).__init__()

    @classmethod
    def no_retries(cls):
        """Disable retries."""
        return cls(retry_total=0)

    def configure_retries(self, options):
        """Configures the retry settings.

        :param options: keyword arguments from context.
        :return: A dict containing settings and history for retries.
        :rtype: dict
        """
        return {
            "total": options.pop("retry_total", self.total_retries),
            "connect": options.pop("retry_connect", self.connect_retries),
            "read": options.pop("retry_read", self.read_retries),
            "status": options.pop("retry_status", self.status_retries),
            "backoff": options.pop("retry_backoff_factor", self.backoff_factor),
            "max_backoff": options.pop("retry_backoff_max", self.BACKOFF_MAX),
            "methods": options.pop("retry_on_methods", self._method_whitelist),
            "timeout": options.pop("timeout", self.timeout),
            "history": [],
        }

    def get_backoff_time(self, settings):
        """Returns the current backoff time.

        :param dict settings: The retry settings.
        :return: The current backoff value.
        :rtype: float
        """
        # We want to consider only the last consecutive errors sequence (Ignore redirects).
        consecutive_errors_len = len(settings["history"])
        if consecutive_errors_len <= 1:
            return 0

        if self.retry_mode == RetryMode.Fixed:
            backoff_value = settings["backoff"]
        else:
            backoff_value = settings["backoff"] * (2 ** (consecutive_errors_len - 1))
        return min(settings["max_backoff"], backoff_value)

    def parse_retry_after(self, retry_after):
        """Helper to parse Retry-After and get value in seconds.

        :param str retry_after: Retry-After header
        :rtype: float
        """
        return _utils.parse_retry_after(retry_after)

    def get_retry_after(self, response):
        """Get the value of Retry-After in seconds.

        :param response: The PipelineResponse object
        :type response: ~azure.core.pipeline.PipelineResponse
        :return: Value of Retry-After in seconds.
        :rtype: float or None
        """
        return _utils.get_retry_after(response)

    def _is_connection_error(self, err):
        """Errors when we're fairly sure that the server did not receive the
        request, so it should be safe to retry.
        """
        return isinstance(err, ServiceRequestError)

    def _is_read_error(self, err):
        """Errors that occur after the request has been started, so we should
        assume that the server began processing it.
        """
        return isinstance(err, ServiceResponseError)

    def _is_method_retryable(self, settings, request, response=None):
        """Checks if a given HTTP method should be retried upon, depending if
        it is included on the method allowlist.

        :param dict settings: The retry settings.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :return: True if method should be retried upon. False if not in method allowlist.
        :rtype: bool
        """
        if response and request.method.upper() in ["POST", "PATCH"] and response.status_code in [500, 503, 504]:
            return True
        if request.method.upper() not in settings["methods"]:
            return False

        return True

    def is_retry(self, settings, response):
        """Checks if method/status code is retryable.

        Based on allowlists and control variables such as the number of
        total retries to allow, whether to respect the Retry-After header,
        whether this header is present, and whether the returned status
        code is on the list of status codes to be retried upon on the
        presence of the aforementioned header.

        The behavior is:
        -	If status_code < 400: don't retry
        -	Else if Retry-After present: retry
        -	Else: retry based on the safe status code list ([408, 429, 500, 502, 503, 504])


        :param dict settings: The retry settings.
        :param response: The PipelineResponse object
        :type response: ~azure.core.pipeline.PipelineResponse
        :return: True if method/status code is retryable. False if not retryable.
        :rtype: bool
        """
        if response.http_response.status_code < 400:
            return False
        has_retry_after = bool(response.http_response.headers.get("Retry-After"))
        if has_retry_after and self._respect_retry_after_header:
            return True
        if not self._is_method_retryable(settings, response.http_request, response=response.http_response):
            return False
        return settings["total"] and response.http_response.status_code in self._retry_on_status_codes

    def is_exhausted(self, settings):
        """Checks if any retries left.

        :param dict settings: the retry settings
        :return: False if have more retries. True if retries exhausted.
        :rtype: bool
        """
        retry_counts = (
            settings["total"],
            settings["connect"],
            settings["read"],
            settings["status"],
        )
        retry_counts = list(filter(None, retry_counts))
        if not retry_counts:
            return False

        return min(retry_counts) < 0

    def increment(self, settings, response=None, error=None):
        """Increment the retry counters.

        :param settings: The retry settings.
        :param response: A pipeline response object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :param error: An error encountered during the request, or
         None if the response was received successfully.
        :return: Whether any retry attempt is available
         True if more retry attempts available, False otherwise
        :rtype: bool
        """
        settings["total"] -= 1

        if isinstance(response, PipelineResponse) and response.http_response.status_code == 202:
            return False

        if error and self._is_connection_error(error):
            # Connect retry?
            settings["connect"] -= 1
            settings["history"].append(RequestHistory(response.http_request, error=error))

        elif error and self._is_read_error(error):
            # Read retry?
            settings["read"] -= 1
            if hasattr(response, "http_request"):
                settings["history"].append(RequestHistory(response.http_request, error=error))

        else:
            # Incrementing because of a server error like a 500 in
            # status_forcelist and a the given method is in the allowlist
            if response:
                settings["status"] -= 1
                if hasattr(response, "http_request") and hasattr(response, "http_response"):
                    settings["history"].append(
                        RequestHistory(response.http_request, http_response=response.http_response)
                    )

        if self.is_exhausted(settings):
            return False

        if response.http_request.body and hasattr(response.http_request.body, "read"):
            if "body_position" not in settings:
                return False
            try:
                # attempt to rewind the body to the initial position
                response.http_request.body.seek(settings["body_position"], SEEK_SET)
            except (UnsupportedOperation, ValueError, AttributeError):
                # if body is not seekable, then retry would not work
                return False
        file_positions = settings.get("file_positions")
        if response.http_request.files and file_positions:
            try:
                for value in response.http_request.files.values():
                    file_name, body = value[0], value[1]
                    if file_name in file_positions:
                        position = file_positions[file_name]
                        body.seek(position, SEEK_SET)
            except (UnsupportedOperation, ValueError, AttributeError):
                # if body is not seekable, then retry would not work
                return False
        return True

    def update_context(self, context, retry_settings):
        """Updates retry history in pipeline context.

        :param context: The pipeline context.
        :type context: ~azure.core.pipeline.PipelineContext
        :param retry_settings: The retry settings.
        :type retry_settings: dict
        """
        if retry_settings["history"]:
            context["history"] = retry_settings["history"]

    def _configure_timeout(self, request, absolute_timeout, is_response_error):
        if absolute_timeout <= 0:
            if is_response_error:
                raise ServiceResponseTimeoutError("Response timeout")
            raise ServiceRequestTimeoutError("Request timeout")

        # if connection_timeout is already set, ensure it doesn't exceed absolute_timeout
        connection_timeout = request.context.options.get("connection_timeout")
        if connection_timeout:
            request.context.options["connection_timeout"] = min(connection_timeout, absolute_timeout)

        # otherwise, try to ensure the transport's configured connection_timeout doesn't exceed absolute_timeout
        # ("connection_config" isn't defined on Async/HttpTransport but all implementations in this library have it)
        elif hasattr(request.context.transport, "connection_config"):
            default_timeout = getattr(request.context.transport.connection_config, "timeout", absolute_timeout)
            try:
                if absolute_timeout < default_timeout:
                    request.context.options["connection_timeout"] = absolute_timeout
            except TypeError:
                # transport.connection_config.timeout is something unexpected (not a number)
                pass

    def _configure_positions(self, request, retry_settings):
        body_position = None
        file_positions = None
        if request.http_request.body and hasattr(request.http_request.body, "read"):
            try:
                body_position = request.http_request.body.tell()
            except (AttributeError, UnsupportedOperation):
                # if body position cannot be obtained, then retries will not work
                pass
        else:
            if request.http_request.files:
                file_positions = {}
                try:
                    for value in request.http_request.files.values():
                        name, body = value[0], value[1]
                        if name and body and hasattr(body, "read"):
                            position = body.tell()
                            file_positions[name] = position
                except (AttributeError, UnsupportedOperation):
                    file_positions = None

        retry_settings["body_position"] = body_position
        retry_settings["file_positions"] = file_positions


class RetryPolicy(RetryPolicyBase, HTTPPolicy):
    """A retry policy.

    The retry policy in the pipeline can be configured directly, or tweaked on a per-call basis.

    :keyword int retry_total: Total number of retries to allow. Takes precedence over other counts.
     Default value is 10.

    :keyword int retry_connect: How many connection-related errors to retry on.
     These are errors raised before the request is sent to the remote server,
     which we assume has not triggered the server to process the request. Default value is 3.

    :keyword int retry_read: How many times to retry on read errors.
     These errors are raised after the request was sent to the server, so the
     request may have side-effects. Default value is 3.

    :keyword int retry_status: How many times to retry on bad status codes. Default value is 3.

    :keyword float retry_backoff_factor: A backoff factor to apply between attempts after the second try
     (most errors are resolved immediately by a second try without a delay).
     In fixed mode, retry policy will always sleep for {backoff factor}.
     In 'exponential' mode, retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))`
     seconds. If the backoff_factor is 0.1, then the retry will sleep
     for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is 0.8.

    :keyword int retry_backoff_max: The maximum back off time. Default value is 120 seconds (2 minutes).

    :keyword RetryMode retry_mode: Fixed or exponential delay between attemps, default is exponential.

    :keyword int timeout: Timeout setting for the operation in seconds, default is 604800s (7 days).

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sync.py
            :start-after: [START retry_policy]
            :end-before: [END retry_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a retry policy.
    """

    def _sleep_for_retry(self, response, transport):
        """Sleep based on the Retry-After response header value.

        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :param transport: The HTTP transport type.
        """
        retry_after = self.get_retry_after(response)
        if retry_after:
            transport.sleep(retry_after)
            return True
        return False

    def _sleep_backoff(self, settings, transport):
        """Sleep using exponential backoff. Immediately returns if backoff is 0.

        :param dict settings: The retry settings.
        :param transport: The HTTP transport type.
        """
        backoff = self.get_backoff_time(settings)
        if backoff <= 0:
            return
        transport.sleep(backoff)

    def sleep(self, settings, transport, response=None):
        """Sleep between retry attempts.

        This method will respect a server's ``Retry-After`` response header
        and sleep the duration of the time requested. If that is not present, it
        will use an exponential backoff. By default, the backoff factor is 0 and
        this method will return immediately.

        :param dict settings: The retry settings.
        :param transport: The HTTP transport type.
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        if response:
            slept = self._sleep_for_retry(response, transport)
            if slept:
                return
        self._sleep_backoff(settings, transport)

    def send(self, request):
        """Sends the PipelineRequest object to the next policy. Uses retry settings if necessary.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises: ~azure.core.exceptions.AzureError if maximum retries exceeded.
        :raises: ~azure.core.exceptions.ClientAuthenticationError if authentication
        """
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        self._configure_positions(request, retry_settings)

        absolute_timeout = retry_settings["timeout"]
        is_response_error = True

        while retry_active:
            try:
                start_time = time.time()
                self._configure_timeout(request, absolute_timeout, is_response_error)
                response = self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retry_active = self.increment(retry_settings, response=response)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport, response=response)
                        is_response_error = True
                        continue
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except AzureError as err:
                if absolute_timeout > 0 and self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        if isinstance(err, ServiceRequestError):
                            is_response_error = False
                        else:
                            is_response_error = True
                        continue
                raise err
            finally:
                end_time = time.time()
                if absolute_timeout:
                    absolute_timeout -= end_time - start_time

        self.update_context(response.context, retry_settings)
        return response
