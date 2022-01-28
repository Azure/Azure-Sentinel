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
This module represents universal policy that works whatever the HTTPSender implementation
"""
import json
import logging
import os
import xml.etree.ElementTree as ET
import platform
import codecs
import re

from typing import Mapping, Any, Optional, AnyStr, Union, IO, cast, TYPE_CHECKING  # pylint: disable=unused-import

from ..version import msrest_version as _msrest_version
from . import SansIOHTTPPolicy
from ..exceptions import DeserializationError, raise_with_traceback
from ..http_logger import log_request, log_response

if TYPE_CHECKING:
    from . import Request, Response  # pylint: disable=unused-import


_LOGGER = logging.getLogger(__name__)

_BOM = codecs.BOM_UTF8.decode(encoding='utf-8')


class HeadersPolicy(SansIOHTTPPolicy):
    """A simple policy that sends the given headers
    with the request.

    This overwrite any headers already defined in the request.
    """
    def __init__(self, headers):
        # type: (Mapping[str, str]) -> None
        self.headers = headers

    def on_request(self, request, **kwargs):
        # type: (Request, Any) -> None
        http_request = request.http_request
        http_request.headers.update(self.headers)

class UserAgentPolicy(SansIOHTTPPolicy):
    _USERAGENT = "User-Agent"
    _ENV_ADDITIONAL_USER_AGENT = 'AZURE_HTTP_USER_AGENT'

    def __init__(self, user_agent=None, overwrite=False):
        # type: (Optional[str], bool) -> None
        self._overwrite = overwrite
        if user_agent is None:
            self._user_agent = "python/{} ({}) msrest/{}".format(
                platform.python_version(),
                platform.platform(),
                _msrest_version
            )
        else:
            self._user_agent = user_agent

        # Whatever you gave me a header explicitly or not,
        # if the env variable is set, add to it.
        add_user_agent_header = os.environ.get(self._ENV_ADDITIONAL_USER_AGENT, None)
        if add_user_agent_header is not None:
            self.add_user_agent(add_user_agent_header)

    @property
    def user_agent(self):
        # type: () -> str
        """The current user agent value."""
        return self._user_agent

    def add_user_agent(self, value):
        # type: (str) -> None
        """Add value to current user agent with a space.

        :param str value: value to add to user agent.
        """
        self._user_agent = "{} {}".format(self._user_agent, value)

    def on_request(self, request, **kwargs):
        # type: (Request, Any) -> None
        http_request = request.http_request
        if self._overwrite or self._USERAGENT not in http_request.headers:
            http_request.headers[self._USERAGENT] = self._user_agent

class HTTPLogger(SansIOHTTPPolicy):
    """A policy that logs HTTP request and response to the DEBUG logger.

    This accepts both global configuration, and kwargs request level with "enable_http_logger"
    """
    def __init__(self, enable_http_logger = False):
        self.enable_http_logger = enable_http_logger

    def on_request(self, request, **kwargs):
        # type: (Request, Any) -> None
        http_request = request.http_request
        if kwargs.get("enable_http_logger", self.enable_http_logger):
            log_request(None, http_request)

    def on_response(self, request, response, **kwargs):
        # type: (Request, Response, Any) -> None
        http_request = request.http_request
        if kwargs.get("enable_http_logger", self.enable_http_logger):
            log_response(None, http_request, response.http_response, result=response)


class RawDeserializer(SansIOHTTPPolicy):

    # Accept "text" because we're open minded people...
    JSON_REGEXP = re.compile(r'^(application|text)/([a-z+.]+\+)?json$')

    # Name used in context
    CONTEXT_NAME = "deserialized_data"

    @classmethod
    def deserialize_from_text(cls, data, content_type=None):
        # type: (Optional[Union[AnyStr, IO]], Optional[str]) -> Any
        """Decode data according to content-type.

        Accept a stream of data as well, but will be load at once in memory for now.

        If no content-type, will return the string version (not bytes, not stream)

        :param data: Input, could be bytes or stream (will be decoded with UTF8) or text
        :type data: str or bytes or IO
        :param str content_type: The content type.
        """
        if hasattr(data, 'read'):
            # Assume a stream
            data = cast(IO, data).read()

        if isinstance(data, bytes):
            data_as_str = data.decode(encoding='utf-8-sig')
        else:
            # Explain to mypy the correct type.
            data_as_str = cast(str, data)

            # Remove Byte Order Mark if present in string
            data_as_str = data_as_str.lstrip(_BOM)

        if content_type is None:
            return data

        if cls.JSON_REGEXP.match(content_type):
            try:
                return json.loads(data_as_str)
            except ValueError as err:
                raise DeserializationError("JSON is invalid: {}".format(err), err)
        elif "xml" in (content_type or []):
            try:

                try:
                    if isinstance(data, unicode):  # type: ignore
                        # If I'm Python 2.7 and unicode XML will scream if I try a "fromstring" on unicode string
                        data_as_str = data_as_str.encode(encoding="utf-8")  # type: ignore
                except NameError:
                    pass

                return ET.fromstring(data_as_str)
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
                raise_with_traceback(DeserializationError, "XML is invalid")
        raise DeserializationError("Cannot deserialize content-type: {}".format(content_type))

    @classmethod
    def deserialize_from_http_generics(cls, body_bytes, headers):
        # type: (Optional[Union[AnyStr, IO]], Mapping) -> Any
        """Deserialize from HTTP response.

        Use bytes and headers to NOT use any requests/aiohttp or whatever
        specific implementation.
        Headers will tested for "content-type"
        """
        # Try to use content-type from headers if available
        content_type = None
        if 'content-type' in headers:
            content_type = headers['content-type'].split(";")[0].strip().lower()
        # Ouch, this server did not declare what it sent...
        # Let's guess it's JSON...
        # Also, since Autorest was considering that an empty body was a valid JSON,
        # need that test as well....
        else:
            content_type = "application/json"

        if body_bytes:
            return cls.deserialize_from_text(body_bytes, content_type)
        return None

    def on_response(self, request, response, **kwargs):
        # type: (Request, Response, Any) -> None
        """Extract data from the body of a REST response object.

        This will load the entire payload in memory.

        Will follow Content-Type to parse.
        We assume everything is UTF8 (BOM acceptable).

        :param raw_data: Data to be processed.
        :param content_type: How to parse if raw_data is a string/bytes.
        :raises JSONDecodeError: If JSON is requested and parsing is impossible.
        :raises UnicodeDecodeError: If bytes is not UTF8
        :raises xml.etree.ElementTree.ParseError: If bytes is not valid XML
        """
        # If response was asked as stream, do NOT read anything and quit now
        if kwargs.get("stream", True):
            return

        http_response = response.http_response

        response.context[self.CONTEXT_NAME] = self.deserialize_from_http_generics(
            http_response.text(),
            http_response.headers
        )
