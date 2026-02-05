# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Any, Dict, Optional

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline import PipelineRequest, PipelineResponse

from .._constants import EnvironmentVariables
from .._internal.managed_identity_base import ManagedIdentityBase
from .._internal.managed_identity_client import ManagedIdentityClient


class AzureArcCredential(ManagedIdentityBase):
    def get_client(self, **kwargs: Any) -> Optional[ManagedIdentityClient]:
        url = os.environ.get(EnvironmentVariables.IDENTITY_ENDPOINT)
        imds = os.environ.get(EnvironmentVariables.IMDS_ENDPOINT)
        if url and imds:
            return ManagedIdentityClient(
                _per_retry_policies=[ArcChallengeAuthPolicy()],
                request_factory=functools.partial(_get_request, url),
                **kwargs
            )
        return None

    def __enter__(self) -> "AzureArcCredential":
        if self._client:
            self._client.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._client:
            self._client.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def get_unavailable_message(self) -> str:
        return "Azure Arc managed identity configuration not found in environment"


def _get_request(url: str, scope: str, identity_config: Dict) -> HttpRequest:
    if identity_config:
        raise ClientAuthenticationError(
            message="User assigned managed identities are not supported by Azure Arc. To authenticate with the system "
            "assigned identity omit the client id when constructing the credential, and if authenticating with "
            "DefaultAzureCredential ensure the AZURE_CLIENT_ID environment variable is not set."
        )

    request = HttpRequest("GET", url)
    request.format_parameters(dict({"api-version": "2019-11-01", "resource": scope}, **identity_config))
    return request


def _get_secret_key(response: PipelineResponse) -> str:
    # expecting header containing path to secret key file
    header = response.http_response.headers.get("WWW-Authenticate")
    if not header:
        raise ClientAuthenticationError(message="Did not receive a value from WWW-Authenticate header")

    # expecting header with structure like 'Basic realm=<file path>'
    try:
        key_file = header.split("=")[1]
    except IndexError as ex:
        raise ClientAuthenticationError(
            message="Did not receive a correct value from WWW-Authenticate header: {}".format(header)
        ) from ex
    with open(key_file, "r", encoding="utf-8") as file:
        try:
            return file.read()
        except Exception as error:  # pylint:disable=broad-except
            # user is expected to have obtained read permission prior to this being called
            raise ClientAuthenticationError(
                message="Could not read file {} contents: {}".format(key_file, error)
            ) from error


class ArcChallengeAuthPolicy(HTTPPolicy):
    """Policy for handling Azure Arc's challenge authentication"""

    def send(self, request: PipelineRequest) -> PipelineResponse:
        request.http_request.headers["Metadata"] = "true"
        response = self.next.send(request)

        if response.http_response.status_code == 401:
            secret_key = _get_secret_key(response)
            request.http_request.headers["Authorization"] = "Basic {}".format(secret_key)
            response = self.next.send(request)

        return response
