# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, List, Mapping, Optional, Union, TYPE_CHECKING
from uuid import uuid4

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    AsyncBearerTokenCredentialPolicy,
    AsyncRedirectPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy,
    ProxyPolicy,
    AzureSasCredentialPolicy,
    RequestIdPolicy,
    CustomHookPolicy,
    NetworkTraceLoggingPolicy,
)
from azure.core.pipeline.transport import (
    AsyncHttpTransport,
    HttpRequest,
)

from .._generated.aio import AzureTable
from .._base_client import AccountHostsMixin, get_api_version, extract_batch_part_metadata
from .._authentication import SharedKeyCredentialPolicy
from .._constants import STORAGE_OAUTH_SCOPE
from .._error import RequestTooLargeError, TableTransactionError, _decode_error
from .._policies import StorageHosts, StorageHeadersPolicy
from .._sdk_moniker import SDK_MONIKER
from ._policies_async import AsyncTablesRetryPolicy

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class AsyncTablesBaseClient(AccountHostsMixin):

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential
        self,
        endpoint: str,
        *,
        credential: Optional[Union[AzureSasCredential, AzureNamedKeyCredential, "AsyncTokenCredential"]] = None,
        **kwargs: Any
    ) -> None:
        super(AsyncTablesBaseClient, self).__init__(endpoint, credential=credential, **kwargs)  # type: ignore
        self._client = AzureTable(
            self.url,
            policies=kwargs.pop('policies', self._policies),
            **kwargs
        )
        self._client._config.version = get_api_version(kwargs, self._client._config.version)  # pylint: disable=protected-access


    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._client.close()

    def _configure_credential(self, credential):
        # type: (Any) -> None
        if hasattr(credential, "get_token"):
            self._credential_policy = AsyncBearerTokenCredentialPolicy(  # type: ignore
                credential, STORAGE_OAUTH_SCOPE
            )
        elif isinstance(credential, SharedKeyCredentialPolicy):
            self._credential_policy = credential  # type: ignore
        elif isinstance(credential, AzureSasCredential):
            self._credential_policy = AzureSasCredentialPolicy(credential)  # type: ignore
        elif isinstance(credential, AzureNamedKeyCredential):
            self._credential_policy = SharedKeyCredentialPolicy(credential)  # type: ignore
        elif credential is not None:
            raise TypeError("Unsupported credential: {}".format(credential))

    def _configure_policies(self, **kwargs):
        return [
            RequestIdPolicy(**kwargs),
            StorageHeadersPolicy(**kwargs),
            UserAgentPolicy(sdk_moniker=SDK_MONIKER, **kwargs),
            ProxyPolicy(**kwargs),
            self._credential_policy,
            ContentDecodePolicy(response_encoding="utf-8"),
            AsyncRedirectPolicy(**kwargs),
            StorageHosts(**kwargs),
            AsyncTablesRetryPolicy(**kwargs),
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs),
        ]

    async def _batch_send(self, *reqs: "HttpRequest", **kwargs) -> List[Mapping[str, Any]]:
        """Given a series of request, do a Storage batch call."""
        # Pop it here, so requests doesn't feel bad about additional kwarg
        policies = [StorageHeadersPolicy()]

        changeset = HttpRequest("POST", None)  # type: ignore
        changeset.set_multipart_mixed(
            *reqs, policies=policies, boundary="changeset_{}".format(uuid4())
        )
        request = self._client._client.post(  # pylint: disable=protected-access
            url="https://{}/$batch".format(self._primary_hostname),
            headers={
                "x-ms-version": self.api_version,
                "DataServiceVersion": "3.0",
                "MaxDataServiceVersion": "3.0;NetFx",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
        )
        request.set_multipart_mixed(
            changeset,
            policies=policies,
            enforce_https=False,
            boundary="batch_{}".format(uuid4()),
        )

        pipeline_response = await self._client._client._pipeline.run(request, **kwargs)  # pylint: disable=protected-access
        response = pipeline_response.http_response
        # TODO: Check for proper error model deserialization
        if response.status_code == 413:
            raise _decode_error(
                response,
                error_message="The transaction request was too large",
                error_type=RequestTooLargeError)
        if response.status_code != 202:
            raise _decode_error(response)

        parts_iter = response.parts()
        parts = []
        async for p in parts_iter:
            parts.append(p)
        error_parts = [p for p in parts if not 200 <= p.status_code < 300]
        if any(error_parts):
            if error_parts[0].status_code == 413:
                raise _decode_error(
                    response,
                    error_message="The transaction request was too large",
                    error_type=RequestTooLargeError)
            raise _decode_error(
                response=error_parts[0],
                error_type=TableTransactionError,
            )
        return [extract_batch_part_metadata(p) for p in parts]


class AsyncTransportWrapper(AsyncHttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """
    def __init__(self, async_transport):
        self._transport = async_transport

    async def send(self, request, **kwargs):
        return await self._transport.send(request, **kwargs)

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):  # pylint: disable=arguments-differ
        pass
