# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections.abc
import http
import io
import types
import typing

from ._jsonutils import json
from werkzeug import formparser as _wk_parser
from werkzeug import http as _wk_http
from werkzeug.datastructures import (Headers, FileStorage, MultiDict,
                                     ImmutableMultiDict)

from . import _abc


class BaseHeaders(collections.abc.Mapping):

    def __init__(self, source: typing.Optional[typing.Mapping] = None) -> None:
        self.__http_headers__: typing.Dict[str, str] = {}

        if source is not None:
            self.__http_headers__.update(
                {k.lower(): v for k, v in source.items()})

    def __getitem__(self, key: str) -> str:
        return self.__http_headers__[key.lower()]

    def __len__(self):
        return len(self.__http_headers__)

    def __contains__(self, key: typing.Any):
        return key.lower() in self.__http_headers__

    def __iter__(self):
        return iter(self.__http_headers__)


class HttpRequestHeaders(BaseHeaders):
    pass


class HttpResponseHeaders(Headers):
    pass


class HttpResponse(_abc.HttpResponse):
    """An HTTP response object.

    :param str/bytes body:
        Optional response body.

    :param int status_code:
        Response status code.  If not specified, defaults to 200.
        You can use an int status code or an http.HTTPStatus value

    :param dict headers:
        An optional mapping containing response HTTP headers.

    :param str mimetype:
        An optional response MIME type.  If not specified, defaults to
        ``'text/plain'``.

    :param str charset:
        Response content text encoding.  If not specified, defaults to
        ``'utf-8'``.
    """

    def __init__(self,
                 body: typing.Optional[typing.Union[str, bytes]] = None, *,
                 status_code: typing.Optional[typing.Union[
                     http.HTTPStatus, int
                 ]] = None,
                 headers: typing.Optional[typing.Mapping[str, str]] = None,
                 mimetype: typing.Optional[str] = None,
                 charset: typing.Optional[str] = None) -> None:
        if status_code is None:
            status_code = 200
        if isinstance(status_code, http.HTTPStatus):
            status_code = status_code.value
        self.__status_code = status_code

        if mimetype is None:
            mimetype = 'text/plain'
        self.__mimetype = mimetype

        if charset is None:
            charset = 'utf-8'
        self.__charset = charset

        if headers is None:
            headers = {}

        self.__headers = HttpResponseHeaders([])
        for k, v in headers.items():
            self.__headers.add_header(k, v)

        if body is not None:
            self.__set_body(body)
        else:
            self.__body = b''

    @property
    def mimetype(self):
        """Response MIME type."""
        return self.__mimetype

    @property
    def charset(self):
        """Response text encoding."""
        return self.__charset

    @property
    def headers(self):
        """A dictionary of response HTTP headers."""
        return self.__headers

    @property
    def status_code(self):
        """Response status code."""
        return self.__status_code

    def __set_body(self, body):
        if isinstance(body, str):
            body = body.encode(self.__charset)

        if not isinstance(body, (bytes, bytearray)):
            raise TypeError(
                f'response is expected to be either of '
                f'str, bytes, or bytearray, got {type(body).__name__}')

        self.__body = bytes(body)

    def get_body(self) -> bytes:
        """Response body as a bytes object."""
        return self.__body


class HttpRequest(_abc.HttpRequest):
    """An HTTP request object.

    :param str method:
        HTTP request method name.

    :param str url:
        HTTP URL.

    :param dict headers:
        An optional mapping containing HTTP request headers.

    :param dict params:
        An optional mapping containing HTTP request params.

    :param dict route_params:
        An optional mapping containing HTTP request route params.

    :param bytes body:
        HTTP request body.
    """

    def __init__(self,
                 method: str,
                 url: str, *,
                 headers: typing.Optional[typing.Mapping[str, str]] = None,
                 params: typing.Optional[typing.Mapping[str, str]] = None,
                 route_params: typing.Optional[
                     typing.Mapping[str, str]] = None,
                 body: bytes) -> None:
        self.__method = method
        self.__url = url
        self.__headers = HttpRequestHeaders(headers or {})
        self.__params = types.MappingProxyType(params or {})
        self.__route_params = types.MappingProxyType(route_params or {})
        self.__body_bytes = body
        self.__form_parsed = False
        self.__form: MultiDict[str, str]
        self.__files: MultiDict[str, FileStorage]

    @property
    def url(self):
        return self.__url

    @property
    def method(self):
        return self.__method.upper()

    @property
    def headers(self):
        return self.__headers

    @property
    def params(self):
        return self.__params

    @property
    def route_params(self):
        return self.__route_params

    @property
    def form(self):
        self._parse_form_data()
        return self.__form

    @property
    def files(self):
        self._parse_form_data()
        return self.__files

    def get_body(self) -> bytes:
        return self.__body_bytes

    def get_json(self) -> typing.Any:
        return json.loads(self.__body_bytes.decode('utf-8'))

    def _parse_form_data(self):
        if self.__form_parsed:
            return

        body = self.get_body()
        content_type = self.headers.get('Content-Type', '')
        content_length = len(body)
        mimetype, options = _wk_http.parse_options_header(content_type)
        parser = _wk_parser.FormDataParser(
            _wk_parser.default_stream_factory, max_form_memory_size=None,
            max_content_length=None,
            cls=ImmutableMultiDict
        )

        body_stream = io.BytesIO(body)

        _, self.__form, self.__files = parser.parse(
            body_stream, mimetype, content_length, options
        )

        self.__form_parsed = True
