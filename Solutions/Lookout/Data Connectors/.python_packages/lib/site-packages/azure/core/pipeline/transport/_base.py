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
from __future__ import absolute_import
import abc
from email.message import Message

try:
    from email import message_from_bytes as message_parser
except ImportError:  # 2.7
    from email import message_from_string as message_parser  # type: ignore
from io import BytesIO
import json
import logging
import os
import time
import copy

try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
    cast,
    IO,
    List,
    Union,
    Any,
    Mapping,
    Dict,
    Optional,
    Tuple,
    Iterator,
    Type
)

from six.moves.http_client import HTTPConnection, HTTPResponse as _HTTPResponse

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import (
    ABC,
    AbstractContextManager,
    PipelineRequest,
    PipelineResponse,
    PipelineContext,
)
from .._tools import await_result as _await_result
from ..._utils import _case_insensitive_dict


if TYPE_CHECKING:
    from ..policies import SansIOHTTPPolicy
    from collections.abc import MutableMapping

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")
PipelineType = TypeVar("PipelineType")

_LOGGER = logging.getLogger(__name__)


def _format_url_section(template, **kwargs):
    """String format the template with the kwargs, auto-skip sections of the template that are NOT in the kwargs.

    By default in Python, "format" will raise a KeyError if a template element is not found. Here the section between
    the slashes will be removed from the template instead.

    This is used for API like Storage, where when Swagger has template section not defined as parameter.

    :param str template: a string template to fill
    :param dict[str,str] kwargs: Template values as string
    :rtype: str
    :returns: Template completed
    """
    components = template.split("/")
    while components:
        try:
            return template.format(**kwargs)
        except KeyError as key:
            formatted_components = template.split("/")
            components = [
                c for c in formatted_components if "{{{}}}".format(key.args[0]) not in c
            ]
            template = "/".join(components)
    # No URL sections left - returning None


def _urljoin(base_url, stub_url):
    # type: (str, str) -> str
    """Append to end of base URL without losing query parameters.

    :param str base_url: The base URL.
    :param str stub_url: Section to append to the end of the URL path.
    :returns: The updated URL.
    :rtype: str
    """
    parsed = urlparse(base_url)
    parsed = parsed._replace(path=parsed.path.rstrip("/") + "/" + stub_url)
    return parsed.geturl()


class _HTTPSerializer(HTTPConnection, object):
    """Hacking the stdlib HTTPConnection to serialize HTTP request as strings.
    """

    def __init__(self, *args, **kwargs):
        self.buffer = b""
        kwargs.setdefault("host", "fakehost")
        super(_HTTPSerializer, self).__init__(*args, **kwargs)

    def putheader(self, header, *values):
        if header in ["Host", "Accept-Encoding"]:
            return
        super(_HTTPSerializer, self).putheader(header, *values)

    def send(self, data):
        self.buffer += data


def _serialize_request(http_request):
    serializer = _HTTPSerializer()
    serializer.request(
        method=http_request.method,
        url=http_request.url,
        body=http_request.body,
        headers=http_request.headers,
    )
    return serializer.buffer


class HttpTransport(
    AbstractContextManager, ABC, Generic[HTTPRequestType, HTTPResponseType]
):  # type: ignore
    """An http sender ABC.
    """

    @abc.abstractmethod
    def send(self, request, **kwargs):
        # type: (HTTPRequestType, Any) -> HTTPResponseType
        """Send the request using this HTTP sender.

        :param request: The pipeline request object
        :type request: ~azure.core.transport.HTTPRequest
        :return: The pipeline response object.
        :rtype: ~azure.core.pipeline.transport.HttpResponse
        """

    @abc.abstractmethod
    def open(self):
        """Assign new session if one does not already exist."""

    @abc.abstractmethod
    def close(self):
        """Close the session if it is not externally owned."""

    def sleep(self, duration):  # pylint: disable=no-self-use
        time.sleep(duration)


