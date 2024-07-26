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
import copy

from typing import TYPE_CHECKING

from ..utils._utils import _case_insensitive_dict
from ._helpers import (
    set_content_body,
    set_json_body,
    set_multipart_body,
    set_urlencoded_body,
    _format_parameters_helper,
    HttpRequestBackcompatMixin,
)
if TYPE_CHECKING:
    from typing import (
        Iterable,
        Optional,
        Any,
        Iterator,
        Union,
        Dict,
        MutableMapping,
    )
    ByteStream = Iterable[bytes]
    ContentType = Union[str, bytes, ByteStream]

    from ._helpers import ContentTypeBase as ContentType

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

################################## CLASSES ######################################

class HttpRequest(HttpRequestBackcompatMixin):
    """HTTP request.

    It should be passed to your client's `send_request` method.

    >>> from azure.core.rest import HttpRequest
    >>> request = HttpRequest('GET', 'http://www.example.com')
    <HttpRequest [GET], url: 'http://www.example.com'>
    >>> response = client.send_request(request)
    <HttpResponse: 200 OK>

    :param str method: HTTP method (GET, HEAD, etc.)
    :param str url: The url for your request
    :keyword mapping params: Query parameters to be mapped into your URL. Your input
     should be a mapping of query name to query value(s).
    :keyword mapping headers: HTTP headers you want in your request. Your input should
     be a mapping of header name to header value.
    :keyword any json: A JSON serializable object. We handle JSON-serialization for your
     object, so use this for more complicated data structures than `data`.
    :keyword content: Content you want in your request body. Think of it as the kwarg you should input
     if your data doesn't fit into `json`, `data`, or `files`. Accepts a bytes type, or a generator
     that yields bytes.
    :paramtype content: str or bytes or iterable[bytes]
    :keyword dict data: Form data you want in your request body. Use for form-encoded data, i.e.
     HTML forms.
    :keyword mapping files: Files you want to in your request body. Use for uploading files with
     multipart encoding. Your input should be a mapping of file name to file content.
     Use the `data` kwarg in addition if you want to include non-file data files as part of your request.
    :ivar str url: The URL this request is against.
    :ivar str method: The method type of this request.
    :ivar mapping headers: The HTTP headers you passed in to your request
    :ivar bytes content: The content passed in for the request
    """

    def __init__(self, method, url, **kwargs):
        # type: (str, str, Any) -> None

        self.url = url
        self.method = method

        params = kwargs.pop("params", None)
        if params:
            _format_parameters_helper(self, params)
        self._files = None
        self._data = None

        default_headers = self._set_body(
            content=kwargs.pop("content", None),
            data=kwargs.pop("data", None),
            files=kwargs.pop("files", None),
            json=kwargs.pop("json", None),
        )
        self.headers = _case_insensitive_dict(default_headers)
        self.headers.update(kwargs.pop("headers", {}))

        if kwargs:
            raise TypeError(
                "You have passed in kwargs '{}' that are not valid kwargs.".format(
                    "', '".join(list(kwargs.keys()))
                )
            )

    def _set_body(self, **kwargs):
        # type: (Any) -> MutableMapping[str, str]
        """Sets the body of the request, and returns the default headers
        """
        content = kwargs.pop("content", None)
        data = kwargs.pop("data", None)
        files = kwargs.pop("files", None)
        json = kwargs.pop("json", None)
        default_headers = {}
        if data is not None and not isinstance(data, dict):
            # should we warn?
            content = data
        if content is not None:
            default_headers, self._data = set_content_body(content)
            return default_headers
        if json is not None:
            default_headers, self._data = set_json_body(json)
            return default_headers
        if files:
            default_headers, self._files = set_multipart_body(files)
        if data:
            default_headers, self._data = set_urlencoded_body(data, bool(files))
        return default_headers

    def _update_headers(self, default_headers):
        # type: (Dict[str, str]) -> None
        for name, value in default_headers.items():
            if name == "Transfer-Encoding" and "Content-Length" in self.headers:
                continue
            self.headers.setdefault(name, value)

    @property
    def content(self):
        # type: (...) -> Any
        """Get's the request's content

        :return: The request's content
        :rtype: any
        """
        return self._data or self._files

    def __repr__(self):
        # type: (...) -> str
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    def __deepcopy__(self, memo=None):
        try:
            request = HttpRequest(
                method=self.method,
                url=self.url,
                headers=self.headers,
            )
            request._data = copy.deepcopy(self._data, memo)
            request._files = copy.deepcopy(self._files, memo)
            self._add_backcompat_properties(request, memo)
            return request
        except (ValueError, TypeError):
            return copy.copy(self)

