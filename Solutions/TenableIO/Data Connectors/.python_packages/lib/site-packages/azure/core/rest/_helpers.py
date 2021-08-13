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
import os
import codecs
import cgi
from enum import Enum
from json import dumps
import collections
from typing import (
    Optional,
    Union,
    Mapping,
    Sequence,
    List,
    Tuple,
    IO,
    Any,
    Dict,
    Iterable,
    Iterator,
    cast,
    Callable,
)
import xml.etree.ElementTree as ET
import six
try:
    from urlparse import urlparse  # type: ignore
except ImportError:
    from urllib.parse import urlparse

################################### TYPES SECTION #########################

PrimitiveData = Optional[Union[str, int, float, bool]]


ParamsType = Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]]

HeadersType = Mapping[str, str]

FileContent = Union[str, bytes, IO[str], IO[bytes]]
FileType = Union[
    Tuple[Optional[str], FileContent],
]

FilesType = Union[
    Mapping[str, FileType],
    Sequence[Tuple[str, FileType]]
]

ContentTypeBase = Union[str, bytes, Iterable[bytes]]

class HttpVerbs(str, Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    HEAD = "HEAD"
    PATCH = "PATCH"
    DELETE = "DELETE"
    MERGE = "MERGE"

########################### ERRORS SECTION #################################



########################### HELPER SECTION #################################

def _verify_data_object(name, value):
    if not isinstance(name, str):
        raise TypeError(
            "Invalid type for data name. Expected str, got {}: {}".format(
                type(name), name
            )
        )
    if value is not None and not isinstance(value, (str, bytes, int, float)):
        raise TypeError(
            "Invalid type for data value. Expected primitive type, got {}: {}".format(
                type(name), name
            )
        )

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

def set_urlencoded_body(data, has_files):
    body = {}
    default_headers = {}
    for f, d in data.items():
        if not d:
            continue
        if isinstance(d, list):
            for item in d:
                _verify_data_object(f, item)
        else:
            _verify_data_object(f, d)
        body[f] = d
    if not has_files:
        # little hacky, but for files we don't send a content type with
        # boundary so requests / aiohttp etc deal with it
        default_headers["Content-Type"] = "application/x-www-form-urlencoded"
    return default_headers, body

def set_multipart_body(files):
    formatted_files = {
        f: _format_data(d) for f, d in files.items() if d is not None
    }
    return {}, formatted_files

def set_xml_body(content):
    headers = {}
    bytes_content = ET.tostring(content, encoding="utf8")
    body = bytes_content.replace(b"encoding='utf8'", b"encoding='utf-8'")
    if body:
        headers["Content-Length"] = str(len(body))
    return headers, body

def _shared_set_content_body(content):
    # type: (Any) -> Tuple[HeadersType, Optional[ContentTypeBase]]
    headers = {}  # type: HeadersType

    if isinstance(content, ET.Element):
        # XML body
        return set_xml_body(content)
    if isinstance(content, (str, bytes)):
        headers = {}
        body = content
        if isinstance(content, six.string_types):
            headers["Content-Type"] = "text/plain"
        if body:
            headers["Content-Length"] = str(len(body))
        return headers, body
    if isinstance(content, collections.Iterable):
        return {}, content
    return headers, None

def set_content_body(content):
    headers, body = _shared_set_content_body(content)
    if body is not None:
        return headers, body
    raise TypeError(
        "Unexpected type for 'content': '{}'. ".format(type(content)) +
        "We expect 'content' to either be str, bytes, or an Iterable"
    )

def set_json_body(json):
    # type: (Any) -> Tuple[Dict[str, str], Any]
    body = dumps(json)
    return {
        "Content-Type": "application/json",
        "Content-Length": str(len(body))
    }, body

def format_parameters(url, params):
    """Format parameters into a valid query string.
    It's assumed all parameters have already been quoted as
    valid URL strings.

    :param dict params: A dictionary of parameters.
    """
    query = urlparse(url).query
    if query:
        url = url.partition("?")[0]
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
    url += query
    return url

def lookup_encoding(encoding):
    # type: (str) -> bool
    # including check for whether encoding is known taken from httpx
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False

def parse_lines_from_text(text):
    # largely taken from httpx's LineDecoder code
    lines = []
    last_chunk_of_text = ""
    while text:
        text_length = len(text)
        for idx in range(text_length):
            curr_char = text[idx]
            next_char = None if idx == len(text) - 1 else text[idx + 1]
            if curr_char == "\n":
                lines.append(text[: idx + 1])
                text = text[idx + 1: ]
                break
            if curr_char == "\r" and next_char == "\n":
                # if it ends with \r\n, we only do \n
                lines.append(text[:idx] + "\n")
                text = text[idx + 2:]
                break
            if curr_char == "\r" and next_char is not None:
                # if it's \r then a normal character, we switch \r to \n
                lines.append(text[:idx] + "\n")
                text = text[idx + 1:]
                break
            if next_char is None:
                last_chunk_of_text += text
                text = ""
                break
    if last_chunk_of_text.endswith("\r"):
        # if ends with \r, we switch \r to \n
        lines.append(last_chunk_of_text[:-1] + "\n")
    elif last_chunk_of_text:
        lines.append(last_chunk_of_text)
    return lines

def to_pipeline_transport_request_helper(rest_request):
    from ..pipeline.transport import HttpRequest as PipelineTransportHttpRequest
    return PipelineTransportHttpRequest(
        method=rest_request.method,
        url=rest_request.url,
        headers=rest_request.headers,
        files=rest_request._files,  # pylint: disable=protected-access
        data=rest_request._data  # pylint: disable=protected-access
    )

def from_pipeline_transport_request_helper(request_class, pipeline_transport_request):
    return request_class(
        method=pipeline_transport_request.method,
        url=pipeline_transport_request.url,
        headers=pipeline_transport_request.headers,
        files=pipeline_transport_request.files,
        data=pipeline_transport_request.data
    )

def get_charset_encoding(response):
    # type: (...) -> Optional[str]
    content_type = response.headers.get("Content-Type")

    if not content_type:
        return None
    _, params = cgi.parse_header(content_type)
    encoding = params.get('charset') # -> utf-8
    if encoding is None or not lookup_encoding(encoding):
        return None
    return encoding

def decode_to_text(encoding, content):
    # type: (Optional[str], bytes) -> str
    if encoding == "utf-8":
        encoding = "utf-8-sig"
    if encoding:
        return content.decode(encoding)
    return codecs.getincrementaldecoder("utf-8-sig")(errors="replace").decode(content)
