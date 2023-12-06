# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import absolute_import

from io import BytesIO
from email.message import Message

try:
    from email import message_from_bytes as message_parser
except ImportError:  # 2.7
    from email import message_from_string as message_parser  # type: ignore
import os
from typing import TYPE_CHECKING, cast, IO

from six.moves.http_client import HTTPConnection

try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse

from ..pipeline import (
    PipelineRequest,
    PipelineResponse,
    PipelineContext,
)
from ..pipeline._tools import await_result as _await_result

if TYPE_CHECKING:
    from typing import (  # pylint: disable=ungrouped-imports
        Dict,
        List,
        Union,
        Tuple,
        Optional,
        Callable,
        Type,
        Iterator,
    )
    # importing both the py3 RestHttpRequest and the fallback RestHttpRequest
    from azure.core.rest._rest_py3 import HttpRequest as RestHttpRequestPy3
    from azure.core.rest._rest import HttpRequest as RestHttpRequestPy2
    from azure.core.pipeline.transport import (
        HttpRequest as PipelineTransportHttpRequest
    )
    HTTPRequestType = Union[
        RestHttpRequestPy3, RestHttpRequestPy2, PipelineTransportHttpRequest
    ]
    from ..pipeline.policies import SansIOHTTPPolicy
    from azure.core.pipeline.transport import (
        HttpResponse as PipelineTransportHttpResponse,
        AioHttpTransportResponse as PipelineTransportAioHttpTransportResponse,
    )
    from azure.core.pipeline.transport._base import (
        _HttpResponseBase as PipelineTransportHttpResponseBase
    )

class BytesIOSocket(object):
    """Mocking the "makefile" of socket for HTTPResponse.
    This can be used to create a http.client.HTTPResponse object
    based on bytes and not a real socket.
    """

    def __init__(self, bytes_data):
        self.bytes_data = bytes_data

    def makefile(self, *_):
        return BytesIO(self.bytes_data)

def _format_parameters_helper(http_request, params):
    """Helper for format_parameters.

    Format parameters into a valid query string.
    It's assumed all parameters have already been quoted as
    valid URL strings.

    :param http_request: The http request whose parameters
     we are trying to format
    :param dict params: A dictionary of parameters.
    """
    query = urlparse(http_request.url).query
    if query:
        http_request.url = http_request.url.partition("?")[0]
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
    http_request.url = http_request.url + query

def _pad_attr_name(attr, backcompat_attrs):
    # type: (str, List[str]) -> str
    """Pad hidden attributes so users can access them.

    Currently, for our backcompat attributes, we define them
    as private, so they're hidden from intellisense and sphinx,
    but still allow users to access them as public attributes
    for backcompat purposes. This function is called so if
    users access publicly call a private backcompat attribute,
    we can return them the private variable in getattr
    """
    return "_{}".format(attr) if attr in backcompat_attrs else attr

def _prepare_multipart_body_helper(http_request, content_index=0):
    # type: (HTTPRequestType, int) -> int
    """Helper for prepare_multipart_body.

    Will prepare the body of this request according to the multipart information.

    This call assumes the on_request policies have been applied already in their
    correct context (sync/async)

    Does nothing if "set_multipart_mixed" was never called.
    :param http_request: The http request whose multipart body we are trying
     to prepare
    :param int content_index: The current index of parts within the batch message.
    :returns: The updated index after all parts in this request have been added.
    :rtype: int
    """
    if not http_request.multipart_mixed_info:
        return 0

    requests = http_request.multipart_mixed_info[0]  # type: List[HTTPRequestType]
    boundary = http_request.multipart_mixed_info[2]  # type: Optional[str]

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
    http_request.set_bytes_body(body)
    http_request.headers["Content-Type"] = (
        "multipart/mixed; boundary=" + main_message.get_boundary()
    )
    return content_index

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
    # type: (HTTPRequestType) -> bytes
    """Helper for serialize.

    Serialize a request using the application/http spec/

    :param http_request: The http request which we are trying
     to serialize.
    :rtype: bytes
    """
    serializer = _HTTPSerializer()
    serializer.request(
        method=http_request.method,
        url=http_request.url,
        body=http_request.body,
        headers=http_request.headers,
    )
    return serializer.buffer

