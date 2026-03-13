# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
from types import TracebackType
from typing import Any, cast, Optional, TypeVar, Type

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from . import AsyncContextManager
from .get_token_mixin import GetTokenMixin
from .managed_identity_client import AsyncManagedIdentityClient
from ... import CredentialUnavailableError

T = TypeVar("T", bound="AsyncManagedIdentityBase")


class AsyncManagedIdentityBase(AsyncContextManager, GetTokenMixin):
    """Base class for internal credentials using AsyncManagedIdentityClient"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self._client = self.get_client(**kwargs)

    @abc.abstractmethod
    def get_client(self, **kwargs) -> Optional[AsyncManagedIdentityClient]:
        pass

    @abc.abstractmethod
    def get_unavailable_message(self, desc: str = "") -> str:
        pass

    async def __aenter__(self: T) -> T:
        if self._client:
            await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        if self._client:
            await self._client.__aexit__(exc_type, exc_value, traceback)

    async def close(self) -> None:
        await self.__aexit__()

    async def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs: Any
    ) -> AccessToken:
        if not self._client:
            raise CredentialUnavailableError(message=self.get_unavailable_message())
        return await super().get_token(*scopes, claims=claims, tenant_id=tenant_id, **kwargs)

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        if not self._client:
            raise CredentialUnavailableError(message=self.get_unavailable_message())
        return await super().get_token_info(*scopes, options=options)

    async def _acquire_token_silently(self, *scopes: str, **kwargs) -> Optional[AccessTokenInfo]:
        # casting because mypy can't determine that these methods are called
        # only by get_token, which raises when self._client is None
        return cast(AsyncManagedIdentityClient, self._client).get_cached_token(*scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs) -> AccessTokenInfo:
        return await cast(AsyncManagedIdentityClient, self._client).request_token(*scopes, **kwargs)
