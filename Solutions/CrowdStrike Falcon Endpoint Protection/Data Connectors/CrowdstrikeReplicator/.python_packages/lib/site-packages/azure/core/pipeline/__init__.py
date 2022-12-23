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
from typing import TypeVar, Generic

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

try:
    from contextlib import (  # pylint: disable=unused-import
        AbstractContextManager,
    )
except ImportError:  # Python <= 3.5

    class AbstractContextManager(object):  # type: ignore
        def __enter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None


class PipelineContext(dict):
    """A context object carried by the pipeline request and response containers.

    This is transport specific and can contain data persisted between
    pipeline requests (for example reusing an open connection pool or "session"),
    as well as used by the SDK developer to carry arbitrary data through
    the pipeline.

    :param transport: The HTTP transport type.
    :param kwargs: Developer-defined keyword arguments.
    """
    _PICKLE_CONTEXT = {
        'deserialized_data'
    }

    def __init__(self, transport, **kwargs):  # pylint: disable=super-init-not-called
        self.transport = transport
        self.options = kwargs
        self._protected = ["transport", "options"]

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['transport']
        return state

    def __reduce__(self):
        reduced = super(PipelineContext, self).__reduce__()
        saved_context = {}
        for key, value in self.items():
            if key in self._PICKLE_CONTEXT:
                saved_context[key] = value
        # 1 is for from __reduce__ spec of pickle (generic args for recreation)
        # 2 is how dict is implementing __reduce__ (dict specific)
        # tuple are read-only, we use a list in the meantime
        reduced = list(reduced)
        dict_reduced_result = list(reduced[1])
        dict_reduced_result[2] = saved_context
        reduced[1] = tuple(dict_reduced_result)
        return tuple(reduced)

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Re-create the unpickable entries
        self.transport = None

    def __setitem__(self, key, item):
        # If reloaded from pickle, _protected might not be here until restored by pickle
        # this explains the hasattr test
        if hasattr(self, '_protected') and key in self._protected:
            raise ValueError("Context value {} cannot be overwritten.".format(key))
        return super(PipelineContext, self).__setitem__(key, item)

    def __delitem__(self, key):
        if key in self._protected:
            raise ValueError("Context value {} cannot be deleted.".format(key))
        return super(PipelineContext, self).__delitem__(key)

    def clear(self):
        """Context objects cannot be cleared.

        :raises: TypeError
        """
        raise TypeError("Context objects cannot be cleared.")

    def update(self, *args, **kwargs):
        """Context objects cannot be updated.

        :raises: TypeError
        """
        raise TypeError("Context objects cannot be updated.")

    def pop(self, *args):
        """Removes specified key and returns the value.
        """
        if args and args[0] in self._protected:
            raise ValueError("Context value {} cannot be popped.".format(args[0]))
        return super(PipelineContext, self).pop(*args)


class PipelineRequest(Generic[HTTPRequestType]):
    """A pipeline request object.

    Container for moving the HttpRequest through the pipeline.
    Universal for all transports, both synchronous and asynchronous.

    :param http_request: The request object.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param context: Contains the context - data persisted between pipeline requests.
    :type context: ~azure.core.pipeline.PipelineContext
    """

    def __init__(self, http_request, context):
        # type: (HTTPRequestType, PipelineContext) -> None
        self.http_request = http_request
        self.context = context


class PipelineResponse(Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline response object.

    The PipelineResponse interface exposes an HTTP response object as it returns through the pipeline of Policy objects.
    This ensures that Policy objects have access to the HTTP response.

    This also has a "context" object where policy can put additional fields.
    Policy SHOULD update the "context" with additional post-processed field if they create them.
    However, nothing prevents a policy to actually sub-class this class a return it instead of the initial instance.

    :param http_request: The request object.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param http_response: The response object.
    :type http_response: ~azure.core.pipeline.transport.HttpResponse
    :param context: Contains the context - data persisted between pipeline requests.
    :type context: ~azure.core.pipeline.PipelineContext
    """

    def __init__(self, http_request, http_response, context):
        # type: (HTTPRequestType, HTTPResponseType, PipelineContext) -> None
        self.http_request = http_request
        self.http_response = http_response
        self.context = context


from ._base import Pipeline  # pylint: disable=wrong-import-position

__all__ = ["Pipeline", "PipelineRequest", "PipelineResponse", "PipelineContext"]

try:
    from ._base_async import AsyncPipeline  # pylint: disable=unused-import

    __all__.append("AsyncPipeline")
except (SyntaxError, ImportError):
    pass  # Asynchronous pipelines not supported.
