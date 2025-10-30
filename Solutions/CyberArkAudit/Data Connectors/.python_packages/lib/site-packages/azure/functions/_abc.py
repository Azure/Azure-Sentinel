# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import datetime
import io
import threading
import typing

from azure.functions._thirdparty.werkzeug.datastructures import Headers

T = typing.TypeVar('T')


class Out(abc.ABC, typing.Generic[T]):
    """An interface to set function output parameters."""

    @abc.abstractmethod
    def set(self, val: T) -> None:
        """Set the value of the output parameter."""
        pass

    @abc.abstractmethod
    def get(self) -> T:
        """Get the value of the output parameter."""
        pass


class RpcException:
    """Rpc Exception object."""

    @property
    @abc.abstractmethod
    def source(self) -> str:
        """Source of the exception."""
        pass

    @property
    @abc.abstractmethod
    def stack_trace(self) -> str:
        """Stack trace for the exception."""
        pass

    @property
    @abc.abstractmethod
    def message(self) -> str:
        """Textual message describing the exception."""
        pass


class TraceContext(abc.ABC):
    """Trace context object."""

    @property
    @abc.abstractmethod
    def trace_state(self) -> str:
        """Gets trace state from trace-context."""
        pass

    @property
    @abc.abstractmethod
    def trace_parent(self) -> str:
        """Gets trace parent from trace-context."""
        pass

    @property
    @abc.abstractmethod
    def attributes(self) -> typing.Dict[str, str]:
        """Gets trace-context attributes."""
        pass


class RetryContext(abc.ABC):
    """Retry Context object.
       For more information refer: https://aka.ms/azfunc-retries-policies
    """

    @property
    @abc.abstractmethod
    def retry_count(self) -> int:
        """Gets the current retry count from retry-context."""
        pass

    @property
    @abc.abstractmethod
    def max_retry_count(self) -> int:
        """Gets the max retry count from retry-context."""
        pass

    @property
    @abc.abstractmethod
    def exception(self) -> RpcException:
        """Gets the RpcException"""
        pass


class Context(abc.ABC):
    """Function invocation context."""

    @property
    @abc.abstractmethod
    def invocation_id(self) -> str:
        """Function invocation ID."""
        pass

    @property
    @abc.abstractmethod
    def thread_local_storage(self) -> typing.Type[threading.local]:
        """Thread local storage.

        :attribute str invocation_id:
            Invocation ID contained in local thread storage.
            Enables logging from user threads when set to
            the current context's invocation ID.
        """
        pass

    @property
    @abc.abstractmethod
    def function_name(self) -> str:
        """Function name."""
        pass

    @property
    @abc.abstractmethod
    def function_directory(self) -> str:
        """Function directory."""
        pass

    @property
    @abc.abstractmethod
    def trace_context(self) -> TraceContext:
        """Context for distributed tracing."""
        pass

    @property
    @abc.abstractmethod
    def retry_context(self) -> RetryContext:
        """Context for retries to the function."""
        pass


class HttpRequest(abc.ABC):
    """HTTP request object."""

    @property
    @abc.abstractmethod
    def method(self) -> str:
        """Request method."""
        pass

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """Request URL."""
        pass

    @property
    @abc.abstractmethod
    def headers(self) -> typing.Mapping[str, str]:
        """A dictionary containing request headers."""
        pass

    @property
    @abc.abstractmethod
    def params(self) -> typing.Mapping[str, str]:
        """A dictionary containing request GET parameters."""
        pass

    @property
    @abc.abstractmethod
    def route_params(self) -> typing.Mapping[str, str]:
        """A dictionary containing request route parameters."""
        pass

    @abc.abstractmethod
    def get_body(self) -> bytes:
        """Return request body as bytes."""
        pass

    @abc.abstractmethod
    def get_json(self) -> typing.Any:
        """Decode and return request body as JSON.

        :raises ValueError:
            when the request does not contain valid JSON data.
        """
        pass


