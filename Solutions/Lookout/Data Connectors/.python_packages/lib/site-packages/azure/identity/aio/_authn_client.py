# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.credentials import AccessToken
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    AsyncRetryPolicy,
    ContentDecodePolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    UserAgentPolicy,
)
from azure.core.pipeline.transport import AioHttpTransport

from .._authn_client import AuthnClientBase
from .._internal.user_agent import USER_AGENT

if TYPE_CHECKING:
    from typing import Any, Dict, Iterable, Mapping, Optional
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.core.pipeline.transport import AsyncHttpTransport


class AsyncAuthnClient(AuthnClientBase):  # pylint:disable=async-client-bad-name
    """Async authentication client"""

    # pylint:disable=missing-client-constructor-parameter-credential
    def __init__(
        self,
        config: "Optional[Configuration]" = None,
        policies: "Optional[Iterable[HTTPPolicy]]" = None,
        transport: "Optional[AsyncHttpTransport]" = None,
        **kwargs: "Any"
    ) -> None:
        config = config or self._create_config(**kwargs)
        policies = policies or [
            ContentDecodePolicy(),
            config.user_agent_policy,
            config.proxy_policy,
            config.retry_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]
        if not transport:
            transport = AioHttpTransport(**kwargs)
        self._pipeline = AsyncPipeline(transport=transport, policies=policies)
        super().__init__(**kwargs)

    async def __aenter__(self):
        await self._pipeline.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        await self._pipeline.__aexit__()

    async def request_token(  # pylint:disable=invalid-overridden-method
        self,
        scopes: "Iterable[str]",
        method: "Optional[str]" = "POST",
        headers: "Optional[Mapping[str, str]]" = None,
        form_data: "Optional[Mapping[str, str]]" = None,
        params: "Optional[Dict[str, str]]" = None,
        **kwargs: "Any"
    ) -> AccessToken:
        request = self._prepare_request(method, headers=headers, form_data=form_data, params=params)
        request_time = int(time.time())
        self._last_refresh_time = request_time  # no matter succeed or not, update the last refresh time
        response = await self._pipeline.run(request, stream=False, **kwargs)
        token = self._deserialize_and_cache_token(response=response, scopes=scopes, request_time=request_time)
        return token

    @staticmethod
    def _create_config(**kwargs: "Any") -> Configuration:
        config = Configuration(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.retry_policy = AsyncRetryPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)
        return config
