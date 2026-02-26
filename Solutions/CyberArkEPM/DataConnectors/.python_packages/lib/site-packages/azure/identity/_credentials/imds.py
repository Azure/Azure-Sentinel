# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
from typing import Any, Optional, Dict

from azure.core.pipeline import PipelineResponse
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.rest import HttpRequest
from azure.core.credentials import AccessTokenInfo
from azure.core.pipeline.policies import RetryPolicy

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal import within_credential_chain
from .._internal.managed_identity_client import ManagedIdentityClient
from .._internal.msal_managed_identity_client import MsalManagedIdentityClient


IMDS_AUTHORITY = "http://169.254.169.254"
IMDS_TOKEN_PATH = "/metadata/identity/oauth2/token"

PIPELINE_SETTINGS = {
    "connection_timeout": 2,
    # Five retries, with each retry sleeping for [0.0s, 1.6s, 3.2s, 6.4s, 12.8s] between attempts.
    "retry_backoff_factor": 0.8,
    "retry_backoff_max": 60,
    "retry_on_status_codes": [404, 410, 429] + list(range(500, 600)),
    "retry_status": 5,
    "retry_total": 5,
}


class ImdsRetryPolicy(RetryPolicy):
    """Custom retry policy for IMDS credential with extended retry duration for 410 responses.

    This policy ensures that specifically for 410 status codes, the total exponential backoff duration
    is at least 70 seconds to handle temporary IMDS endpoint unavailability.
    For other status codes, it uses the standard retry behavior.
    """

    def __init__(self, **kwargs: Any) -> None:
        # Increased backoff factor to ensure at least 70 seconds retry duration for 410 responses.
        # Five retries, with each retry sleeping for [0.0s, 5.0s, 10.0s, 20.0s, 40.0s] between attempts (75s total)
        self.backoff_factor_for_410 = 2.5
        super().__init__(**kwargs)

    def is_retry(self, settings: Dict[str, Any], response: PipelineResponse[Any, Any]) -> bool:
        if response.http_response.status_code == 410:
            settings["backoff"] = self.backoff_factor_for_410
        else:
            settings["backoff"] = self.backoff_factor
        return super().is_retry(settings, response)


def _get_request(scope: str, identity_config: Dict) -> HttpRequest:
    url = (
        os.environ.get(EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST, IMDS_AUTHORITY).strip("/")
        + IMDS_TOKEN_PATH
    )
    return HttpRequest("GET", url, params=dict({"api-version": "2018-02-01", "resource": scope}, **identity_config))


def _check_forbidden_response(ex: HttpResponseError) -> None:
    """Special case handling for Docker Desktop.

    Docker Desktop proxies all HTTP traffic, and if the IMDS endpoint is unreachable, it
    responds with a 403 with a message that contains "unreachable".

    :param ~azure.core.exceptions.HttpResponseError ex: The exception raised by the request
    :raises ~azure.core.exceptions.CredentialUnavailableError: When the IMDS endpoint is unreachable
    """
    if ex.status_code == 403:
        if ex.message and "unreachable" in ex.message:
            error_message = f"ManagedIdentityCredential authentication unavailable. Error: {ex.message}"
            raise CredentialUnavailableError(message=error_message) from ex


class ImdsCredential(MsalManagedIdentityClient):
    def __init__(self, **kwargs: Any) -> None:
        # If set to True/False, _enable_imds_probe forces whether or not the credential
        # probes for the IMDS endpoint before attempting to get a token. If None (the default),
        # the credential probes only if it's part of a ChainedTokenCredential chain.
        self._enable_imds_probe = kwargs.pop("_enable_imds_probe", None)
        super().__init__(retry_policy_class=ImdsRetryPolicy, **dict(PIPELINE_SETTINGS, **kwargs))
        self._config = kwargs

        if EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST in os.environ:
            self._endpoint_available: Optional[bool] = True
        else:
            self._endpoint_available = None

    def __enter__(self) -> "ImdsCredential":
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def _request_token(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:

        do_probe = self._enable_imds_probe if self._enable_imds_probe is not None else within_credential_chain.get()
        if do_probe and not self._endpoint_available:
            # Probe to see if the IMDS endpoint is available to avoid hanging for a long time if it's not.
            try:
                client = ManagedIdentityClient(_get_request, **dict(PIPELINE_SETTINGS, **self._config))
                client.request_token(*scopes, connection_timeout=1, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError as ex:
                # IMDS responded
                _check_forbidden_response(ex)
                self._endpoint_available = True
            except Exception as ex:
                error_message = (
                    "ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint."
                )
                raise CredentialUnavailableError(error_message) from ex

        try:
            token_info = super()._request_token(*scopes, **kwargs)
        except CredentialUnavailableError:
            # Response is not json, skip the IMDS credential
            raise
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                error_message = (
                    "ManagedIdentityCredential authentication unavailable. "
                    "No identity has been assigned to this resource."
                )

                if ex.message:
                    error_message += f" Error: {ex.message}"

                raise CredentialUnavailableError(message=error_message) from ex

            _check_forbidden_response(ex)
            # any other error is unexpected
            raise ClientAuthenticationError(message=ex.message, response=ex.response) from ex
        except json.decoder.JSONDecodeError as ex:
            raise CredentialUnavailableError(message="ManagedIdentityCredential authentication unavailable.") from ex
        except Exception as ex:
            # if anything else was raised, assume the endpoint is unavailable
            error_message = "ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint."
            raise CredentialUnavailableError(error_message) from ex
        return token_info

    def get_unavailable_message(self, desc: str = "") -> str:
        return f"ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint. {desc}"
