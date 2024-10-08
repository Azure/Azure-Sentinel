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
"""
This module is the requests implementation of Pipeline ABC
"""
from __future__ import absolute_import  # we have a "requests" module that conflicts with "requests" on Py2.7
import contextlib
import logging
import threading
from typing import TYPE_CHECKING, List, Callable, Iterator, Any, Union, Dict, Optional  # pylint: disable=unused-import
import warnings

try:
    from configparser import NoOptionError
except ImportError:
    from ConfigParser import NoOptionError  # type: ignore

from oauthlib import oauth2
import requests
from requests.models import CONTENT_CHUNK_SIZE

from urllib3 import Retry  # Needs requests 2.16 at least to be safe

from ..exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback)
from . import HTTPSender, HTTPClientResponse, ClientResponse, HTTPSenderConfiguration

if TYPE_CHECKING:
    from . import ClientRequest  # pylint: disable=unused-import


_LOGGER = logging.getLogger(__name__)



class HTTPRequestsClientResponse(HTTPClientResponse):
    def __init__(self, request, requests_response):
        super(HTTPRequestsClientResponse, self).__init__(request, requests_response)
        self.status_code = requests_response.status_code
        self.headers = requests_response.headers
        self.reason = requests_response.reason

    def body(self):
        return self.internal_response.content

    def text(self, encoding=None):
        if encoding:
            self.internal_response.encoding = encoding
        return self.internal_response.text

    def raise_for_status(self):
        self.internal_response.raise_for_status()

class RequestsClientResponse(HTTPRequestsClientResponse, ClientResponse):

    def stream_download(self, chunk_size=None, callback=None):
        # type: (Optional[int], Optional[Callable]) -> Iterator[bytes]
        """Generator for streaming request body data.

        :param callback: Custom callback for monitoring progress.
        :param int chunk_size:
        """
        chunk_size = chunk_size or CONTENT_CHUNK_SIZE
        with contextlib.closing(self.internal_response) as response:
            # https://github.com/PyCQA/pylint/issues/1437
            for chunk in response.iter_content(chunk_size):  # pylint: disable=no-member
                if not chunk:
                    break
                if callback and callable(callback):
                    callback(chunk, response=response)
                yield chunk


class BasicRequestsHTTPSender(HTTPSender):
    """Implements a basic requests HTTP sender.

    Since requests team recommends to use one session per requests, you should
    not consider this class as thread-safe, since it will use one Session
    per instance.

    In this simple implementation:
    - You provide the configured session if you want to, or a basic session is created.
    - All kwargs received by "send" are sent to session.request directly
    """

    def __init__(self, session=None):
        # type: (Optional[requests.Session]) -> None
        self.session = session or requests.Session()

    def __enter__(self):
        # type: () -> BasicRequestsHTTPSender
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self.close()

    def close(self):
        self.session.close()

    def send(self, request, **kwargs):
        # type: (ClientRequest, Any) -> ClientResponse
        """Send request object according to configuration.

        Allowed kwargs are:
        - session : will override the driver session and use yours. Should NOT be done unless really required.
        - anything else is sent straight to requests.

        :param ClientRequest request: The request object to be sent.
        """
        # It's not recommended to provide its own session, and is mostly
        # to enable some legacy code to plug correctly
        session = kwargs.pop('session', self.session)
        try:
            response = session.request(
                request.method,
                request.url,
                **kwargs)
        except requests.RequestException as err:
            msg = "Error occurred in request."
            raise_with_traceback(ClientRequestError, msg, err)

        return RequestsClientResponse(request, response)


def _patch_redirect(session):
    # type: (requests.Session) -> None
    """Whether redirect policy should be applied based on status code.

    HTTP spec says that on 301/302 not HEAD/GET, should NOT redirect.
    But requests does, to follow browser more than spec
    https://github.com/requests/requests/blob/f6e13ccfc4b50dc458ee374e5dba347205b9a2da/requests/sessions.py#L305-L314

    This patches "requests" to be more HTTP compliant.

    Note that this is super dangerous, since technically this is not public API.
    """
    def enforce_http_spec(resp, request):
        if resp.status_code in (301, 302) and \
                request.method not in ['GET', 'HEAD']:
            return False
        return True

    redirect_logic = session.resolve_redirects

    def wrapped_redirect(resp, req, **kwargs):
        attempt = enforce_http_spec(resp, req)
        return redirect_logic(resp, req, **kwargs) if attempt else []
    wrapped_redirect.is_msrest_patched = True  # type: ignore

    session.resolve_redirects = wrapped_redirect  # type: ignore

