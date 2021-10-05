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

from oauthlib import oauth2
import requests
from requests.models import CONTENT_CHUNK_SIZE

from urllib3 import Retry  # Needs requests 2.16 at least to be safe

from ..exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback
)
from ..universal_http import ClientRequest
from ..universal_http.requests import BasicRequestsHTTPSender
from . import HTTPSender, HTTPPolicy, Response, Request


_LOGGER = logging.getLogger(__name__)


class RequestsCredentialsPolicy(HTTPPolicy):
    """Implementation of request-oauthlib except and retry logic.
    """
    def __init__(self, credentials):
        super(RequestsCredentialsPolicy, self).__init__()
        self._creds = credentials

    def send(self, request, **kwargs):
        session = request.context.session
        try:
            self._creds.signed_session(session)
        except TypeError: # Credentials does not support session injection
            _LOGGER.warning("Your credentials class does not support session injection. Performance will not be at the maximum.")
            request.context.session = session = self._creds.signed_session()

        try:
            try:
                return self.next.send(request, **kwargs)
            except (oauth2.rfc6749.errors.InvalidGrantError,
                    oauth2.rfc6749.errors.TokenExpiredError) as err:
                error = "Token expired or is invalid. Attempting to refresh."
                _LOGGER.warning(error)

            try:
                try:
                    self._creds.refresh_session(session)
                except TypeError: # Credentials does not support session injection
                    _LOGGER.warning("Your credentials class does not support session injection. Performance will not be at the maximum.")
                    request.context.session = session = self._creds.refresh_session()

                return self.next.send(request, **kwargs)
            except (oauth2.rfc6749.errors.InvalidGrantError,
                    oauth2.rfc6749.errors.TokenExpiredError) as err:
                msg = "Token expired or is invalid."
                raise_with_traceback(TokenExpiredError, msg, err)

        except (requests.RequestException,
                oauth2.rfc6749.errors.OAuth2Error) as err:
            msg = "Error occurred in request."
            raise_with_traceback(ClientRequestError, msg, err)

class RequestsPatchSession(HTTPPolicy):
    """Implements request level configuration
    that are actually to be done at the session level.

    This is highly deprecated, and is totally legacy.
    The pipeline structure allows way better design for this.
    """
    _protocols = ['http://', 'https://']

    def send(self, request, **kwargs):
        """Patch the current session with Request level operation config.

        This is deprecated, we shouldn't patch the session with
        arguments at the Request, and "config" should be used.
        """
        session = request.context.session

        old_max_redirects = None
        if 'max_redirects' in kwargs:
            warnings.warn("max_redirects in operation kwargs is deprecated, use config.redirect_policy instead",
                          DeprecationWarning)
            old_max_redirects = session.max_redirects
            session.max_redirects = int(kwargs['max_redirects'])

        old_trust_env = None
        if 'use_env_proxies' in kwargs:
            warnings.warn("use_env_proxies in operation kwargs is deprecated, use config.proxies instead",
                          DeprecationWarning)
            old_trust_env = session.trust_env
            session.trust_env = bool(kwargs['use_env_proxies'])

        old_retries = {}
        if 'retries' in kwargs:
            warnings.warn("retries in operation kwargs is deprecated, use config.retry_policy instead",
                          DeprecationWarning)
            max_retries = kwargs['retries']
            for protocol in self._protocols:
                old_retries[protocol] = session.adapters[protocol].max_retries
                session.adapters[protocol].max_retries = max_retries

        try:
            return self.next.send(request, **kwargs)
        finally:
            if old_max_redirects:
                session.max_redirects = old_max_redirects

            if old_trust_env:
                session.trust_env = old_trust_env

            if old_retries:
                for protocol in self._protocols:
                    session.adapters[protocol].max_retries = old_retries[protocol]

class RequestsContext(object):
    def __init__(self, session):
        self.session = session


class PipelineRequestsHTTPSender(HTTPSender):
    """Implements a basic Pipeline, that supports universal HTTP lib "requests" driver.
    """

    def __init__(self, universal_http_requests_driver=None):
        # type: (Optional[BasicRequestsHTTPSender]) -> None
        self.driver = universal_http_requests_driver or BasicRequestsHTTPSender()

    def __enter__(self):
        # type: () -> PipelineRequestsHTTPSender
        self.driver.__enter__()
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self.driver.__exit__(*exc_details)

    def close(self):
        self.__exit__()

    def build_context(self):
        # type: () -> RequestsContext
        return RequestsContext(
            session=self.driver.session,
        )

    def send(self, request, **kwargs):
        # type: (Request[ClientRequest], Any) -> Response
        """Send request object according to configuration.

        :param Request request: The request object to be sent.
        """
        if request.context is None:  # Should not happen, but make mypy happy and does not hurt
            request.context = self.build_context()

        if request.context.session is not self.driver.session:
            kwargs['session'] = request.context.session

        return Response(
            request,
            self.driver.send(request.http_request, **kwargs)
        )
