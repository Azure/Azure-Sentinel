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
import asyncio
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Callable, Optional, AsyncIterator as AsyncIteratorType

from oauthlib import oauth2
import requests
from requests.models import CONTENT_CHUNK_SIZE

from ..exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback
)
from ..universal_http.async_requests import AsyncBasicRequestsHTTPSender
from . import AsyncHTTPSender, AsyncHTTPPolicy, Response, Request
from .requests import RequestsContext


_LOGGER = logging.getLogger(__name__)


class AsyncPipelineRequestsHTTPSender(AsyncHTTPSender):
    """Implements a basic Pipeline, that supports universal HTTP lib "requests" driver.
    """

    def __init__(self, universal_http_requests_driver: Optional[AsyncBasicRequestsHTTPSender]=None) -> None:
        self.driver = universal_http_requests_driver or AsyncBasicRequestsHTTPSender()

    async def __aenter__(self) -> 'AsyncPipelineRequestsHTTPSender':
        await self.driver.__aenter__()
        return self

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        await self.driver.__aexit__(*exc_details)

    async def close(self):
        await self.__aexit__()

    def build_context(self):
        # type: () -> RequestsContext
        return RequestsContext(
            session=self.driver.session,
        )

    async def send(self, request: Request, **kwargs) -> Response:
        """Send request object according to configuration.

        :param Request request: The request object to be sent.
        """
        if request.context is None:  # Should not happen, but make mypy happy and does not hurt
            request.context = self.build_context()

        if request.context.session is not self.driver.session:
            kwargs['session'] = request.context.session

        return Response(
            request,
            await self.driver.send(request.http_request, **kwargs)
        )


class AsyncRequestsCredentialsPolicy(AsyncHTTPPolicy):
    """Implementation of request-oauthlib except and retry logic.
    """
    def __init__(self, credentials):
        super(AsyncRequestsCredentialsPolicy, self).__init__()
        self._creds = credentials

    async def send(self, request, **kwargs):
        session = request.context.session
        try:
            self._creds.signed_session(session)
        except TypeError: # Credentials does not support session injection
            _LOGGER.warning("Your credentials class does not support session injection. Performance will not be at the maximum.")
            request.context.session = session = self._creds.signed_session()

        try:
            try:
                return await self.next.send(request, **kwargs)
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

                return await self.next.send(request, **kwargs)
            except (oauth2.rfc6749.errors.InvalidGrantError,
                    oauth2.rfc6749.errors.TokenExpiredError) as err:
                msg = "Token expired or is invalid."
                raise_with_traceback(TokenExpiredError, msg, err)

        except (requests.RequestException,
                oauth2.rfc6749.errors.OAuth2Error) as err:
            msg = "Error occurred in request."
            raise_with_traceback(ClientRequestError, msg, err)