class RequestsHTTPSender(BasicRequestsHTTPSender):
    """A requests HTTP sender that can consume a msrest.Configuration object.

    This instance will consume the following configuration attributes:
    - connection
    - proxies
    - retry_policy
    - redirect_policy
    - enable_http_logger
    - hooks
    - session_configuration_callback
    """

    _protocols = ['http://', 'https://']

    # Set of authorized kwargs at the operation level
    _REQUESTS_KWARGS = [
        'cookies',
        'verify',
        'timeout',
        'allow_redirects',
        'proxies',
        'verify',
        'cert'
    ]

    def __init__(self, config=None):
        # type: (Optional[RequestHTTPSenderConfiguration]) -> None
        self._session_mapping = threading.local()
        self.config = config or RequestHTTPSenderConfiguration()
        super(RequestsHTTPSender, self).__init__()

    @property  # type: ignore
    def session(self):
        try:
            return self._session_mapping.session
        except AttributeError:
            self._session_mapping.session = requests.Session()
            self._init_session(self._session_mapping.session)
            return self._session_mapping.session

    @session.setter
    def session(self, value):
        self._init_session(value)
        self._session_mapping.session = value

    def _init_session(self, session):
        # type: (requests.Session) -> None
        """Init session level configuration of requests.

        This is initialization I want to do once only on a session.
        """
        _patch_redirect(session)

        # Change max_retries in current all installed adapters
        max_retries = self.config.retry_policy()
        for protocol in self._protocols:
            session.adapters[protocol].max_retries = max_retries

    def _configure_send(self, request, **kwargs):
        # type: (ClientRequest, Any) -> Dict[str, str]
        """Configure the kwargs to use with requests.

        See "send" for kwargs details.

        :param ClientRequest request: The request object to be sent.
        :returns: The requests.Session.request kwargs
        :rtype: dict[str,str]
        """
        requests_kwargs = {}  # type: Any
        session = kwargs.pop('session', self.session)

        # If custom session was not create here
        if session is not self.session:
            self._init_session(session)

        session.max_redirects = int(self.config.redirect_policy())
        session.trust_env = bool(self.config.proxies.use_env_settings)

        # Initialize requests_kwargs with "config" value
        requests_kwargs.update(self.config.connection())
        requests_kwargs['allow_redirects'] = bool(self.config.redirect_policy)
        requests_kwargs['headers'] = self.config.headers.copy()

        proxies = self.config.proxies()
        if proxies:
            requests_kwargs['proxies'] = proxies

        # Replace by operation level kwargs
        # We allow some of them, since some like stream or json are controlled by msrest
        for key in kwargs:
            if key in self._REQUESTS_KWARGS:
                requests_kwargs[key] = kwargs[key]

        # Hooks. Deprecated, should be a policy
        def make_user_hook_cb(user_hook, session):
            def user_hook_cb(r, *args, **kwargs):
                kwargs.setdefault("msrest", {})['session'] = session
                return user_hook(r, *args, **kwargs)
            return user_hook_cb

        hooks = []
        for user_hook in self.config.hooks:
            hooks.append(make_user_hook_cb(user_hook, self.session))

        if hooks:
            requests_kwargs['hooks'] = {'response': hooks}

        # Configuration callback. Deprecated, should be a policy
        output_kwargs = self.config.session_configuration_callback(
            session,
            self.config,
            kwargs,
            **requests_kwargs
        )
        if output_kwargs is not None:
            requests_kwargs = output_kwargs

        # If custom session was not create here
        if session is not self.session:
            requests_kwargs['session'] = session

        ### Autorest forced kwargs now ###

        # If Autorest needs this response to be streamable. True for compat.
        requests_kwargs['stream'] = kwargs.get('stream', True)

        if request.files:
            requests_kwargs['files'] = request.files
        elif request.data:
            requests_kwargs['data'] = request.data
        requests_kwargs['headers'].update(request.headers)

        return requests_kwargs

    def send(self, request, **kwargs):
        # type: (ClientRequest, Any) -> ClientResponse
        """Send request object according to configuration.

        Available kwargs:
        - session : will override the driver session and use yours. Should NOT be done unless really required.
        - A subset of what requests.Session.request can receive:

            - cookies
            - verify
            - timeout
            - allow_redirects
            - proxies
            - verify
            - cert

        Everything else will be silently ignored.

        :param ClientRequest request: The request object to be sent.
        """
        requests_kwargs = self._configure_send(request, **kwargs)
        return super(RequestsHTTPSender, self).send(request, **requests_kwargs)


