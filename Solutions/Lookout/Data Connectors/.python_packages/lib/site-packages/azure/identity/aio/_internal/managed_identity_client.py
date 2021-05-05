# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncRetryPolicy

from ..._internal import _scopes_to_resource
from ..._internal.managed_identity_client import ManagedIdentityClient, _get_policies

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Callable, List, Optional, Union
    from azure.core.credentials import AccessToken
    from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy
    from azure.core.pipeline.transport import HttpTransport, HttpRequest

    Policy = Union[AsyncHTTPPolicy, SansIOHTTPPolicy]


# pylint:disable=async-client-bad-name,missing-client-constructor-parameter-credential
class AsyncManagedIdentityClient(ManagedIdentityClient):
    def __init__(self, request_factory: "Callable[[str, dict], HttpRequest]", **kwargs: "Any") -> None:
        config = _get_configuration(**kwargs)
        super().__init__(request_factory, _config=config, **kwargs)

    async def close(self) -> None:
        await self._pipeline.__aexit__()

    async def request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        # pylint:disable=invalid-overridden-method,unused-argument
        resource = _scopes_to_resource(*scopes)
        request = self._request_factory(resource, self._identity_config)
        request_time = int(time.time())
        response = await self._pipeline.run(request)
        token = self._process_response(response, request_time)
        return token

    def _build_pipeline(
        self,
        config: Configuration,
        policies: "Optional[List[Policy]]" = None,
        transport: "Optional[HttpTransport]" = None,
        **kwargs: "Any"
    ) -> AsyncPipeline:
        if policies is None:  # [] is a valid policy list
            policies = _get_policies(config, **kwargs)
        if not transport:
            from azure.core.pipeline.transport import AioHttpTransport

            transport = AioHttpTransport(**kwargs)

        return AsyncPipeline(transport=transport, policies=policies)


def _get_configuration(**kwargs: "Any") -> Configuration:
    config = Configuration()
    config.retry_policy = AsyncRetryPolicy(**kwargs)
    return config
