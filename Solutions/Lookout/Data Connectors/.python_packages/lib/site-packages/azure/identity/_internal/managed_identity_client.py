# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import time
from typing import TYPE_CHECKING

from msal import TokenCache

from azure.core.configuration import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HeadersPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    RetryPolicy,
    NetworkTraceLoggingPolicy,
)
from azure.identity._internal import _scopes_to_resource

from .user_agent import USER_AGENT

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Callable, List, Optional, Union
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import HttpTransport, HttpRequest

    PolicyType = Union[HTTPPolicy, SansIOHTTPPolicy]


class ManagedIdentityClient(object):
    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(self, request_factory, client_id=None, **kwargs):
        # type: (Callable[[str, dict], HttpRequest], Optional[str], **Any) -> None
        self._cache = kwargs.pop("_cache", None) or TokenCache()
        self._content_callback = kwargs.pop("_content_callback", None)
        self._identity_config = kwargs.pop("_identity_config", None) or {}
        if client_id:
            self._identity_config["client_id"] = client_id

        config = kwargs.pop("_config", None) or _get_configuration(**kwargs)
        self._pipeline = self._build_pipeline(config, **kwargs)

        self._request_factory = request_factory

    def get_cached_token(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        resource = _scopes_to_resource(*scopes)
        tokens = self._cache.find(TokenCache.CredentialType.ACCESS_TOKEN, target=[resource])
        for token in tokens:
            if token["expires_on"] > time.time():
                return AccessToken(token["secret"], token["expires_on"])
        return None

    def request_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        resource = _scopes_to_resource(*scopes)
        request = self._request_factory(resource, self._identity_config)
        request_time = int(time.time())
        response = self._pipeline.run(request)
        token = self._process_response(response, request_time)
        return token

    def _process_response(self, response, request_time):
        # type: (PipelineResponse, int) -> AccessToken

        # ContentDecodePolicy sets this, and should have raised if it couldn't deserialize the response
        content = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)  # type: dict
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

        token = AccessToken(content["access_token"], content["expires_on"])

        # caching is the final step because TokenCache.add mutates its "event"
        self._cache.add(
            event={"response": content, "scope": content["resource"]}, now=request_time,
        )

        return token

    def _build_pipeline(self, config, policies=None, transport=None, **kwargs):  # pylint:disable=no-self-use
        # type: (Configuration, Optional[List[PolicyType]], Optional[HttpTransport], **Any) -> Pipeline
        if policies is None:  # [] is a valid policy list
            policies = _get_policies(config, **kwargs)
        if not transport:
            from azure.core.pipeline.transport import RequestsTransport

            transport = RequestsTransport(**kwargs)

        return Pipeline(transport=transport, policies=policies)


def _get_policies(config, **kwargs):
    return [
        HeadersPolicy(**kwargs),
        UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs),
        config.proxy_policy,
        config.retry_policy,
        NetworkTraceLoggingPolicy(**kwargs),
        DistributedTracingPolicy(**kwargs),
        HttpLoggingPolicy(**kwargs),
    ]


def _get_configuration(**kwargs):
    # type: (**Any) -> Configuration
    config = Configuration()
    config.retry_policy = RetryPolicy(**kwargs)
    return config