class ClientRetryPolicy(object):
    """Retry configuration settings.
    Container for retry policy object.
    """

    safe_codes = [i for i in range(500) if i != 408] + [501, 505]

    def __init__(self):
        self.policy = Retry()
        self.policy.total = 3
        self.policy.connect = 3
        self.policy.read = 3
        self.policy.backoff_factor = 0.8
        self.policy.BACKOFF_MAX = 90

        retry_codes = [i for i in range(999) if i not in self.safe_codes]
        self.policy.status_forcelist = retry_codes
        self.policy.method_whitelist = ['HEAD', 'TRACE', 'GET', 'PUT',
                                        'OPTIONS', 'DELETE', 'POST', 'PATCH']

    def __call__(self):
        # type: () -> Retry
        """Return configuration to be applied to connection."""
        debug = ("Configuring retry: max_retries=%r, "
                 "backoff_factor=%r, max_backoff=%r")
        _LOGGER.debug(
            debug, self.retries, self.backoff_factor, self.max_backoff)
        return self.policy

    @property
    def retries(self):
        # type: () -> int
        """Total number of allowed retries."""
        return self.policy.total

    @retries.setter
    def retries(self, value):
        # type: (int) -> None
        self.policy.total = value
        self.policy.connect = value
        self.policy.read = value

    @property
    def backoff_factor(self):
        # type: () -> Union[int, float]
        """Factor by which back-off delay is incrementally increased."""
        return self.policy.backoff_factor

    @backoff_factor.setter
    def backoff_factor(self, value):
        # type: (Union[int, float]) -> None
        self.policy.backoff_factor = value

    @property
    def max_backoff(self):
        # type: () -> int
        """Max retry back-off delay."""
        return self.policy.BACKOFF_MAX

    @max_backoff.setter
    def max_backoff(self, value):
        # type: (int) -> None
        self.policy.BACKOFF_MAX = value

def default_session_configuration_callback(session, global_config, local_config, **kwargs):  # pylint: disable=unused-argument
    # type: (requests.Session, RequestHTTPSenderConfiguration, Dict[str,str], str) -> Dict[str, str]
    """Configuration callback if you need to change default session configuration.

    :param requests.Session session: The session.
    :param Configuration global_config: The global configuration.
    :param dict[str,str] local_config: The on-the-fly configuration passed on the call.
    :param dict[str,str] kwargs: The current computed values for session.request method.
    :return: Must return kwargs, to be passed to session.request. If None is return, initial kwargs will be used.
    :rtype: dict[str,str]
    """
    return kwargs

class RequestHTTPSenderConfiguration(HTTPSenderConfiguration):
    """Requests specific HTTP sender configuration.

    :param str filepath: Path to existing config file (optional).
    """

    def __init__(self, filepath=None):
        # type: (Optional[str]) -> None

        super(RequestHTTPSenderConfiguration, self).__init__()

        # Retry configuration
        self.retry_policy = ClientRetryPolicy()

        # Requests hooks. Must respect requests hook callback signature
        # Note that we will inject the following parameters:
        # - kwargs['msrest']['session'] with the current session
        self.hooks = []  # type: List[Callable[[requests.Response, str, str], None]]

        self.session_configuration_callback = default_session_configuration_callback

        if filepath:
            self.load(filepath)

    def save(self, filepath):
        """Save current configuration to file.

        :param str filepath: Path to file where settings will be saved.
        :raises: ValueError if supplied filepath cannot be written to.
        """
        self._config.add_section("RetryPolicy")
        self._config.set("RetryPolicy", "retries", str(self.retry_policy.retries))
        self._config.set("RetryPolicy", "backoff_factor",
                         str(self.retry_policy.backoff_factor))
        self._config.set("RetryPolicy", "max_backoff",
                         str(self.retry_policy.max_backoff))
        super(RequestHTTPSenderConfiguration, self).save(filepath)

    def load(self, filepath):
        try:
            self.retry_policy.retries = \
                self._config.getint("RetryPolicy", "retries")
            self.retry_policy.backoff_factor = \
                self._config.getfloat("RetryPolicy", "backoff_factor")
            self.retry_policy.max_backoff = \
                self._config.getint("RetryPolicy", "max_backoff")
        except (ValueError, EnvironmentError, NoOptionError):
            error = "Supplied config file incompatible."
            raise_with_traceback(ValueError, error)
        finally:
            self._clear_config()
        super(RequestHTTPSenderConfiguration, self).load(filepath)
