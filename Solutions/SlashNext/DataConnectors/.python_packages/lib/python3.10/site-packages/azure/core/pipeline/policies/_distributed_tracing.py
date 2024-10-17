# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Traces network calls using the implementation library from the settings."""
import logging
import sys
import urllib.parse
from typing import TYPE_CHECKING, Optional, Tuple, TypeVar, Union, Any, Type
from types import TracebackType

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpResponse as LegacyHttpResponse, HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpResponse, HttpRequest
from azure.core.settings import settings
from azure.core.tracing import SpanKind

if TYPE_CHECKING:
    from azure.core.tracing._abstract_span import (
        AbstractSpan,
    )

HTTPResponseType = TypeVar("HTTPResponseType", HttpResponse, LegacyHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)
ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, Tuple[None, None, None]]

_LOGGER = logging.getLogger(__name__)


def _default_network_span_namer(http_request: HTTPRequestType) -> str:
    """Extract the path to be used as network span name.

    :param http_request: The HTTP request
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :returns: The string to use as network span name
    :rtype: str
    """
    path = urllib.parse.urlparse(http_request.url).path
    if not path:
        path = "/"
    return path


class DistributedTracingPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """The policy to create spans for Azure calls.

    :keyword network_span_namer: A callable to customize the span name
    :type network_span_namer: callable[[~azure.core.pipeline.transport.HttpRequest], str]
    :keyword tracing_attributes: Attributes to set on all created spans
    :type tracing_attributes: dict[str, str]
    """

    TRACING_CONTEXT = "TRACING_CONTEXT"
    _REQUEST_ID = "x-ms-client-request-id"
    _RESPONSE_ID = "x-ms-request-id"
    _HTTP_RESEND_COUNT = "http.request.resend_count"

    def __init__(self, **kwargs: Any):
        self._network_span_namer = kwargs.get("network_span_namer", _default_network_span_namer)
        self._tracing_attributes = kwargs.get("tracing_attributes", {})

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        ctxt = request.context.options
        try:
            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return

            namer = ctxt.pop("network_span_namer", self._network_span_namer)
            span_name = namer(request.http_request)

            span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
            for attr, value in self._tracing_attributes.items():
                span.add_attribute(attr, value)
            span.start()

            headers = span.to_header()
            request.http_request.headers.update(headers)

            request.context[self.TRACING_CONTEXT] = span
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Unable to start network span: %s", err)

    def end_span(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: Optional[HTTPResponseType] = None,
        exc_info: Optional[OptExcInfo] = None,
    ) -> None:
        """Ends the span that is tracing the network and updates its status.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The HttpResponse object
        :type response: ~azure.core.rest.HTTPResponse or ~azure.core.pipeline.transport.HttpResponse
        :param exc_info: The exception information
        :type exc_info: tuple
        """
        if self.TRACING_CONTEXT not in request.context:
            return

        span: "AbstractSpan" = request.context[self.TRACING_CONTEXT]
        http_request: Union[HttpRequest, LegacyHttpRequest] = request.http_request
        if span is not None:
            span.set_http_attributes(http_request, response=response)
            if request.context.get("retry_count"):
                span.add_attribute(self._HTTP_RESEND_COUNT, request.context["retry_count"])
            request_id = http_request.headers.get(self._REQUEST_ID)
            if request_id is not None:
                span.add_attribute(self._REQUEST_ID, request_id)
            if response and self._RESPONSE_ID in response.headers:
                span.add_attribute(self._RESPONSE_ID, response.headers[self._RESPONSE_ID])
            if exc_info:
                span.__exit__(*exc_info)
            else:
                span.finish()

    def on_response(
        self, request: PipelineRequest[HTTPRequestType], response: PipelineResponse[HTTPRequestType, HTTPResponseType]
    ) -> None:
        self.end_span(request, response=response.http_response)

    def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None:
        self.end_span(request, exc_info=sys.exc_info())