class HttpRequest(object):
    """Represents a HTTP request.

    URL can be given without query parameters, to be added later using "format_parameters".

    :param str method: HTTP method (GET, HEAD, etc.)
    :param str url: At least complete scheme/host/path
    :param dict[str,str] headers: HTTP headers
    :param files: Files list.
    :param data: Body to be sent.
    :type data: bytes or str.
    """

    def __init__(self, method, url, headers=None, files=None, data=None):
        # type: (str, str, Mapping[str, str], Any, Any) -> None
        self.method = method
        self.url = url
        self.headers = _case_insensitive_dict(headers)
        self.files = files
        self.data = data
        self.multipart_mixed_info = None  # type: Optional[Tuple]

    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    def __deepcopy__(self, memo=None):
        try:
            data = copy.deepcopy(self.body, memo)
            files = copy.deepcopy(self.files, memo)
            return HttpRequest(self.method, self.url, self.headers, files, data)
        except (ValueError, TypeError):
            return copy.copy(self)

    @property
    def query(self):
        """The query parameters of the request as a dict.

        :rtype: dict[str, str]
        """
        query = urlparse(self.url).query
        if query:
            return {p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]}
        return {}

    @property
    def body(self):
        """Alias to data.

        :rtype: bytes
        """
        return self.data

    @body.setter
    def body(self, value):
        self.data = value

    @staticmethod
    def _format_data(data):
        # type: (Union[str, IO]) -> Union[Tuple[None, str], Tuple[Optional[str], IO, str]]
        """Format field data according to whether it is a stream or
        a string for a form-data request.

        :param data: The request field data.
        :type data: str or file-like object.
        """
        if hasattr(data, "read"):
            data = cast(IO, data)
            data_name = None
            try:
                if data.name[0] != "<" and data.name[-1] != ">":
                    data_name = os.path.basename(data.name)
            except (AttributeError, TypeError):
                pass
            return (data_name, data, "application/octet-stream")
        return (None, cast(str, data))

    def format_parameters(self, params):
        # type: (Dict[str, str]) -> None
        """Format parameters into a valid query string.
        It's assumed all parameters have already been quoted as
        valid URL strings.

        :param dict params: A dictionary of parameters.
        """
        query = urlparse(self.url).query
        if query:
            self.url = self.url.partition("?")[0]
            existing_params = {
                p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]
            }
            params.update(existing_params)
        query_params = []
        for k, v in params.items():
            if isinstance(v, list):
                for w in v:
                    if w is None:
                        raise ValueError("Query parameter {} cannot be None".format(k))
                    query_params.append("{}={}".format(k, w))
            else:
                if v is None:
                    raise ValueError("Query parameter {} cannot be None".format(k))
                query_params.append("{}={}".format(k, v))
        query = "?" + "&".join(query_params)
        self.url = self.url + query

    def set_streamed_data_body(self, data):
        """Set a streamable data body.

        :param data: The request field data.
        :type data: stream or generator or asyncgenerator
        """
        if not isinstance(data, binary_type) and not any(
            hasattr(data, attr) for attr in ["read", "__iter__", "__aiter__"]
        ):
            raise TypeError(
                "A streamable data source must be an open file-like object or iterable."
            )
        self.data = data
        self.files = None

    def set_text_body(self, data):
        """Set a text as body of the request.

        :param data: A text to send as body.
        :type data: str
        """
        if data is None:
            self.data = None
        else:
            self.data = data
            self.headers["Content-Length"] = str(len(self.data))
        self.files = None

    def set_xml_body(self, data):
        """Set an XML element tree as the body of the request.

        :param data: The request field data.
        :type data: XML node
        """
        if data is None:
            self.data = None
        else:
            bytes_data = ET.tostring(data, encoding="utf8")
            self.data = bytes_data.replace(b"encoding='utf8'", b"encoding='utf-8'")
            self.headers["Content-Length"] = str(len(self.data))
        self.files = None

    def set_json_body(self, data):
        """Set a JSON-friendly object as the body of the request.

        :param data: A JSON serializable object
        """
        if data is None:
            self.data = None
        else:
            self.data = json.dumps(data)
            self.headers["Content-Length"] = str(len(self.data))
        self.files = None

    def set_formdata_body(self, data=None):
        """Set form-encoded data as the body of the request.

        :param data: The request field data.
        :type data: dict
        """
        if data is None:
            data = {}
        content_type = self.headers.pop("Content-Type", None) if self.headers else None

        if content_type and content_type.lower() == "application/x-www-form-urlencoded":
            self.data = {f: d for f, d in data.items() if d is not None}
            self.files = None
        else:  # Assume "multipart/form-data"
            self.files = {
                f: self._format_data(d) for f, d in data.items() if d is not None
            }
            self.data = None

    def set_bytes_body(self, data):
        """Set generic bytes as the body of the request.

        Will set content-length.

        :param data: The request field data.
        :type data: bytes
        """
        if data:
            self.headers["Content-Length"] = str(len(data))
        self.data = data
        self.files = None

    def set_multipart_mixed(self, *requests, **kwargs):
        # type: (HttpRequest, Any) -> None
        """Set the part of a multipart/mixed.

        Only supported args for now are HttpRequest objects.

        boundary is optional, and one will be generated if you don't provide one.
        Note that no verification are made on the boundary, this is considered advanced
        enough so you know how to respect RFC1341 7.2.1 and provide a correct boundary.

        Any additional kwargs will be passed into the pipeline context for per-request policy
        configuration.

        :keyword list[SansIOHTTPPolicy] policies: SansIOPolicy to apply at preparation time
        :keyword str boundary: Optional boundary
        :param requests: HttpRequests object
        """
        self.multipart_mixed_info = (
            requests,
            kwargs.pop("policies", []),
            kwargs.pop("boundary", None),
            kwargs
        )

    def prepare_multipart_body(self, content_index=0):
        # type: (int) -> int
        """Will prepare the body of this request according to the multipart information.

        This call assumes the on_request policies have been applied already in their
        correct context (sync/async)

        Does nothing if "set_multipart_mixed" was never called.

        :param int content_index: The current index of parts within the batch message.
        :returns: The updated index after all parts in this request have been added.
        :rtype: int
        """
        if not self.multipart_mixed_info:
            return 0

        requests = self.multipart_mixed_info[0]  # type: List[HttpRequest]
        boundary = self.multipart_mixed_info[2]  # type: Optional[str]

        # Update the main request with the body
        main_message = Message()
        main_message.add_header("Content-Type", "multipart/mixed")
        if boundary:
            main_message.set_boundary(boundary)

        for req in requests:
            part_message = Message()
            if req.multipart_mixed_info:
                content_index = req.prepare_multipart_body(content_index=content_index)
                part_message.add_header("Content-Type", req.headers['Content-Type'])
                payload = req.serialize()
                # We need to remove the ~HTTP/1.1 prefix along with the added content-length
                payload = payload[payload.index(b'--'):]
            else:
                part_message.add_header("Content-Type", "application/http")
                part_message.add_header("Content-Transfer-Encoding", "binary")
                part_message.add_header("Content-ID", str(content_index))
                payload = req.serialize()
                content_index += 1
            part_message.set_payload(payload)
            main_message.attach(part_message)

        try:
            from email.policy import HTTP

            full_message = main_message.as_bytes(policy=HTTP)
            eol = b"\r\n"
        except ImportError:  # Python 2.7
            # Right now we decide to not support Python 2.7 on serialization, since
            # it doesn't serialize a valid HTTP request (and our main scenario Storage refuses it)
            raise NotImplementedError(
                "Multipart request are not supported on Python 2.7"
            )
            # full_message = main_message.as_string()
            # eol = b'\n'
        _, _, body = full_message.split(eol, 2)
        self.set_bytes_body(body)
        self.headers["Content-Type"] = (
            "multipart/mixed; boundary=" + main_message.get_boundary()
        )
        return content_index

    def serialize(self):
        # type: () -> bytes
        """Serialize this request using application/http spec.

        :rtype: bytes
        """
        return _serialize_request(self)