class HttpResponse(abc.ABC):

    @property
    @abc.abstractmethod
    def status_code(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def mimetype(self):
        pass

    @property
    @abc.abstractmethod
    def charset(self):
        pass

    @property
    @abc.abstractmethod
    def headers(self) -> Headers:
        pass

    @abc.abstractmethod
    def get_body(self) -> bytes:
        pass


class TimerRequest(abc.ABC):
    """Timer request object."""

    @property
    @abc.abstractmethod
    def past_due(self) -> bool:
        """Whether the timer is past due."""
        pass


class InputStream(io.BufferedIOBase, abc.ABC):
    """File-like object representing an input blob."""

    @abc.abstractmethod
    def read(self, size=-1) -> bytes:
        """Return and read up to *size* bytes.

        :param int size:
            The number of bytes to read.  If the argument is omitted,
            ``None``, or negative, data is read and returned until
            EOF is reached.

        :return:
            Bytes read from the input stream.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> typing.Optional[str]:
        """The name of the blob."""
        pass

    @property
    @abc.abstractmethod
    def length(self) -> typing.Optional[int]:
        """The size of the blob in bytes."""
        pass

    @property
    @abc.abstractmethod
    def uri(self) -> typing.Optional[str]:
        """The blob's primary location URI."""
        pass


class QueueMessage(abc.ABC):

    @property
    @abc.abstractmethod
    def id(self) -> typing.Optional[str]:
        pass

    @abc.abstractmethod
    def get_body(self) -> typing.Union[str, bytes]:
        pass

    @abc.abstractmethod
    def get_json(self) -> typing.Any:
        pass

    @property
    @abc.abstractmethod
    def dequeue_count(self) -> typing.Optional[int]:
        pass

    @property
    @abc.abstractmethod
    def expiration_time(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def insertion_time(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def time_next_visible(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def pop_receipt(self) -> typing.Optional[str]:
        pass


class EventGridEvent(abc.ABC):
    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    @abc.abstractmethod
    def get_json(self) -> typing.Any:
        pass

    @property
    @abc.abstractmethod
    def topic(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def subject(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def event_type(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def event_time(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def data_version(self) -> str:
        pass


class EventGridOutputEvent(abc.ABC):
    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    @abc.abstractmethod
    def get_json(self) -> typing.Any:
        pass

    @property
    @abc.abstractmethod
    def subject(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def event_type(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def event_time(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def data_version(self) -> str:
        pass


class Document(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def from_json(cls, json_data: str) -> 'Document':
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, dct: dict) -> 'Document':
        pass

    @abc.abstractmethod
    def __getitem__(self, key):
        pass

    @abc.abstractmethod
    def __setitem__(self, key, value):
        pass

    @abc.abstractmethod
    def to_json(self) -> str:
        pass

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass


class DocumentList(abc.ABC):
    pass


class EventHubEvent(abc.ABC):

    @abc.abstractmethod
    def get_body(self) -> bytes:
        pass

    @property
    @abc.abstractmethod
    def partition_key(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def sequence_number(self) -> typing.Optional[int]:
        pass

    @property
    @abc.abstractmethod
    def iothub_metadata(self) -> typing.Optional[typing.Mapping[str, str]]:
        pass

    @property
    @abc.abstractmethod
    def enqueued_time(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def offset(self) -> typing.Optional[str]:
        pass


class OrchestrationContext(abc.ABC):
    @property
    @abc.abstractmethod
    def body(self) -> str:
        pass


class ServiceBusMessage(abc.ABC):

    @abc.abstractmethod
    def get_body(self) -> typing.Union[str, bytes]:
        pass

    @property
    @abc.abstractmethod
    def content_type(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def correlation_id(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def dead_letter_source(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def delivery_count(self) -> typing.Optional[int]:
        pass

    @property
    @abc.abstractmethod
    def enqueued_time_utc(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def expires_at_utc(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def expiration_time(self) -> typing.Optional[datetime.datetime]:
        """(Deprecated, use expires_at_utc instead)"""
        pass

    @property
    @abc.abstractmethod
    def label(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def lock_token(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def message_id(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def partition_key(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def reply_to(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def reply_to_session_id(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def scheduled_enqueue_time(self) -> typing.Optional[datetime.datetime]:
        """(Deprecated, use scheduled_enqueue_time_utc instead)"""
        pass

    @property
    @abc.abstractmethod
    def scheduled_enqueue_time_utc(self) -> typing.Optional[datetime.datetime]:
        pass

    @property
    @abc.abstractmethod
    def sequence_number(self) -> typing.Optional[int]:
        pass

    @property
    @abc.abstractmethod
    def session_id(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def time_to_live(self) -> typing.Optional[datetime.timedelta]:
        pass

    @property
    @abc.abstractmethod
    def to(self) -> typing.Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def user_properties(self) -> typing.Dict[str, typing.Any]:
        pass

    @property
    @abc.abstractmethod
    def metadata(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        pass
