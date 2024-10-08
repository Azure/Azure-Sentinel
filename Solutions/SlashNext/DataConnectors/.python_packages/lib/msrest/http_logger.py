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

import logging
import re
import types

from typing import Any, Optional, TYPE_CHECKING  # pylint: disable=unused-import

if TYPE_CHECKING:
    from .universal_http import ClientRequest, ClientResponse  # pylint: disable=unused-import

_LOGGER = logging.getLogger(__name__)


def log_request(_, request, *_args, **_kwargs):
    # type: (Any, ClientRequest, str, str) -> None
    """Log a client request.

    :param _: Unused in current version (will be None)
    :param requests.Request request: The request object.
    """
    if not _LOGGER.isEnabledFor(logging.DEBUG):
        return

    try:
        _LOGGER.debug("Request URL: %r", request.url)
        _LOGGER.debug("Request method: %r", request.method)
        _LOGGER.debug("Request headers:")
        for header, value in request.headers.items():
            if header.lower() == 'authorization':
                value = '*****'
            _LOGGER.debug("    %r: %r", header, value)
        _LOGGER.debug("Request body:")

        # We don't want to log the binary data of a file upload.
        if isinstance(request.body, types.GeneratorType):
            _LOGGER.debug("File upload")
        else:
            _LOGGER.debug(str(request.body))
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.debug("Failed to log request: %r", err)


def log_response(_, _request, response, *_args, **kwargs):
    # type: (Any, ClientRequest, ClientResponse, str, Any) -> Optional[ClientResponse]
    """Log a server response.

    :param _: Unused in current version (will be None)
    :param requests.Request request: The request object.
    :param requests.Response response: The response object.
    """
    if not _LOGGER.isEnabledFor(logging.DEBUG):
        return None

    try:
        _LOGGER.debug("Response status: %r", response.status_code)
        _LOGGER.debug("Response headers:")
        for res_header, value in response.headers.items():
            _LOGGER.debug("    %r: %r", res_header, value)

        # We don't want to log binary data if the response is a file.
        _LOGGER.debug("Response content:")
        pattern = re.compile(r'attachment; ?filename=["\w.]+', re.IGNORECASE)
        header = response.headers.get('content-disposition')

        if header and pattern.match(header):
            filename = header.partition('=')[2]
            _LOGGER.debug("File attachments: %s", filename)
        elif response.headers.get("content-type", "").endswith("octet-stream"):
            _LOGGER.debug("Body contains binary data.")
        elif response.headers.get("content-type", "").startswith("image"):
            _LOGGER.debug("Body contains image data.")
        else:
            if kwargs.get('stream', False):
                _LOGGER.debug("Body is streamable")
            else:
                _LOGGER.debug(response.text())
        return response
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.debug("Failed to log response: %s", repr(err))
        return response
