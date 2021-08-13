# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from typing import TYPE_CHECKING

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import SansIOHTTPPolicy

try:
    from azure.core.pipeline.transport import AsyncHttpTransport
except ImportError:
    AsyncHttpTransport = None  # type: ignore

try:
    from yarl import URL
except ImportError:
    pass

from ._common_conversion import (
    _sign_string,
)

from ._error import (
    _wrap_exception,
)

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest  # pylint: disable=ungrouped-imports


logger = logging.getLogger(__name__)


class AzureSigningError(ClientAuthenticationError):
    """
    Represents a fatal error when attempting to sign a request.
    In general, the cause of this exception is user error. For example, the given account key is not valid.
    Please visit https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account for more info.
    """


# pylint: disable=no-self-use
class SharedKeyCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, credential, is_emulated=False):
        self._credential = credential
        self.is_emulated = is_emulated

    def _get_headers(self, request, headers_to_sign):
        headers = dict(
            (name.lower(), value) for name, value in request.headers.items() if value
        )
        if "content-length" in headers and headers["content-length"] == "0":
            del headers["content-length"]
        return "\n".join(headers.get(x, "") for x in headers_to_sign) + "\n"

    def _get_verb(self, request):
        return request.method + "\n"

    def _get_canonicalized_resource(self, request):
        uri_path = urlparse(request.http_request.url).path
        try:
            if (
                isinstance(request.context.transport, AsyncHttpTransport)
                or isinstance(
                    getattr(request.context.transport, "_transport", None),
                    AsyncHttpTransport,
                )
                or isinstance(
                    getattr(
                        getattr(request.context.transport, "_transport", None),
                        "_transport",
                        None,
                    ),
                    AsyncHttpTransport,
                )
            ):
                uri_path = URL(uri_path)
                return "/" + self._credential.named_key.name + str(uri_path)
        except TypeError:
            pass
        return "/" + self._credential.named_key.name + uri_path

    def _get_canonicalized_headers(self, request):
        string_to_sign = ""
        x_ms_headers = []
        for name, value in request.headers.items():
            if name.startswith("x-ms-"):
                x_ms_headers.append((name.lower(), value))
        x_ms_headers.sort()
        for name, value in x_ms_headers:
            if value is not None:
                string_to_sign += "".join([name, ":", value, "\n"])
        return string_to_sign

    def _add_authorization_header(self, request, string_to_sign):
        try:
            signature = _sign_string(self._credential.named_key.key, string_to_sign)
            auth_string = "SharedKey " + self._credential.named_key.name + ":" + signature
            request.headers["Authorization"] = auth_string
        except Exception as ex:
            # Wrap any error that occurred as signing error
            # Doing so will clarify/locate the source of problem
            raise _wrap_exception(ex, AzureSigningError)

    def on_request(self, request):
    # type: (PipelineRequest) -> None
        self.sign_request(request)

    def sign_request(self, request):
        string_to_sign = (
            self._get_verb(request.http_request)
            + self._get_headers(
                request.http_request,
                ["content-md5", "content-type", "x-ms-date"],
            )
            + self._get_canonicalized_resource(request)
            + self._get_canonicalized_resource_query(request.http_request)
        )
        self._add_authorization_header(request.http_request, string_to_sign)
        logger.debug("String_to_sign=%s", string_to_sign)

    def _get_canonicalized_resource_query(self, request):
        for name, value in request.query.items():
            if name == "comp":
                return "?comp=" + value
        return ""
