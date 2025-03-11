import logging

from .events_formatter import Formatter

log = logging.getLogger(__name__)


class Connector:
    def __init__(self, withsecure_client, ingestion_client, storage_client):
        self._withsecure_client = withsecure_client
        self._ingestion_client = ingestion_client
        self._storage_client = storage_client
        self._common_security_log_formatter = Formatter()

    def execute(self):
        # TODO: haven't tested any resilience solutions - so not sure what will happen when network connection fails
        last_timestamp = self._storage_client.get_start_timestamp()

        log.info(f"Start polling from {last_timestamp}")
        all_events = self._withsecure_client.get_events_after(last_timestamp)
        log.info(f"Found {len(all_events)} since {last_timestamp}")
        if len(all_events) == 0:
            return
        new_last_timestamp = all_events[-1].persistenceTimestamp
        log.info(f"Last persistenceTimestamp: {new_last_timestamp}")

        # TODO: in case when function was down for too long it might timeout without moving forward
        # it will get the same old timestamp every execution
        # maybe limit of that can be greater if execution happens every 5 minutes instead of every minute
        self._ingestion_client.upload_events(
            [self.to_sentinel_format(event) for event in all_events]
        )

        self._storage_client.save_start_timestamp(new_last_timestamp)
        log.info(f"Updated timestamp in storage to: {new_last_timestamp}")

    def to_sentinel_format(self, event):
        return self._common_security_log_formatter.format(event)
