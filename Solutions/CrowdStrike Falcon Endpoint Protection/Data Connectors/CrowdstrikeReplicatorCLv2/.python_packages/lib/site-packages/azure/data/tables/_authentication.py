# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, SansIOHTTPPolicy

try:
    from azure.core.pipeline.transport import AsyncHttpTransport
except ImportError:
    AsyncHttpTransport = None  # type: ignore

try:
    from yarl import URL # cspell:disable-line
except ImportError:
    pass

from ._common_conversion import (
    _sign_string,
)

from ._error import (
    _wrap_exception,
)

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineResponse, PipelineRequest  # pylint: disable=ungrouped-imports


class AzureSigningError(ClientAuthenticationError):
    """
    Represents a fatal error when attempting to sign a request.
    In general, the cause of this exception is user error. For example, the given account key is not valid.
    Please visit https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account for more info.
    """


class _HttpChallenge(object):  # pylint:disable=too-few-public-methods
    """Represents a parsed HTTP WWW-Authentication Bearer challenge from a server."""

    def __init__(self, challenge):
        if not challenge:
            raise ValueError("Challenge cannot be empty")

        self._parameters = {}

        # Split the scheme ("Bearer") from the challenge parameters
        trimmed_challenge = challenge.strip()
        split_challenge = trimmed_challenge.split(" ", 1)
        trimmed_challenge = split_challenge[1]

        # Split trimmed challenge into name=value pairs; these pairs are expected to be split by either commas or spaces
        # Values may be surrounded by quotes, which are stripped here
        separator = "," if "," in trimmed_challenge else " "
        for item in trimmed_challenge.split(separator):
            # Process 'name=value' pairs
            comps = item.split("=")
            if len(comps) == 2:
                key = comps[0].strip(' "')
                value = comps[1].strip(' "')
                if key:
                    self._parameters[key] = value

        # Challenge must specify authorization or authorization_uri
        if not self._parameters or (
            "authorization" not in self._parameters and "authorization_uri" not in self._parameters
        ):
            raise ValueError("Invalid challenge parameters. `authorization` or `authorization_uri` must be present.")

        authorization_uri = self._parameters.get("authorization") or self._parameters.get("authorization_uri") or ""
        # the authorization server URI should look something like https://login.windows.net/tenant-id[/oauth2/authorize]
        uri_path = urlparse(authorization_uri).path.lstrip("/")
        self.tenant_id = uri_path.split("/")[0] or None

        self.scope = self._parameters.get("scope") or ""
        self.resource = self._parameters.get("resource") or self._parameters.get("resource_id") or ""


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

    def _get_canonicalized_resource_query(self, request):
        for name, value in request.query.items():
            if name == "comp":
                return "?comp=" + value
        return ""


class BearerTokenChallengePolicy(BearerTokenCredentialPolicy):
    """Adds a bearer token Authorization header to requests, for the tenant provided in authentication challenges.

    See https://docs.microsoft.com/azure/active-directory/develop/claims-challenge for documentation on AAD
    authentication challenges.

    :param credential: The credential.
    :type credential: ~azure.core.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    :keyword bool discover_tenant: Determines if tenant discovery should be enabled. Defaults to True.
    :keyword bool discover_scopes: Determines if scopes from authentication challenges should be provided to token
        requests, instead of the scopes given to the policy's constructor, if any are present. Defaults to True.
    :raises: :class:`~azure.core.exceptions.ServiceRequestError`
    """

    def __init__(
        self,
        credential: "TokenCredential",
        *scopes: str,
        discover_tenant: bool = True,
        discover_scopes: bool = True,
        **kwargs: "Any"
    ) -> None:
        self._discover_tenant = discover_tenant
        self._discover_scopes = discover_scopes
        super().__init__(credential, *scopes, **kwargs)

    def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        """
        if not self._discover_tenant and not self._discover_scopes:
            # We can't discover the tenant or use a different scope; the request will fail because it hasn't changed
            return False

        try:
            challenge = _HttpChallenge(response.http_response.headers.get("WWW-Authenticate"))
            # azure-identity credentials require an AADv2 scope but the challenge may specify an AADv1 resource
            # if no scopes are included in the challenge, challenge.scope and challenge.resource will both be ''
            scope = challenge.scope or challenge.resource + "/.default" if self._discover_scopes else self._scopes
            if scope == "/.default":
                scope = self._scopes
        except ValueError:
            return False

        if self._discover_tenant:
            self.authorize_request(request, scope, tenant_id=challenge.tenant_id)
        else:
            self.authorize_request(request, scope)
        return True
