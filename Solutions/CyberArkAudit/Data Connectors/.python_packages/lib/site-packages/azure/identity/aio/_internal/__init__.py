# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
from types import TracebackType
from typing import Optional, Type

from .aad_client import AadClient
from .decorators import wrap_exceptions


class AsyncContextManager(abc.ABC):
    @abc.abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.close()


__all__ = ["AadClient", "AsyncContextManager", "wrap_exceptions"]
