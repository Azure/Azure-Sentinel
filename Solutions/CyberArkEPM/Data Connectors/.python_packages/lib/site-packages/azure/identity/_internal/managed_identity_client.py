# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import logging
import time
from typing import Any, Callable, Dict, Optional

from msal import TokenCache

from azure.core.credentials import AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError, DecodeError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest
from .. import CredentialUnavailableError
from .._internal import _scopes_to_resource
from .._internal.pipeline import build_pipeline

_LOGGER = logging.getLogger(__name__)


class ManagedIdentityClientBase(abc.ABC):
    def __init__(
        self,
        request_factory: Callable[[str, dict], HttpRequest],
        client_id: Optional[str] = None,
        identity_config: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        self._custom_cache = False
        self._cache = kwargs.pop("_cache", None)
        if self._cache:
            self._custom_cache = True
        else:
            self._cache = TokenCache()
        self._content_callback = kwargs.pop("_content_callback", None)
        self._identity_config = identity_config or {}
        if client_id:
            self._identity_config["client_id"] = client_id
        self._pipeline = self._build_pipeline(**kwargs)
        self._request_factory = request_factory

    def _process_response(self, response: PipelineResponse, request_time: int) -> AccessTokenInfo:
        content = response.context.get(ContentDecodePolicy.CONTEXT_NAME)
        if not content:
            try:
                content = ContentDecodePolicy.deserialize_from_text(
                    response.http_response.text(), mime_type="application/json"
                )
            except DecodeError as ex:
                if response.http_response.content_type.startswith("application/json"):
                    message = "Failed to deserialize JSON from response"
                    raise ClientAuthenticationError(message=message, response=response.http_response) from ex
                message = 'Unexpected content type "{}"'.format(response.http_response.content_type)
                raise CredentialUnavailableError(message=message, response=response.http_response) from ex

        if not content:
            raise ClientAuthenticationError(message="No token received.", response=response.http_response)

        if "access_token" not in content or not ("expires_in" in content or "expires_on" in content):
            if content and "access_token" in content:
                content["access_token"] = "****"
            raise ClientAuthenticationError(
                message='Unexpected response "{}"'.format(content), response=response.http_response
            )

        if self._content_callback:
            self._content_callback(content)

        expires_on = int(content.get("expires_on") or int(content["expires_in"]) + request_time)
        content["expires_on"] = expires_on

        expires_in = int(content.get("expires_in") or expires_on - request_time)
        if "refresh_in" not in content and expires_in >= 7200:
            # MSAL TokenCache expects "refresh_in"
            content["refresh_in"] = expires_in // 2

        refresh_on = request_time + int(content["refresh_in"]) if "refresh_in" in content else None
        token = AccessTokenInfo(
            content["access_token"],
            content["expires_on"],
            token_type=content.get("token_type", "Bearer"),
            refresh_on=refresh_on,
        )

        # caching is the final step because TokenCache.add mutates its "event"
        self._cache.add(
            event={"response": content, "scope": [content["resource"]]},
            now=request_time,
        )

        return token

    def get_cached_token(self, *scopes: str, **kwargs: Any) -> Optional[AccessTokenInfo]:
        # Do not return a cached token if claims are provided.
        if kwargs.get("claims") is not None:
            return None

        resource = _scopes_to_resource(*scopes)
        now = time.time()
        for token in self._cache.search(TokenCache.CredentialType.ACCESS_TOKEN, target=[resource]):
            expires_on = int(token["expires_on"])
            refresh_on = int(token["refresh_on"]) if "refresh_on" in token else None
            if expires_on > now and (not refresh_on or refresh_on > now):
                expires_in = expires_on - int(now)
                refresh_on_msg = f", refresh in {refresh_on - int(now)}s" if refresh_on else ""
                _LOGGER.debug(
                    "Access token found in cache for resource %s (expires in %ss%s, cache ID: %s)",
                    resource,
                    expires_in,
                    refresh_on_msg,
                    id(self._cache),
                )
                return AccessTokenInfo(
                    token["secret"], expires_on, token_type=token.get("token_type", "Bearer"), refresh_on=refresh_on
                )

        return None

    @abc.abstractmethod
    def request_token(self, *scopes, **kwargs):
        pass

    @abc.abstractmethod
    def _build_pipeline(self, **kwargs):
        pass

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        # Remove the non-picklable entries
        if not self._custom_cache:
            del state["_cache"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        # Re-create the unpickable entries
        if not self._custom_cache:
            self._cache = TokenCache()


class ManagedIdentityClient(ManagedIdentityClientBase):
    def __enter__(self) -> "ManagedIdentityClient":
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._pipeline.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def request_token(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:
        resource = _scopes_to_resource(*scopes)
        request = self._request_factory(resource, self._identity_config)
        kwargs.pop("tenant_id", None)
        kwargs.pop("claims", None)
        request_time = int(time.time())
        response = self._pipeline.run(request, retry_on_methods=[request.method], **kwargs)
        token = self._process_response(response, request_time)
        return token

    def _build_pipeline(self, **kwargs):
        return build_pipeline(**kwargs)
