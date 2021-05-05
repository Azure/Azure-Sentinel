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
from __future__ import absolute_import  # we have a "requests" module that conflicts with "requests" on Py2.7
import json
import logging
import os
import platform
import xml.etree.ElementTree as ET
import types
import re
import uuid
from typing import (Mapping, IO, TypeVar, TYPE_CHECKING, Type, cast, List, Callable, Iterator, # pylint: disable=unused-import
                    Any, Union, Dict, Optional, AnyStr)
from six.moves import urllib

from azure.core import __version__  as azcore_version
from azure.core.exceptions import (
    DecodeError,
    raise_with_traceback
)

from azure.core.pipeline import PipelineRequest, PipelineResponse
from ._base import SansIOHTTPPolicy

if TYPE_CHECKING:
    from azure.core.pipeline.transport import HttpResponse, AsyncHttpResponse

_LOGGER = logging.getLogger(__name__)
ContentDecodePolicyType = TypeVar('ContentDecodePolicyType', bound='ContentDecodePolicy')
HTTPRequestType = TypeVar("HTTPRequestType")
HTTPResponseType = TypeVar("HTTPResponseType")


class HeadersPolicy(SansIOHTTPPolicy):
    """A simple policy that sends the given headers with the request.

    This will overwrite any headers already defined in the request. Headers can be
    configured up front, where any custom headers will be applied to all outgoing
    operations, and additional headers can also be added dynamically per operation.

    :param dict base_headers: Headers to send with the request.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sansio.py
            :start-after: [START headers_policy]
            :end-before: [END headers_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a headers policy.
    """
    def __init__(self, base_headers=None, **kwargs):  # pylint: disable=super-init-not-called
        # type: (Dict[str, str], Any) -> None
        self._headers = base_headers or {}
        self._headers.update(kwargs.pop('headers', {}))

    @property
    def headers(self):
        """The current headers collection."""
        return self._headers

    def add_header(self, key, value):
        """Add a header to the configuration to be applied to all requests.

        :param str key: The header.
        :param str value: The header's value.
        """
        self._headers[key] = value

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Updates with the given headers before sending the request to the next policy.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request.http_request.headers.update(self.headers)
        additional_headers = request.context.options.pop('headers', {})
        if additional_headers:
            request.http_request.headers.update(additional_headers)

class _Unset(object):
    pass

class RequestIdPolicy(SansIOHTTPPolicy):
    """A simple policy that sets the given request id in the header.

    This will overwrite request id that is already defined in the request. Request id can be
    configured up front, where the request id will be applied to all outgoing
    operations, and additional request id can also be set dynamically per operation.

    :keyword str request_id: The request id to be added into header.
    :keyword bool auto_request_id: Auto generates a unique request ID per call if true which is by default.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sansio.py
            :start-after: [START request_id_policy]
            :end-before: [END request_id_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a request id policy.
    """
    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        # type: (dict) -> None
        self._request_id = kwargs.pop('request_id', _Unset)
        self._auto_request_id = kwargs.pop('auto_request_id', True)

    def set_request_id(self, value):
        """Add the request id to the configuration to be applied to all requests.

        :param str value: The request id value.
        """
        self._request_id = value

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Updates with the given request id before sending the request to the next policy.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request_id = unset = object()
        if 'request_id' in request.context.options:
            request_id = request.context.options.pop('request_id')
            if request_id is None:
                return
        elif self._request_id is None:
            return
        elif self._request_id is not _Unset:
            request_id = self._request_id
        elif self._auto_request_id:
            request_id = str(uuid.uuid1())
        if request_id is not unset:
            header = {"x-ms-client-request-id": request_id}
            request.http_request.headers.update(header)

