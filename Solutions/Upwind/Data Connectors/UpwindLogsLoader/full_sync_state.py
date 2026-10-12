"""Progress of the periodic full catalog sync, kept between runs in blob storage."""

import json
import logging
from datetime import datetime, timedelta

_CONTAINER_NAME = "upwind-catalog-loader"
_BLOB_NAME = "catalog-full-sync-state.json"


def is_full_sync_due(state: dict, now: datetime, interval_hours: int) -> bool:
    """
    Whether this run should work on the full catalog sync.

    A sync is due when one is already in progress (a saved cursor), when none
    has ever completed (a fresh install), or when the last one started at least
    ``interval_hours`` ago.

    :param state: Saved state, as returned by ``FullSyncStateStore.load``.
    :param now: The run's start time (timezone-aware).
    :param interval_hours: Hours between full syncs; 0 or less disables them.
    :return: True if the full sync should run in this invocation.
    """

    if interval_hours <= 0:
        return False

    if state.get("cursor"):
        return True

    last_completed_at = state.get("last_completed_at")
    if not last_completed_at:
        return True

    return now - datetime.fromisoformat(last_completed_at) >= timedelta(hours=interval_hours)


class FullSyncStateStore:
    """
    Reads and writes the full catalog sync's progress as a small JSON blob in
    the Function App's own storage account (``AzureWebJobsStorage``).

    The saved state is ``{"cursor", "started_at", "last_completed_at"}``:
    ``cursor`` is the next catalog page to fetch (None when no sync is in
    progress), and ``last_completed_at`` is when the last completed sync
    started, so every asset in the table is at most one interval older than it.
    """

    def __init__(self, connection_string: str):
        # Imported here so the rest of the function doesn't depend on the
        # storage SDK being importable when full syncs are turned off.
        from azure.storage.blob import BlobServiceClient

        service = BlobServiceClient.from_connection_string(connection_string)
        self._container = service.get_container_client(_CONTAINER_NAME)
        self._blob = self._container.get_blob_client(_BLOB_NAME)
        self._container_exists = False

    def load(self) -> dict:
        """Return the saved state, or an empty dict if nothing was saved yet."""

        from azure.core.exceptions import ResourceNotFoundError

        try:
            return json.loads(self._blob.download_blob().readall())
        except ResourceNotFoundError:
            return {}

    def save(self, state: dict) -> None:
        """Overwrite the saved state, creating the container on first use."""

        from azure.core.exceptions import ResourceExistsError

        if not self._container_exists:
            try:
                self._container.create_container()
            except ResourceExistsError:
                pass
            self._container_exists = True
        self._blob.upload_blob(json.dumps(state), overwrite=True)
        logging.debug("Saved full catalog sync state: %s", state)
