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
from __future__ import absolute_import  # we have a "requests" module that conflicts with "requests" on Py2.7
import abc
try:
    import configparser
    from configparser import NoOptionError
except ImportError:
    import ConfigParser as configparser  # type: ignore
    from ConfigParser import NoOptionError  # type: ignore
import json
import logging
import os.path
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from typing import TYPE_CHECKING, Generic, TypeVar, cast, IO, List, Union, Any, Mapping, Dict, Optional, Tuple, Callable, Iterator  # pylint: disable=unused-import

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

# This file is NOT using any "requests" HTTP implementation
# However, the CaseInsensitiveDict is handy.
# If one day we reach the point where "requests" can be skip totally,
# might provide our own implementation
from requests.structures import CaseInsensitiveDict


_LOGGER = logging.getLogger(__name__)

try:
    ABC = abc.ABC
except AttributeError: # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})  # type: ignore

try:
    from contextlib import AbstractContextManager  # type: ignore
except ImportError: # Python <= 3.5
    class AbstractContextManager(object):  # type: ignore
        def __enter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None

class HTTPPolicy(ABC, Generic[HTTPRequestType, HTTPResponseType]):
    """An http policy ABC.
    """
    def __init__(self):
        self.next = None

    @abc.abstractmethod
    def send(self, request, **kwargs):
        # type: (Request[HTTPRequestType], Any) -> Response[HTTPRequestType, HTTPResponseType]
        """Mutate the request.

        Context content is dependent of the HTTPSender.
        """
        pass

class SansIOHTTPPolicy(Generic[HTTPRequestType, HTTPResponseType]):
    """Represents a sans I/O policy.

    This policy can act before the I/O, and after the I/O.
    Use this policy if the actual I/O in the middle is an implementation
    detail.

    Context is not available, since it's implementation dependent.
    if a policy needs a context of the Sender, it can't be universal.

    Example: setting a UserAgent does not need to be tight to
    sync or async implementation or specific HTTP lib
    """
    def on_request(self, request, **kwargs):
        # type: (Request[HTTPRequestType], Any) -> None
        """Is executed before sending the request to next policy.
        """
        pass

    def on_response(self, request, response, **kwargs):
        # type: (Request[HTTPRequestType], Response[HTTPRequestType, HTTPResponseType], Any) -> None
        """Is executed after the request comes back from the policy.
        """
        pass

    def on_exception(self, request, **kwargs):
        # type: (Request[HTTPRequestType], Any) -> bool
        """Is executed if an exception comes back from the following
        policy.

        Return True if the exception has been handled and should not
        be forwarded to the caller.

        This method is executed inside the exception handler.
        To get the exception, raise and catch it:

            try:
                raise
            except MyError:
                do_something()

        or use

            exc_type, exc_value, exc_traceback = sys.exc_info()
        """
        return False

class _SansIOHTTPPolicyRunner(HTTPPolicy, Generic[HTTPRequestType, HTTPResponseType]):
    """Sync implementation of the SansIO policy.
    """

    def __init__(self, policy):
        # type: (SansIOHTTPPolicy) -> None
        super(_SansIOHTTPPolicyRunner, self).__init__()
        self._policy = policy

    def send(self, request, **kwargs):
        # type: (Request[HTTPRequestType], Any) -> Response[HTTPRequestType, HTTPResponseType]
        self._policy.on_request(request, **kwargs)
        try:
            response = self.next.send(request, **kwargs)
        except Exception:
            if not self._policy.on_exception(request, **kwargs):
                raise
        else:
            self._policy.on_response(request, response, **kwargs)
        return response

