# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc

from .aad_client import AadClient
from .decorators import wrap_exceptions


class AsyncContextManager(abc.ABC):
    @abc.abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


__all__ = ["AadClient", "AsyncContextManager", "wrap_exceptions"]
