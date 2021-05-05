# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import logging
from typing import TYPE_CHECKING

from azure.core.polling import AsyncPollingMethod
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

if TYPE_CHECKING:
    # pylint:disable=ungrouped-imports
    from typing import Any, Callable, Union

logger = logging.getLogger(__name__)


class AsyncDeleteRecoverPollingMethod(AsyncPollingMethod):
    """Poller for deleting resources, and recovering deleted resources, in vaults with soft-delete enabled.

    This works by polling for the existence of the deleted or recovered resource. When a resource is deleted, Key Vault
    immediately removes it from its collection. However, the resource will not immediately appear in the deleted
    collection. Key Vault will therefore respond 404 to GET requests for the deleted resource; when it responds 2xx,
    the resource exists in the deleted collection i.e. its deletion is complete.

    Similarly, while recovering a deleted resource, Key Vault will respond 404 to GET requests for the non-deleted
    resource; when it responds 2xx, the resource exists in the non-deleted collection, i.e. its recovery is complete.
    """

    def __init__(self, command, final_resource, finished, interval=2):
        self._command = command
        self._resource = final_resource
        self._polling_interval = interval
        self._finished = finished

    def initialize(self, client, initial_response, deserialization_callback):
        pass

    async def _update_status(self) -> None:
        try:
            await self._command()
            self._finished = True
        except ResourceNotFoundError:
            pass
        except HttpResponseError as e:
            # If we are polling on get_deleted_* and we don't have get permissions, we will get
            # ResourceNotFoundError until the resource is recovered, at which point we'll get a 403.
            if e.status_code == 403:
                self._finished = True
            else:
                raise

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_status()
                if not self.finished():
                    await asyncio.sleep(self._polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        return self._finished

    def resource(self) -> "Any":
        return self._resource

    def status(self) -> str:
        return "finished" if self._finished else "polling"
