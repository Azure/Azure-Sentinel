import logging
import time

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
)
from azure.storage.blob import BlobLeaseClient

from services.azure_clients import get_blob_service_client

LOCK_CONTAINER = "checkpoints"
# Azure Blob leases only support a fixed duration between 15-60s, or
# infinite (-1). A single feed page cycle (fetch up to 120s timeout,
# normalize, upload) can exceed 60s, so a fixed lease renewed only once
# per page would expire on slow-but-successful pages.
#
# Strategy: infinite lease while the owner is alive, plus a stale-lock
# breaker. On acquire we write owner metadata (acquired_at UTC epoch).
# If another instance sees a 409 and the lock is older than
# STALE_LOCK_SECONDS, it breaks the lease and retries once. A crash
# mid-feed therefore recovers automatically after the stale window
# instead of deadlocking the feed forever.
LEASE_DURATION = -1
STALE_LOCK_SECONDS = 2 * 60 * 60  # 2 hours
_META_ACQUIRED_AT = "acquired_at"


class LockLostError(RuntimeError):
    """
    Raised when the distributed feed lock's lease could not be
    renewed (taken by another instance after being explicitly broken,
    or the lock blob/container was removed out from under us).

    Surfacing this as a distinct exception makes it clear in
    logs/alerts that this was a coordination issue, not a data or
    network failure, and stops the loop instead of continuing to
    write under a lock we may no longer hold.
    """


class FeedLock:
    def __init__(self, storage_account_name: str, feed_name: str):
        self.feed_name = feed_name
        self.lease_client: BlobLeaseClient | None = None

        blob_service_client = get_blob_service_client(storage_account_name)

        self.container_client = blob_service_client.get_container_client(LOCK_CONTAINER)

        self.blob_client = self.container_client.get_blob_client(
            f"locks/{feed_name}.lock"
        )

    def ensure_lock_blob(self) -> None:
        try:
            self.container_client.get_container_properties()
        except ResourceNotFoundError:
            try:
                self.container_client.create_container()
            except ResourceExistsError:
                # Ignored: Safe race condition if another worker created the container concurrently.
                pass

            logging.info(
                "Created checkpoint container: %s",
                LOCK_CONTAINER,
            )

        try:
            self.blob_client.get_blob_properties()
        except ResourceNotFoundError:
            try:
                self.blob_client.upload_blob(
                    b"whoisfreaks-feed-lock",
                    overwrite=False,
                )
                logging.info(
                    "Created lock blob: %s",
                    self.blob_client.blob_name,
                )
            except ResourceExistsError:
                # Ignored: Safe race condition if another worker created the lock blob concurrently.
                pass

    def _write_acquired_at(self) -> None:
        """Stamp ownership so a later acquirer can detect a stale lock."""
        try:
            # Must pass the active lease id — Azure rejects metadata
            # updates on a leased blob without LeaseId (LeaseIdMissing).
            kwargs = {}
            if self.lease_client is not None:
                kwargs["lease"] = self.lease_client.id
            self.blob_client.set_blob_metadata(
                {_META_ACQUIRED_AT: str(int(time.time()))},
                **kwargs,
            )
        except HttpResponseError:
            logging.exception(
                "Failed to write lock acquired_at metadata: feed=%s",
                self.feed_name,
            )

    def _is_stale(self) -> bool:
        try:
            props = self.blob_client.get_blob_properties()
            acquired_raw = (props.metadata or {}).get(_META_ACQUIRED_AT)
            if not acquired_raw:
                # No timestamp — treat as stale so a crash before the
                # metadata write cannot permanently deadlock the feed.
                return True
            age = time.time() - int(acquired_raw)
            return age >= STALE_LOCK_SECONDS
        except (HttpResponseError, ValueError, TypeError):
            logging.exception(
                "Could not evaluate lock staleness: feed=%s",
                self.feed_name,
            )
            return False

    def _try_break_stale(self) -> bool:
        if not self._is_stale():
            return False
        try:
            breaker = BlobLeaseClient(client=self.blob_client)
            breaker.break_lease(lease_break_period=0)
            logging.warning(
                "Broke stale feed lock: feed=%s (age > %ss)",
                self.feed_name,
                STALE_LOCK_SECONDS,
            )
            return True
        except HttpResponseError:
            logging.exception(
                "Failed to break stale lock: feed=%s",
                self.feed_name,
            )
            return False

    def acquire(self) -> bool:
        self.ensure_lock_blob()

        for attempt in range(2):
            try:
                self.lease_client = BlobLeaseClient(client=self.blob_client)

                self.lease_client.acquire(lease_duration=LEASE_DURATION)
                self._write_acquired_at()

                logging.info(
                    "Feed lock acquired: feed=%s",
                    self.feed_name,
                )
                return True

            except HttpResponseError as exc:
                if exc.status_code == 409:
                    if attempt == 0 and self._try_break_stale():
                        continue
                    logging.info(
                        "Feed already locked; skipping: feed=%s",
                        self.feed_name,
                    )
                    self.lease_client = None
                    return False
                raise

        self.lease_client = None
        return False

    def renew(self) -> None:
        if self.lease_client is None:
            return

        try:
            self.lease_client.renew()
            self._write_acquired_at()

            logging.debug(
                "Feed lock renewed: feed=%s",
                self.feed_name,
            )

        except HttpResponseError as exc:
            # The lease is gone either way -- don't try to release
            # a lease we no longer hold.
            self.lease_client = None

            raise LockLostError(
                f"Lost the distributed lock for feed={self.feed_name} "
                "(lease expired or was taken by another instance)."
            ) from exc

    def release(self) -> None:
        if self.lease_client is None:
            return

        try:
            self.lease_client.release()

            logging.info(
                "Feed lock released: feed=%s",
                self.feed_name,
            )

        except HttpResponseError:
            logging.exception(
                "Failed to release feed lock: feed=%s",
                self.feed_name,
            )

        finally:
            self.lease_client = None