class Pipeline(AbstractContextManager, Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender.
    """

    def __init__(self, policies=None, sender=None):
        # type: (List[Union[HTTPPolicy, SansIOHTTPPolicy]], HTTPSender) -> None
        self._impl_policies = []  # type: List[HTTPPolicy]
        if not sender:
            # Import default only if nothing is provided
            from .requests import PipelineRequestsHTTPSender
            self._sender = cast(HTTPSender, PipelineRequestsHTTPSender())
        else:
            self._sender = sender
        for policy in (policies or []):
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOHTTPPolicyRunner(policy))
            else:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies)-1):
            self._impl_policies[index].next = self._impl_policies[index+1]
        if self._impl_policies:
            self._impl_policies[-1].next = self._sender

    def __enter__(self):
        # type: () -> Pipeline
        self._sender.__enter__()
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self._sender.__exit__(*exc_details)

    def run(self, request, **kwargs):
        # type: (HTTPRequestType, Any) -> Response
        context = self._sender.build_context()
        pipeline_request = Request(request, context)  # type: Request[HTTPRequestType]
        first_node = self._impl_policies[0] if self._impl_policies else self._sender
        return first_node.send(pipeline_request, **kwargs)  # type: ignore

class HTTPSender(AbstractContextManager, ABC, Generic[HTTPRequestType, HTTPResponseType]):
    """An http sender ABC.
    """

    @abc.abstractmethod
    def send(self, request, **config):
        # type: (Request[HTTPRequestType], Any) -> Response[HTTPRequestType, HTTPResponseType]
        """Send the request using this HTTP sender.
        """
        pass

    def build_context(self):
        # type: () -> Any
        """Allow the sender to build a context that will be passed
        across the pipeline with the request.

        Return type has no constraints. Implementation is not
        required and None by default.
        """
        return None


class Request(Generic[HTTPRequestType]):
    """Represents a HTTP request in a Pipeline.

    URL can be given without query parameters, to be added later using "format_parameters".

    Instance can be created without data, to be added later using "add_content"

    Instance can be created without files, to be added later using "add_formdata"

    :param str method: HTTP method (GET, HEAD, etc.)
    :param str url: At least complete scheme/host/path
    :param dict[str,str] headers: HTTP headers
    :param files: Files list.
    :param data: Body to be sent.
    :type data: bytes or str.
    """
    def __init__(self, http_request, context=None):
        # type: (HTTPRequestType, Optional[Any]) -> None
        self.http_request = http_request
        self.context = context


class Response(Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline response object.

    The Response interface exposes an HTTP response object as it returns through the pipeline of Policy objects.
    This ensures that Policy objects have access to the HTTP response.

    This also have a "context" dictionary where policy can put additional fields.
    Policy SHOULD update the "context" dictionary with additional post-processed field if they create them.
    However, nothing prevents a policy to actually sub-class this class a return it instead of the initial instance.
    """
    def __init__(self, request, http_response, context=None):
        # type: (Request[HTTPRequestType], HTTPResponseType, Optional[Dict[str, Any]]) -> None
        self.request = request
        self.http_response = http_response
        self.context = context or {}


# ClientRawResponse is in Pipeline for compat, but technically there is nothing Pipeline here, this is deserialization

if TYPE_CHECKING:
    from ..universal_http import ClientResponse

class ClientRawResponse(object):
    """Wrapper for response object.
    This allows for additional data to be gathereded from the response,
    for example deserialized headers.
    It also allows the raw response object to be passed back to the user.

    :param output: Deserialized response object. This is the type that would have been returned
     directly by the main operation without raw=True.
    :param response: Raw response object (by default requests.Response instance)
    :type response: ~requests.Response
    """

    def __init__(self, output, response):
        # type: (Union[Any], Optional[Union[Response, ClientResponse]]) -> None
        from ..serialization import Deserializer

        if isinstance(response, Response):
            # If pipeline response, remove that layer
            response = response.http_response

        try:
            # If universal driver, remove that layer
            self.response = response.internal_response  # type: ignore
        except AttributeError:
            self.response = response

        self.output = output
        self.headers = {}  # type: Dict[str, Optional[Any]]
        self._deserialize = Deserializer()

    def add_headers(self, header_dict):
        # type: (Dict[str, str]) -> None
        """Deserialize a specific header.

        :param dict header_dict: A dictionary containing the name of the
         header and the type to deserialize to.
        """
        if not self.response:
            return
        for name, data_type in header_dict.items():
            value = self.response.headers.get(name)
            value = self._deserialize(data_type, value)
            self.headers[name] = value



__all__ = [
    'Request',
    'Response',
    'Pipeline',
    'HTTPPolicy',
    'SansIOHTTPPolicy',
    'HTTPSender',
    # backward compat
    'ClientRawResponse',
]

try:
    from .async_abc import AsyncPipeline, AsyncHTTPPolicy, AsyncHTTPSender  # pylint: disable=unused-import
    from .async_abc import __all__ as _async_all
    __all__ += _async_all
except SyntaxError: # Python 2
    pass
except ImportError: # pyinstaller won't include Py3 files in Py2.7 mode
    pass