class _HttpResponseBase(object):
    """Represent a HTTP response.

    No body is defined here on purpose, since async pipeline
    will provide async ways to access the body
    Full in-memory using "body" as bytes.

    :param request: The request.
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param internal_response: The object returned from the HTTP library.
    :param int block_size: Defaults to 4096 bytes.
    """

    def __init__(self, request, internal_response, block_size=None):
        # type: (HttpRequest, Any, Optional[int]) -> None
        self.request = request
        self.internal_response = internal_response
        self.status_code = None  # type: Optional[int]
        self.headers = {}  # type: MutableMapping[str, str]
        self.reason = None  # type: Optional[str]
        self.content_type = None  # type: Optional[str]
        self.block_size = block_size or 4096  # Default to same as Requests

    def body(self):
        # type: () -> bytes
        """Return the whole body as bytes in memory.
        """
        raise NotImplementedError()

    def text(self, encoding=None):
        # type: (str) -> str
        """Return the whole body as a string.

        :param str encoding: The encoding to apply. If None, use "utf-8" with BOM parsing (utf-8-sig).
         Implementation can be smarter if they want (using headers or chardet).
        """
        if encoding == "utf-8" or encoding is None:
            encoding = "utf-8-sig"
        return self.body().decode(encoding)

    def _decode_parts(self, message, http_response_type, requests):
        # type: (Message, Type[_HttpResponseBase], List[HttpRequest]) -> List[HttpResponse]
        """Rebuild an HTTP response from pure string."""
        responses = []
        for index, raw_reponse in enumerate(message.get_payload()):
            content_type = raw_reponse.get_content_type()
            if content_type == "application/http":
                responses.append(
                    _deserialize_response(
                        raw_reponse.get_payload(decode=True),
                        requests[index],
                        http_response_type=http_response_type,
                    )
                )
            elif content_type == "multipart/mixed" and requests[index].multipart_mixed_info:
                # The message batch contains one or more change sets
                changeset_requests = requests[index].multipart_mixed_info[0]  # type: ignore
                changeset_responses = self._decode_parts(raw_reponse, http_response_type, changeset_requests)
                responses.extend(changeset_responses)
            else:
                raise ValueError(
                    "Multipart doesn't support part other than application/http for now"
                )
        return responses

    def _get_raw_parts(self, http_response_type=None):
        # type (Optional[Type[_HttpResponseBase]]) -> Iterator[HttpResponse]
        """Assuming this body is multipart, return the iterator or parts.

        If parts are application/http use http_response_type or HttpClientTransportResponse
        as enveloppe.
        """
        if http_response_type is None:
            http_response_type = HttpClientTransportResponse

        body_as_bytes = self.body()
        # In order to use email.message parser, I need full HTTP bytes. Faking something to make the parser happy
        http_body = (
            b"Content-Type: "
            + self.content_type.encode("ascii")
            + b"\r\n\r\n"
            + body_as_bytes
        )
        message = message_parser(http_body)  # type: Message
        requests = self.request.multipart_mixed_info[0]  # type: List[HttpRequest]
        return self._decode_parts(message, http_response_type, requests)

    def raise_for_status(self):
        # type () -> None
        """Raises an HttpResponseError if the response has an error status code.
        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    def __repr__(self):
        # there doesn't have to be a content type
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )


class HttpResponse(_HttpResponseBase):  # pylint: disable=abstract-method
    def stream_download(self, pipeline):
        # type: (PipelineType) -> Iterator[bytes]
        """Generator for streaming request body data.

        Should be implemented by sub-classes if streaming download
        is supported.

        :rtype: iterator[bytes]
        """

    def parts(self):
        # type: () -> Iterator[HttpResponse]
        """Assuming the content-type is multipart/mixed, will return the parts as an iterator.

        :rtype: iterator[HttpResponse]
        :raises ValueError: If the content is not multipart/mixed
        """
        if not self.content_type or not self.content_type.startswith("multipart/mixed"):
            raise ValueError(
                "You can't get parts if the response is not multipart/mixed"
            )

        responses = self._get_raw_parts()
        if self.request.multipart_mixed_info:
            policies = self.request.multipart_mixed_info[1]  # type: List[SansIOHTTPPolicy]

            # Apply on_response concurrently to all requests
            import concurrent.futures

            def parse_responses(response):
                http_request = response.request
                context = PipelineContext(None)
                pipeline_request = PipelineRequest(http_request, context)
                pipeline_response = PipelineResponse(
                    http_request, response, context=context
                )

                for policy in policies:
                    _await_result(policy.on_response, pipeline_request, pipeline_response)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # List comprehension to raise exceptions if happened
                [  # pylint: disable=expression-not-assigned, unnecessary-comprehension
                    _ for _ in executor.map(parse_responses, responses)
                ]

        return responses


class _HttpClientTransportResponse(_HttpResponseBase):
    """Create a HTTPResponse from an http.client response.

    Body will NOT be read by the constructor. Call "body()" to load the body in memory if necessary.

    :param HttpRequest request: The request.
    :param httpclient_response: The object returned from an HTTP(S)Connection from http.client
    """

    def __init__(self, request, httpclient_response):
        super(_HttpClientTransportResponse, self).__init__(request, httpclient_response)
        self.status_code = httpclient_response.status
        self.headers = _case_insensitive_dict(httpclient_response.getheaders())
        self.reason = httpclient_response.reason
        self.content_type = self.headers.get("Content-Type")
        self.data = None

    def body(self):
        if self.data is None:
            self.data = self.internal_response.read()
        return self.data


class HttpClientTransportResponse(_HttpClientTransportResponse, HttpResponse):
    """Create a HTTPResponse from an http.client response.

    Body will NOT be read by the constructor. Call "body()" to load the body in memory if necessary.
    """


class BytesIOSocket(object):
    """Mocking the "makefile" of socket for HTTPResponse.

    This can be used to create a http.client.HTTPResponse object
    based on bytes and not a real socket.
    """

    def __init__(self, bytes_data):
        self.bytes_data = bytes_data

    def makefile(self, *_):
        return BytesIO(self.bytes_data)


def _deserialize_response(
    http_response_as_bytes, http_request, http_response_type=HttpClientTransportResponse
):
    local_socket = BytesIOSocket(http_response_as_bytes)
    response = _HTTPResponse(local_socket, method=http_request.method)
    response.begin()
    return http_response_type(http_request, response)


class PipelineClientBase(object):
    """Base class for pipeline clients.

    :param str base_url: URL for the request.
    """

    def __init__(self, base_url):
        self._base_url = base_url

    def _request(
        self,
        method,  # type: str
        url,  # type: str
        params,  # type: Optional[Dict[str, str]]
        headers,  # type: Optional[Dict[str, str]]
        content,  # type: Any
        form_content,  # type: Optional[Dict[str, Any]]
        stream_content,  # type: Any
    ):
        # type: (...) -> HttpRequest
        """Create HttpRequest object.

        If content is not None, guesses will be used to set the right body:
        - If content is an XML tree, will serialize as XML
        - If content-type starts by "text/", set the content as text
        - Else, try JSON serialization

        :param str method: HTTP method (GET, HEAD, etc.)
        :param str url: URL for the request.
        :param dict params: URL query parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = HttpRequest(method, self.format_url(url))

        if params:
            request.format_parameters(params)

        if headers:
            request.headers.update(headers)

        if content is not None:
            content_type = request.headers.get("Content-Type")
            if isinstance(content, ET.Element):
                request.set_xml_body(content)
            # https://github.com/Azure/azure-sdk-for-python/issues/12137
            # A string is valid JSON, make the difference between text
            # and a plain JSON string.
            # Content-Type is a good indicator of intent from user
            elif content_type and content_type.startswith("text/"):
                request.set_text_body(content)
            else:
                try:
                    request.set_json_body(content)
                except TypeError:
                    request.data = content

        if form_content:
            request.set_formdata_body(form_content)
        elif stream_content:
            request.set_streamed_data_body(stream_content)

        return request

    def format_url(self, url_template, **kwargs):
        # type: (str, Any) -> str
        """Format request URL with the client base URL, unless the
        supplied URL is already absolute.

        :param str url_template: The request URL to be formatted if necessary.
        """
        url = _format_url_section(url_template, **kwargs)
        if url:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                url = url.lstrip("/")
                try:
                    base = self._base_url.format(**kwargs).rstrip("/")
                except KeyError as key:
                    err_msg = "The value provided for the url part {} was incorrect, and resulted in an invalid url"
                    raise ValueError(err_msg.format(key.args[0]))

                url = _urljoin(base, url)
        else:
            url = self._base_url.format(**kwargs)
        return url

    def get(
        self,
        url,  # type: str
        params=None,  # type: Optional[Dict[str, str]]
        headers=None,  # type: Optional[Dict[str, str]]
        content=None,  # type: Any
        form_content=None,  # type: Optional[Dict[str, Any]]
    ):
        # type: (...) -> HttpRequest
        """Create a GET request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "GET", url, params, headers, content, form_content, None
        )
        request.method = "GET"
        return request

    def put(
        self,
        url,  # type: str
        params=None,  # type: Optional[Dict[str, str]]
        headers=None,  # type: Optional[Dict[str, str]]
        content=None,  # type: Any
        form_content=None,  # type: Optional[Dict[str, Any]]
        stream_content=None,  # type: Any
    ):
        # type: (...) -> HttpRequest
        """Create a PUT request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "PUT", url, params, headers, content, form_content, stream_content
        )
        return request

    def post(
        self,
        url,  # type: str
        params=None,  # type: Optional[Dict[str, str]]
        headers=None,  # type: Optional[Dict[str, str]]
        content=None,  # type: Any
        form_content=None,  # type: Optional[Dict[str, Any]]
        stream_content=None,  # type: Any
    ):
        # type: (...) -> HttpRequest
        """Create a POST request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "POST", url, params, headers, content, form_content, stream_content
        )
        return request

    def head(
        self,
        url,  # type: str
        params=None,  # type: Optional[Dict[str, str]]
        headers=None,  # type: Optional[Dict[str, str]]
        content=None,  # type: Any
        form_content=None,  # type: Optional[Dict[str, Any]]
        stream_content=None,  # type: Any
    ):
        # type: (...) -> HttpRequest
        """Create a HEAD request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "HEAD", url, params, headers, content, form_content, stream_content
        )
        return request

    def patch(
        self,
        url,  # type: str
        params=None,  # type: Optional[Dict[str, str]]
        headers=None,  # type: Optional[Dict[str, str]]
        content=None,  # type: Any
        form_content=None,  # type: Optional[Dict[str, Any]]
        stream_content=None,  # type: Any
    ):
        # type: (...) -> HttpRequest
        """Create a PATCH request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "PATCH", url, params, headers, content, form_content, stream_content
        )
        return request

    def delete(self, url, params=None, headers=None, content=None, form_content=None):
        # type: (str, Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> HttpRequest
        """Create a DELETE request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "DELETE", url, params, headers, content, form_content, None
        )
        return request

    def merge(self, url, params=None, headers=None, content=None, form_content=None):
        # type: (str, Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> HttpRequest
        """Create a MERGE request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param content: The body content
        :param dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        request = self._request(
            "MERGE", url, params, headers, content, form_content, None
        )
        return request

    def options(self, url, params=None, headers=None, **kwargs):
        # type: (str, Optional[Dict[str, str]], Optional[Dict[str, str]], Any) -> HttpRequest
        """Create a OPTIONS request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :keyword content: The body content
        :keyword dict form_content: Form content
        :return: An HttpRequest object
        :rtype: ~azure.core.pipeline.transport.HttpRequest
        """
        content = kwargs.get("content")
        form_content = kwargs.get("form_content")
        request = self._request(
            "OPTIONS", url, params, headers, content, form_content, None
        )
        return request