def _decode_parts_helper(
    response,  # type: PipelineTransportHttpResponseBase
    message,  # type: Message
    http_response_type,  # type: Type[PipelineTransportHttpResponseBase]
    requests,  # type: List[PipelineTransportHttpRequest]
    deserialize_response  # type: Callable
):
    # type: (...) -> List[PipelineTransportHttpResponse]
    """Helper for _decode_parts.

    Rebuild an HTTP response from pure string.
    """
    responses = []
    for index, raw_reponse in enumerate(message.get_payload()):
        content_type = raw_reponse.get_content_type()
        if content_type == "application/http":
            responses.append(
                deserialize_response(
                    raw_reponse.get_payload(decode=True),
                    requests[index],
                    http_response_type=http_response_type,
                )
            )
        elif content_type == "multipart/mixed" and requests[index].multipart_mixed_info:
            # The message batch contains one or more change sets
            changeset_requests = requests[index].multipart_mixed_info[0]  # type: ignore
            changeset_responses = response._decode_parts(raw_reponse, http_response_type, changeset_requests)  # pylint: disable=protected-access
            responses.extend(changeset_responses)
        else:
            raise ValueError(
                "Multipart doesn't support part other than application/http for now"
            )
    return responses

def _get_raw_parts_helper(response, http_response_type):
    """Helper for _get_raw_parts

    Assuming this body is multipart, return the iterator or parts.

    If parts are application/http use http_response_type or HttpClientTransportResponse
    as enveloppe.
    """
    body_as_bytes = response.body()
    # In order to use email.message parser, I need full HTTP bytes. Faking something to make the parser happy
    http_body = (
        b"Content-Type: "
        + response.content_type.encode("ascii")
        + b"\r\n\r\n"
        + body_as_bytes
    )
    message = message_parser(http_body)  # type: Message
    requests = response.request.multipart_mixed_info[0]
    return response._decode_parts(message, http_response_type, requests)  # pylint: disable=protected-access

def _parts_helper(response):
    # type: (PipelineTransportHttpResponse) -> Iterator[PipelineTransportHttpResponse]
    """Assuming the content-type is multipart/mixed, will return the parts as an iterator.

    :rtype: iterator[HttpResponse]
    :raises ValueError: If the content is not multipart/mixed
    """
    if not response.content_type or not response.content_type.startswith("multipart/mixed"):
        raise ValueError(
            "You can't get parts if the response is not multipart/mixed"
        )

    responses = response._get_raw_parts()  # pylint: disable=protected-access
    if response.request.multipart_mixed_info:
        policies = response.request.multipart_mixed_info[1]  # type: List[SansIOHTTPPolicy]

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

def _format_data_helper(data):
    # type: (Union[str, IO]) -> Union[Tuple[None, str], Tuple[Optional[str], IO, str]]
    """Helper for _format_data.

    Format field data according to whether it is a stream or
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

def _aiohttp_body_helper(response):
    # pylint: disable=protected-access
    # type: (PipelineTransportAioHttpTransportResponse) -> bytes
    """Helper for body method of Aiohttp responses.

    Since aiohttp body methods need decompression work synchronously,
    need to share thid code across old and new aiohttp transport responses
    for backcompat.

    :rtype: bytes
    """
    if response._content is None:
        raise ValueError("Body is not available. Call async method load_body, or do your call with stream=False.")
    if not response._decompress:
        return response._content
    if response._decompressed_content:
        return response._content
    enc = response.headers.get('Content-Encoding')
    if not enc:
        return response._content
    enc = enc.lower()
    if enc in ("gzip", "deflate"):
        import zlib
        zlib_mode = 16 + zlib.MAX_WBITS if enc == "gzip" else zlib.MAX_WBITS
        decompressor = zlib.decompressobj(wbits=zlib_mode)
        response._content = decompressor.decompress(response._content)
        response._decompressed_content = True
        return response._content
    return response._content