class UserAgentPolicy(SansIOHTTPPolicy):
    """User-Agent Policy. Allows custom values to be added to the User-Agent header.

    :param str base_user_agent: Sets the base user agent value.

    :keyword bool user_agent_overwrite: Overwrites User-Agent when True. Defaults to False.
    :keyword bool user_agent_use_env: Gets user-agent from environment. Defaults to True.
    :keyword str user_agent: If specified, this will be added in front of the user agent string.
    :keyword str sdk_moniker: If specified, the user agent string will be
        azsdk-python-[sdk_moniker] Python/[python_version] ([platform_version])

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sansio.py
            :start-after: [START user_agent_policy]
            :end-before: [END user_agent_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a user agent policy.
    """
    _USERAGENT = "User-Agent"
    _ENV_ADDITIONAL_USER_AGENT = 'AZURE_HTTP_USER_AGENT'

    def __init__(self, base_user_agent=None, **kwargs):  # pylint: disable=super-init-not-called
        # type: (Optional[str], **Any) -> None
        self.overwrite = kwargs.pop('user_agent_overwrite', False)
        self.use_env = kwargs.pop('user_agent_use_env', True)
        application_id = kwargs.pop('user_agent', None)
        sdk_moniker = kwargs.pop('sdk_moniker', 'core/{}'.format(azcore_version))

        if base_user_agent:
            self._user_agent = base_user_agent
        else:
            self._user_agent = "azsdk-python-{} Python/{} ({})".format(
                sdk_moniker,
                platform.python_version(),
                platform.platform()
            )

        if application_id:
            self._user_agent = "{} {}".format(application_id, self._user_agent)

    @property
    def user_agent(self):
        # type: () -> str
        """The current user agent value."""
        if self.use_env:
            add_user_agent_header = os.environ.get(self._ENV_ADDITIONAL_USER_AGENT, None)
            if add_user_agent_header is not None:
                return "{} {}".format(self._user_agent, add_user_agent_header)
        return self._user_agent

    def add_user_agent(self, value):
        # type: (str) -> None
        """Add value to current user agent with a space.
        :param str value: value to add to user agent.
        """
        self._user_agent = "{} {}".format(self._user_agent, value)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Modifies the User-Agent header before the request is sent.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        http_request = request.http_request
        options_dict = request.context.options
        if 'user_agent' in options_dict:
            user_agent = options_dict.pop('user_agent')
            if options_dict.pop('user_agent_overwrite', self.overwrite):
                http_request.headers[self._USERAGENT] = user_agent
            else:
                user_agent = "{} {}".format(user_agent, self.user_agent)
                http_request.headers[self._USERAGENT] = user_agent

        elif self.overwrite or self._USERAGENT not in http_request.headers:
            http_request.headers[self._USERAGENT] = self.user_agent


