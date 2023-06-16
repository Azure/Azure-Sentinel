# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Protocol that defines what functions wrappers of tracing libraries should implement."""
from enum import Enum
from urllib.parse import urlparse

from typing import (
    TYPE_CHECKING,
    Any,
    Sequence,
    Optional,
    Union,
    Callable,
    ContextManager,
    Dict,
)

if TYPE_CHECKING:
    from azure.core.pipeline.transport import (
        HttpRequest,
        HttpResponse,
        AsyncHttpResponse,
    )

    HttpResponseType = Union[HttpResponse, AsyncHttpResponse]
    AttributeValue = Union[
        str,
        bool,
        int,
        float,
        Sequence[str],
        Sequence[bool],
        Sequence[int],
        Sequence[float],
    ]
    Attributes = Optional[Dict[str, AttributeValue]]

try:
    from typing_extensions import Protocol
except ImportError:
    Protocol = object  # type: ignore


class SpanKind(Enum):
    UNSPECIFIED = 1
    SERVER = 2
    CLIENT = 3
    PRODUCER = 4
    CONSUMER = 5
    INTERNAL = 6


class AbstractSpan(Protocol):
    """Wraps a span from a distributed tracing implementation."""

    def __init__(  # pylint: disable=super-init-not-called
        self, span: Optional[Any] = None, name: Optional[str] = None, **kwargs
    ) -> None:
        """
        If a span is given wraps the span. Else a new span is created.
        The optional argument name is given to the new span.
        """

    def span(self, name: str = "child_span", **kwargs) -> "AbstractSpan":
        """
        Create a child span for the current span and append it to the child spans list.
        The child span must be wrapped by an implementation of AbstractSpan
        """

    @property
    def kind(self) -> Optional[SpanKind]:
        """Get the span kind of this span.

        :rtype: SpanKind
        """

    @kind.setter
    def kind(self, value: SpanKind) -> None:
        """Set the span kind of this span."""

    def __enter__(self):
        """Start a span."""

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""

    def start(self) -> None:
        """Set the start time for a span."""

    def finish(self) -> None:
        """Set the end time for a span."""

    def to_header(self) -> Dict[str, str]:
        """
        Returns a dictionary with the header labels and values.
        """

    def add_attribute(self, key: str, value: Union[str, int]) -> None:
        """
        Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: Union[str, int]
        """

    def set_http_attributes(self, request: "HttpRequest", response: Optional["HttpResponseType"] = None) -> None:
        """
        Add correct attributes for a http client span.

        :param request: The request made
        :type request: HttpRequest
        :param response: The response received by the server. Is None if no response received.
        :type response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
        """

    def get_trace_parent(self) -> str:
        """Return traceparent string.

        :return: a traceparent string
        :rtype: str
        """

    @property
    def span_instance(self) -> Any:
        """
        Returns the span the class is wrapping.
        """

    @classmethod
    def link(cls, traceparent: str, attributes: Optional["Attributes"] = None) -> None:
        """
        Given a traceparent, extracts the context and links the context to the current tracer.

        :param traceparent: A string representing a traceparent
        :type traceparent: str
        """

    @classmethod
    def link_from_headers(cls, headers: Dict[str, str], attributes: Optional["Attributes"] = None) -> None:
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A dictionary of the request header as key value pairs.
        :type headers: dict
        """

    @classmethod
    def get_current_span(cls) -> Any:
        """
        Get the current span from the execution context. Return None otherwise.
        """

    @classmethod
    def get_current_tracer(cls) -> Any:
        """
        Get the current tracer from the execution context. Return None otherwise.
        """

    @classmethod
    def set_current_span(cls, span: Any) -> None:
        """
        Set the given span as the current span in the execution context.
        """

    @classmethod
    def set_current_tracer(cls, tracer: Any) -> None:
        """
        Set the given tracer as the current tracer in the execution context.
        """

    @classmethod
    def change_context(cls, span: "AbstractSpan") -> ContextManager:
        """Change the context for the life of this context manager.

        :rtype: contextmanager
        """

    @classmethod
    def with_current_context(cls, func: Callable) -> Callable:
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        :rtype: callable
        """


# https://github.com/python/mypy/issues/5837
if TYPE_CHECKING:
    _MIXIN_BASE = AbstractSpan
else:
    _MIXIN_BASE = object


class HttpSpanMixin(_MIXIN_BASE):
    """Can be used to get HTTP span attributes settings for free."""

    _SPAN_COMPONENT = "component"
    _HTTP_USER_AGENT = "http.user_agent"
    _HTTP_METHOD = "http.method"
    _HTTP_URL = "http.url"
    _HTTP_STATUS_CODE = "http.status_code"
    _NET_PEER_NAME = "net.peer.name"
    _NET_PEER_PORT = "net.peer.port"

    def set_http_attributes(self, request: "HttpRequest", response: Optional["HttpResponseType"] = None) -> None:
        """
        Add correct attributes for a http client span.

        :param request: The request made
        :type request: HttpRequest
        :param response: The response received from the server. Is None if no response received.
        :type response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
        """
        self.kind = SpanKind.CLIENT
        self.add_attribute(self._SPAN_COMPONENT, "http")
        self.add_attribute(self._HTTP_METHOD, request.method)
        self.add_attribute(self._HTTP_URL, request.url)

        parsed_url = urlparse(request.url)
        if parsed_url.hostname:
            self.add_attribute(self._NET_PEER_NAME, parsed_url.hostname)
        if parsed_url.port and parsed_url.port not in [80, 443]:
            self.add_attribute(self._NET_PEER_PORT, parsed_url.port)

        user_agent = request.headers.get("User-Agent")
        if user_agent:
            self.add_attribute(self._HTTP_USER_AGENT, user_agent)
        if response and response.status_code:
            self.add_attribute(self._HTTP_STATUS_CODE, response.status_code)
        else:
            self.add_attribute(self._HTTP_STATUS_CODE, 504)


class Link:
    """
    This is a wrapper class to link the context to the current tracer.
    :param headers: A dictionary of the request header as key value pairs.
    :type headers: dict
    :param attributes: Any additional attributes that should be added to link
    :type attributes: dict
    """

    def __init__(self, headers: Dict[str, str], attributes: Optional["Attributes"] = None) -> None:
        self.headers = headers
        self.attributes = attributes
