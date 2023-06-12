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
import base64
import logging
import threading
import uuid
from typing import TypeVar, Generic, Any, Callable, Optional, Tuple, List
from azure.core.exceptions import AzureError
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.common import with_current_context


PollingReturnType = TypeVar("PollingReturnType")

_LOGGER = logging.getLogger(__name__)


class PollingMethod(Generic[PollingReturnType]):
    """ABC class for polling method."""

    def initialize(self, client: Any, initial_response: Any, deserialization_callback: Any) -> None:
        raise NotImplementedError("This method needs to be implemented")

    def run(self) -> None:
        raise NotImplementedError("This method needs to be implemented")

    def status(self) -> str:
        raise NotImplementedError("This method needs to be implemented")

    def finished(self) -> bool:
        raise NotImplementedError("This method needs to be implemented")

    def resource(self) -> PollingReturnType:
        raise NotImplementedError("This method needs to be implemented")

    def get_continuation_token(self) -> str:
        raise TypeError("Polling method '{}' doesn't support get_continuation_token".format(self.__class__.__name__))

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs) -> Tuple[Any, Any, Callable]:
        raise TypeError("Polling method '{}' doesn't support from_continuation_token".format(cls.__name__))


class NoPolling(PollingMethod):
    """An empty poller that returns the deserialized initial response."""

    def __init__(self):
        self._initial_response = None
        self._deserialization_callback = None

    def initialize(self, _: Any, initial_response: Any, deserialization_callback: Callable) -> None:
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback

    def run(self) -> None:
        """Empty run, no polling."""

    def status(self) -> str:
        """Return the current status as a string.

        :rtype: str
        """
        return "succeeded"

    def finished(self) -> bool:
        """Is this polling finished?

        :rtype: bool
        """
        return True

    def resource(self) -> Any:
        return self._deserialization_callback(self._initial_response)

    def get_continuation_token(self) -> str:
        import pickle

        return base64.b64encode(pickle.dumps(self._initial_response)).decode("ascii")

    @classmethod
    def from_continuation_token(cls, continuation_token: str, **kwargs) -> Tuple[Any, Any, Callable]:
        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token")
        import pickle

        initial_response = pickle.loads(base64.b64decode(continuation_token))  # nosec
        return None, initial_response, deserialization_callback


class LROPoller(Generic[PollingReturnType]):
    """Poller for long running operations.

    :param client: A pipeline service client
    :type client: ~azure.core.PipelineClient
    :param initial_response: The initial call response
    :type initial_response: ~azure.core.pipeline.PipelineResponse
    :param deserialization_callback: A callback that takes a Response and return a deserialized object.
                                     If a subclass of Model is given, this passes "deserialize" as callback.
    :type deserialization_callback: callable or msrest.serialization.Model
    :param polling_method: The polling strategy to adopt
    :type polling_method: ~azure.core.polling.PollingMethod
    """

    def __init__(
        self,
        client: Any,
        initial_response: Any,
        deserialization_callback: Callable,
        polling_method: PollingMethod[PollingReturnType],
    ) -> None:
        self._callbacks: List[Callable] = []
        self._polling_method = polling_method

        # This implicit test avoids bringing in an explicit dependency on Model directly
        try:
            deserialization_callback = deserialization_callback.deserialize  # type: ignore
        except AttributeError:
            pass

        # Might raise a CloudError
        self._polling_method.initialize(client, initial_response, deserialization_callback)

        # Prepare thread execution
        self._thread = None
        self._done = None
        self._exception = None
        if not self._polling_method.finished():
            self._done = threading.Event()
            self._thread = threading.Thread(
                target=with_current_context(self._start),
                name="LROPoller({})".format(uuid.uuid4()),
            )
            self._thread.daemon = True
            self._thread.start()

    def _start(self):
        """Start the long running operation.
        On completion, runs any callbacks.

        :param callable update_cmd: The API request to check the status of
         the operation.
        """
        try:
            self._polling_method.run()
        except AzureError as error:
            if not error.continuation_token:
                try:
                    error.continuation_token = self.continuation_token()
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.warning("Unable to retrieve continuation token: %s", err)
                    error.continuation_token = None

            self._exception = error
        except Exception as error:  # pylint: disable=broad-except
            self._exception = error

        finally:
            self._done.set()

        callbacks, self._callbacks = self._callbacks, []
        while callbacks:
            for call in callbacks:
                call(self._polling_method)
            callbacks, self._callbacks = self._callbacks, []

    def polling_method(self) -> PollingMethod[PollingReturnType]:
        """Return the polling method associated to this poller."""
        return self._polling_method

    def continuation_token(self) -> str:
        """Return a continuation token that allows to restart the poller later.

        :returns: An opaque continuation token
        :rtype: str
        """
        return self._polling_method.get_continuation_token()

    @classmethod
    def from_continuation_token(
        cls, polling_method: PollingMethod[PollingReturnType], continuation_token: str, **kwargs
    ) -> "LROPoller[PollingReturnType]":
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)
        return cls(client, initial_response, deserialization_callback, polling_method)

    def status(self) -> str:
        """Returns the current status string.

        :returns: The current status string
        :rtype: str
        """
        return self._polling_method.status()

    def result(self, timeout: Optional[float] = None) -> PollingReturnType:
        """Return the result of the long running operation, or
        the result available after the specified timeout.

        :returns: The deserialized resource of the long running operation,
         if one is available.
        :raises ~azure.core.exceptions.HttpResponseError: Server problem with the query.
        """
        self.wait(timeout)
        return self._polling_method.resource()

    @distributed_trace
    def wait(self, timeout: Optional[float] = None) -> None:
        """Wait on the long running operation for a specified length
        of time. You can check if this call as ended with timeout with the
        "done()" method.

        :param float timeout: Period of time to wait for the long running
         operation to complete (in seconds).
        :raises ~azure.core.exceptions.HttpResponseError: Server problem with the query.
        """
        if self._thread is None:
            return
        self._thread.join(timeout=timeout)
        try:
            # Let's handle possible None in forgiveness here
            # https://github.com/python/mypy/issues/8165
            raise self._exception  # type: ignore
        except TypeError:  # Was None
            pass

    def done(self) -> bool:
        """Check status of the long running operation.

        :returns: 'True' if the process has completed, else 'False'.
        :rtype: bool
        """
        return self._thread is None or not self._thread.is_alive()

    def add_done_callback(self, func: Callable) -> None:
        """Add callback function to be run once the long running operation
        has completed - regardless of the status of the operation.

        :param callable func: Callback function that takes at least one
         argument, a completed LongRunningOperation.
        """
        # Still use "_done" and not "done", since CBs are executed inside the thread.
        if self._done is None or self._done.is_set():
            func(self._polling_method)
        # Let's add them still, for consistency (if you wish to access to it for some reasons)
        self._callbacks.append(func)

    def remove_done_callback(self, func: Callable) -> None:
        """Remove a callback from the long running operation.

        :param callable func: The function to be removed from the callbacks.
        :raises ValueError: if the long running operation has already completed.
        """
        if self._done is None or self._done.is_set():
            raise ValueError("Process is complete.")
        self._callbacks = [c for c in self._callbacks if c != func]