class _HttpResponseBase(ABC):

    @property
    @abc.abstractmethod
    def request(self):
        # type: (...) -> HttpRequest
        """The request that resulted in this response.

        :rtype: ~azure.core.rest.HttpRequest
        """

    @property
    @abc.abstractmethod
    def status_code(self):
        # type: (...) -> int
        """The status code of this response.

        :rtype: int
        """

    @property
    @abc.abstractmethod
    def headers(self):
        # type: (...) -> Optional[MutableMapping[str, str]]
        """The response headers. Must be case-insensitive.

        :rtype: MutableMapping[str, str]
        """

    @property
    @abc.abstractmethod
    def reason(self):
        # type: (...) -> str
        """The reason phrase for this response.

        :rtype: str
        """

    @property
    @abc.abstractmethod
    def content_type(self):
        # type: (...) -> Optional[str]
        """The content type of the response.

        :rtype: str
        """

    @property
    @abc.abstractmethod
    def is_closed(self):
        # type: (...) -> bool
        """Whether the network connection has been closed yet.

        :rtype: bool
        """

    @property
    @abc.abstractmethod
    def is_stream_consumed(self):
        # type: (...) -> bool
        """Whether the stream has been consumed.

        :rtype: bool
        """

    @property
    @abc.abstractmethod
    def encoding(self):
        # type: (...) -> Optional[str]
        """Returns the response encoding.

        :return: The response encoding. We either return the encoding set by the user,
         or try extracting the encoding from the response's content type. If all fails,
         we return `None`.
        :rtype: optional[str]
        """

    @encoding.setter
    def encoding(self, value):
        # type: (str) -> None
        """Sets the response encoding.

        :rtype: None
        """

    @property
    @abc.abstractmethod
    def url(self):
        # type: (...) -> str
        """The URL that resulted in this response.

        :rtype: str
        """

    @abc.abstractmethod
    def text(self, encoding=None):
        # type: (Optional[str]) -> str
        """Returns the response body as a string.

        :param optional[str] encoding: The encoding you want to decode the text with. Can
         also be set independently through our encoding property
        :return: The response's content decoded as a string.
        :rtype: str
        """

    @abc.abstractmethod
    def json(self):
        # type: (...) -> Any
        """Returns the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """

    @abc.abstractmethod
    def raise_for_status(self):
        # type: (...) -> None
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.

        :rtype: None
        :raises ~azure.core.HttpResponseError if the object has an error status code.:
        """

    @property
    @abc.abstractmethod
    def content(self):
        # type: (...) -> bytes
        """Return the response's content in bytes.

        :rtype: bytes
        """


class HttpResponse(_HttpResponseBase):
    """Abstract base class for HTTP responses.

    Use this abstract base class to create your own transport responses.

    Responses implementing this ABC are returned from your client's `send_request` method
    if you pass in an :class:`~azure.core.rest.HttpRequest`

    >>> from azure.core.rest import HttpRequest
    >>> request = HttpRequest('GET', 'http://www.example.com')
    <HttpRequest [GET], url: 'http://www.example.com'>
    >>> response = client.send_request(request)
    <HttpResponse: 200 OK>
    """

    @abc.abstractmethod
    def __enter__(self):
        # type: (...) -> HttpResponse
        """Enter this response"""

    @abc.abstractmethod
    def close(self):
        # type: (...) -> None
        """Close this response"""

    @abc.abstractmethod
    def __exit__(self, *args):
        # type: (...) -> None
        """Exit this response"""

    @abc.abstractmethod
    def read(self):
        # type: (...) -> bytes
        """Read the response's bytes.

        :return: The read in bytes
        :rtype: bytes
        """

    @abc.abstractmethod
    def iter_raw(self, **kwargs):
        # type: (Any) -> Iterator[bytes]
        """Iterates over the response's bytes. Will not decompress in the process.

        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """

    @abc.abstractmethod
    def iter_bytes(self, **kwargs):
        # type: (Any) -> Iterator[bytes]
        """Iterates over the response's bytes. Will decompress in the process.

        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
