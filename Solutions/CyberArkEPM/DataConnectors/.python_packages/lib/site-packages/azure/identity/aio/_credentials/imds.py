# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Optional, Any, Dict

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AccessTokenInfo
from azure.core.pipeline.policies import AsyncRetryPolicy
from azure.core.pipeline import PipelineResponse

from ... import CredentialUnavailableError
from ..._constants import EnvironmentVariables
from .._internal import AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.managed_identity_client import AsyncManagedIdentityClient
from ..._internal import within_credential_chain
from ..._credentials.imds import _get_request, _check_forbidden_response, PIPELINE_SETTINGS


class AsyncImdsRetryPolicy(AsyncRetryPolicy):
    """Async custom retry policy for IMDS credential with extended retry duration for 410 responses.

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


class ImdsCredential(AsyncContextManager, GetTokenMixin):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__()

        # If set to True/False, _enable_imds_probe forces whether or not the credential
        # probes for the IMDS endpoint before attempting to get a token. If None (the default),
        # the credential probes only if it's part of a ChainedTokenCredential chain.
        self._enable_imds_probe = kwargs.pop("_enable_imds_probe", None)
        kwargs["retry_policy_class"] = AsyncImdsRetryPolicy
        self._client = AsyncManagedIdentityClient(_get_request, **dict(PIPELINE_SETTINGS, **kwargs))
        if EnvironmentVariables.AZURE_POD_IDENTITY_AUTHORITY_HOST in os.environ:
            self._endpoint_available: Optional[bool] = True
        else:
            self._endpoint_available = None
        self._user_assigned_identity = "client_id" in kwargs or "identity_config" in kwargs

    async def __aenter__(self) -> "ImdsCredential":
        await self._client.__aenter__()
        return self

    async def close(self) -> None:
        await self._client.close()

    async def _acquire_token_silently(self, *scopes: str, **kwargs: Any) -> Optional[AccessTokenInfo]:
        return self._client.get_cached_token(*scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:

        do_probe = self._enable_imds_probe if self._enable_imds_probe is not None else within_credential_chain.get()
        if do_probe and not self._endpoint_available:
            # Probe to see if the IMDS endpoint is available to avoid hanging for a long time if it's not.
            try:
                await self._client.request_token(*scopes, connection_timeout=1, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError as ex:
                # IMDS responded
                _check_forbidden_response(ex)
                self._endpoint_available = True
            except Exception as ex:
                error_message = (
                    "ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint."
                )
                raise CredentialUnavailableError(message=error_message) from ex

        try:
            token_info = await self._client.request_token(*scopes, headers={"Metadata": "true"})
        except CredentialUnavailableError:
            # Response is not json, skip the IMDS credential
            raise
        except HttpResponseError as ex:
            # 400 in response to a token request indicates managed identity is disabled,
            # or the identity with the specified client_id is not available
            if ex.status_code == 400:
                error_message = "ManagedIdentityCredential authentication unavailable. "
                if self._user_assigned_identity:
                    error_message += "The requested identity has not been assigned to this resource."
                else:
                    error_message += "No identity has been assigned to this resource."

                if ex.message:
                    error_message += f" Error: {ex.message}"

                raise CredentialUnavailableError(message=error_message) from ex

            _check_forbidden_response(ex)
            # any other error is unexpected
            raise ClientAuthenticationError(message=ex.message, response=ex.response) from ex
        except Exception as ex:
            # if anything else was raised, assume the endpoint is unavailable
            error_message = "ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint."
            raise CredentialUnavailableError(error_message) from ex
        return token_info