class NetworkTraceLoggingPolicy(SansIOHTTPPolicy):
    """The logging policy in the pipeline is used to output HTTP network trace to the configured logger.

    This accepts both global configuration, and per-request level with "enable_http_logger"

    :param bool logging_enable: Use to enable per operation. Defaults to False.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sansio.py
            :start-after: [START network_trace_logging_policy]
            :end-before: [END network_trace_logging_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a network trace logging policy.
    """
    def __init__(self, logging_enable=False, **kwargs): # pylint: disable=unused-argument
        self.enable_http_logger = logging_enable

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Logs HTTP request to the DEBUG logger.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        http_request = request.http_request
        options = request.context.options
        logging_enable = options.pop("logging_enable", self.enable_http_logger)
        request.context["logging_enable"] = logging_enable
        if logging_enable:
            if not _LOGGER.isEnabledFor(logging.DEBUG):
                return

            try:
                _LOGGER.debug("Request URL: %r", http_request.url)
                _LOGGER.debug("Request method: %r", http_request.method)
                _LOGGER.debug("Request headers:")
                for header, value in http_request.headers.items():
                    _LOGGER.debug("    %r: %r", header, value)
                _LOGGER.debug("Request body:")

                # We don't want to log the binary data of a file upload.
                if isinstance(http_request.body, types.GeneratorType):
                    _LOGGER.debug("File upload")
                    return
                try:
                    if isinstance(http_request.body, types.AsyncGeneratorType):
                        _LOGGER.debug("File upload")
                        return
                except AttributeError:
                    pass
                if http_request.body:
                    _LOGGER.debug(str(http_request.body))
                    return
                _LOGGER.debug("This request has no body")
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.debug("Failed to log request: %r", err)

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        """Logs HTTP response to the DEBUG logger.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        http_response = response.http_response
        try:
            logging_enable = response.context["logging_enable"]
            if logging_enable:
                if not _LOGGER.isEnabledFor(logging.DEBUG):
                    return

                _LOGGER.debug("Response status: %r", http_response.status_code)
                _LOGGER.debug("Response headers:")
                for res_header, value in http_response.headers.items():
                    _LOGGER.debug("    %r: %r", res_header, value)

                # We don't want to log binary data if the response is a file.
                _LOGGER.debug("Response content:")
                pattern = re.compile(r'attachment; ?filename=["\w.]+', re.IGNORECASE)
                header = http_response.headers.get('content-disposition')

                if header and pattern.match(header):
                    filename = header.partition('=')[2]
                    _LOGGER.debug("File attachments: %s", filename)
                elif http_response.headers.get("content-type", "").endswith("octet-stream"):
                    _LOGGER.debug("Body contains binary data.")
                elif http_response.headers.get("content-type", "").startswith("image"):
                    _LOGGER.debug("Body contains image data.")
                else:
                    if response.context.options.get('stream', False):
                        _LOGGER.debug("Body is streamable")
                    else:
                        _LOGGER.debug(response.http_response.text())
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to log response: %s", repr(err))


class HttpLoggingPolicy(SansIOHTTPPolicy):
    """The Pipeline policy that handles logging of HTTP requests and responses.
    """

    DEFAULT_HEADERS_WHITELIST = set([
        "x-ms-request-id",
        "x-ms-client-request-id",
        "x-ms-return-client-request-id",
        "traceparent",
        "Accept",
        "Cache-Control",
        "Connection",
        "Content-Length",
        "Content-Type",
        "Date",
        "ETag",
        "Expires",
        "If-Match",
        "If-Modified-Since",
        "If-None-Match",
        "If-Unmodified-Since",
        "Last-Modified",
        "Pragma",
        "Request-Id",
        "Retry-After",
        "Server",
        "Transfer-Encoding",
        "User-Agent",
    ])
    REDACTED_PLACEHOLDER = "REDACTED"

    def __init__(self, logger=None, **kwargs):  # pylint: disable=unused-argument
        self.logger = logger or logging.getLogger(
            "azure.core.pipeline.policies.http_logging_policy"
        )
        self.allowed_query_params = set()
        self.allowed_header_names = set(self.__class__.DEFAULT_HEADERS_WHITELIST)

    def _redact_query_param(self, key, value):
        lower_case_allowed_query_params = [
            param.lower() for param in self.allowed_query_params
        ]
        return value if key.lower() in lower_case_allowed_query_params else HttpLoggingPolicy.REDACTED_PLACEHOLDER

    def _redact_header(self, key, value):
        lower_case_allowed_header_names = [
            header.lower() for header in self.allowed_header_names
        ]
        return value if key.lower() in lower_case_allowed_header_names else HttpLoggingPolicy.REDACTED_PLACEHOLDER

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Logs HTTP method, url and headers.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        http_request = request.http_request
        options = request.context.options
        # Get logger in my context first (request has been retried)
        # then read from kwargs (pop if that's the case)
        # then use my instance logger
        logger = request.context.setdefault("logger", options.pop("logger", self.logger))

        if not logger.isEnabledFor(logging.INFO):
            return

        try:
            parsed_url = list(urllib.parse.urlparse(http_request.url))
            parsed_qp = urllib.parse.parse_qsl(parsed_url[4], keep_blank_values=True)
            filtered_qp = [(key, self._redact_query_param(key, value)) for key, value in parsed_qp]
            # 4 is query
            parsed_url[4] = "&".join(["=".join(part) for part in filtered_qp])
            redacted_url = urllib.parse.urlunparse(parsed_url)

            logger.info("Request URL: %r", redacted_url)
            logger.info("Request method: %r", http_request.method)
            logger.info("Request headers:")
            for header, value in http_request.headers.items():
                value = self._redact_header(header, value)
                logger.info("    %r: %r", header, value)
            if isinstance(http_request.body, types.GeneratorType):
                logger.info("File upload")
                return
            try:
                if isinstance(http_request.body, types.AsyncGeneratorType):
                    logger.info("File upload")
                    return
            except AttributeError:
                pass
            if http_request.body:
                logger.info("A body is sent with the request")
                return
            logger.info("No body was attached to the request")
            return
        except Exception as err:  # pylint: disable=broad-except
            logger.warning("Failed to log request: %s", repr(err))

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        http_response = response.http_response

        try:
            logger = response.context["logger"]

            if not logger.isEnabledFor(logging.INFO):
                return

            logger.info("Response status: %r", http_response.status_code)
            logger.info("Response headers:")
            for res_header, value in http_response.headers.items():
                value = self._redact_header(res_header, value)
                logger.info("    %r: %r", res_header, value)
        except Exception as err:  # pylint: disable=broad-except
            logger.warning("Failed to log response: %s", repr(err))


class ContentDecodePolicy(SansIOHTTPPolicy):
    """Policy for decoding unstreamed response content.

    :param response_encoding: The encoding to use if known for this service (will disable auto-detection)
    :type response_encoding: str
    """
    # Accept "text" because we're open minded people...
    JSON_REGEXP = re.compile(r'^(application|text)/([0-9a-z+.]+\+)?json$')

    # Name used in context
    CONTEXT_NAME = "deserialized_data"

    def __init__(self, response_encoding=None, **kwargs):  # pylint: disable=unused-argument
        # type: (Optional[str], Any) -> None
        self._response_encoding = response_encoding

    @classmethod
    def deserialize_from_text(
        cls,  # type: Type[ContentDecodePolicyType]
        data,  # type: Optional[Union[AnyStr, IO]]
        mime_type=None,  # Optional[str]
        response=None  # Optional[Union[HttpResponse, AsyncHttpResponse]]
    ):
        """Decode response data according to content-type.

        Accept a stream of data as well, but will be load at once in memory for now.
        If no content-type, will return the string version (not bytes, not stream)

        :param response: The HTTP response.
        :type response: ~azure.core.pipeline.transport.HttpResponse
        :param str mime_type: The mime type. As mime type, charset is not expected.
        :param response: If passed, exception will be annotated with that response
        :raises ~azure.core.exceptions.DecodeError: If deserialization fails
        :returns: A dict or XML tree, depending of the mime_type
        """
        if not data:
            return None

        if hasattr(data, 'read'):
            # Assume a stream
            data = cast(IO, data).read()

        if isinstance(data, bytes):
            data_as_str = data.decode(encoding='utf-8-sig')
        else:
            # Explain to mypy the correct type.
            data_as_str = cast(str, data)

        if mime_type is None:
            return data_as_str

        if cls.JSON_REGEXP.match(mime_type):
            try:
                return json.loads(data_as_str)
            except ValueError as err:
                raise DecodeError(message="JSON is invalid: {}".format(err), response=response, error=err)
        elif "xml" in (mime_type or []):
            try:
                try:
                    if isinstance(data, unicode):  # type: ignore
                        # If I'm Python 2.7 and unicode XML will scream if I try a "fromstring" on unicode string
                        data_as_str = cast(str, data_as_str.encode(encoding="utf-8"))
                except NameError:
                    pass
                return ET.fromstring(data_as_str)   # nosec
            except ET.ParseError:
                # It might be because the server has an issue, and returned JSON with
                # content-type XML....
                # So let's try a JSON load, and if it's still broken
                # let's flow the initial exception
                def _json_attemp(data):
                    try:
                        return True, json.loads(data)
                    except ValueError:
                        return False, None # Don't care about this one
                success, json_result = _json_attemp(data)
                if success:
                    return json_result
                # If i'm here, it's not JSON, it's not XML, let's scream
                # and raise the last context in this block (the XML exception)
                # The function hack is because Py2.7 messes up with exception
                # context otherwise.
                _LOGGER.critical("Wasn't XML not JSON, failing")
                raise_with_traceback(DecodeError, message="XML is invalid", response=response)
        elif mime_type.startswith("text/"):
            return data_as_str
        raise DecodeError("Cannot deserialize content-type: {}".format(mime_type))

    @classmethod
    def deserialize_from_http_generics(
        cls,  # type: Type[ContentDecodePolicyType]
        response,  # Union[HttpResponse, AsyncHttpResponse]
        encoding=None,  # Optional[str]
    ):
        """Deserialize from HTTP response.

        Headers will tested for "content-type"

        :param response: The HTTP response
        :param encoding: The encoding to use if known for this service (will disable auto-detection)
        :raises ~azure.core.exceptions.DecodeError: If deserialization fails
        :returns: A dict or XML tree, depending of the mime-type
        """
        # Try to use content-type from headers if available
        if response.content_type:
            mime_type = response.content_type.split(";")[0].strip().lower()
        # Ouch, this server did not declare what it sent...
        # Let's guess it's JSON...
        # Also, since Autorest was considering that an empty body was a valid JSON,
        # need that test as well....
        else:
            mime_type = "application/json"

        # Rely on transport implementation to give me "text()" decoded correctly
        return cls.deserialize_from_text(response.text(encoding), mime_type, response=response)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        options = request.context.options
        response_encoding = options.pop("response_encoding", self._response_encoding)
        if response_encoding:
            request.context["response_encoding"] = response_encoding

    def on_response(self,
        request, # type: PipelineRequest[HTTPRequestType]
        response  # type: PipelineResponse[HTTPRequestType, Union[HttpResponse, AsyncHttpResponse]]
    ):
        # type: (...) -> None
        """Extract data from the body of a REST response object.
        This will load the entire payload in memory.
        Will follow Content-Type to parse.
        We assume everything is UTF8 (BOM acceptable).

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        :param raw_data: Data to be processed.
        :param content_type: How to parse if raw_data is a string/bytes.
        :raises JSONDecodeError: If JSON is requested and parsing is impossible.
        :raises UnicodeDecodeError: If bytes is not UTF8
        :raises xml.etree.ElementTree.ParseError: If bytes is not valid XML
        :raises ~azure.core.exceptions.DecodeError: If deserialization fails
        """
        # If response was asked as stream, do NOT read anything and quit now
        if response.context.options.get("stream", True):
            return

        response_encoding = request.context.get('response_encoding')

        response.context[self.CONTEXT_NAME] = self.deserialize_from_http_generics(
            response.http_response,
            response_encoding
        )


class ProxyPolicy(SansIOHTTPPolicy):
    """A proxy policy.

    Dictionary mapping protocol or protocol and host to the URL of the proxy
    to be used on each Request.

    :param dict proxies: Maps protocol or protocol and hostname to the URL
     of the proxy.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sansio.py
            :start-after: [START proxy_policy]
            :end-before: [END proxy_policy]
            :language: python
            :dedent: 4
            :caption: Configuring a proxy policy.
    """
    def __init__(self, proxies=None, **kwargs):  #pylint: disable=unused-argument,super-init-not-called
        self.proxies = proxies

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        ctxt = request.context.options
        if self.proxies and "proxies" not in ctxt:
            ctxt["proxies"] = self.proxies
