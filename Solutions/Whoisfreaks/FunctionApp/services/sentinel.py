import json
import logging

from azure.core.exceptions import HttpResponseError
from azure.monitor.ingestion import LogsIngestionClient

from models.feed import FeedConfig
from services.azure_clients import get_credential

# Azure Monitor Logs Ingestion API rejects bodies over ~1 MB.
# Stay under that with headroom for JSON overhead.
_MAX_BATCH_BYTES = 900_000


class SentinelIngestionService:
    """
    Uploads normalized records to Microsoft Sentinel via the Logs
    Ingestion API.

    NOTE ON MULTI-FEED SCALING: a single Data Collection Rule (DCR)
    can declare multiple streams, each mapped to its own custom
    table. This service is written so every enabled feed shares one
    DCR (one DCR_INGESTION_ENDPOINT / DCR_IMMUTABLE_ID) but uploads
    to a different stream (FeedConfig.stream_name) per feed. When you
    add a new feed's normalizer, make sure the DCR referenced by
    DCR_IMMUTABLE_ID also declares a stream named exactly the feed's
    FeedConfig.stream_name (e.g. "Custom-WhoisFreaksPhishing")
    (see config/feeds.py) routed to the matching custom table --
    otherwise upload() will fail with a 400 from the ingestion
    endpoint saying the stream isn't declared on that DCR.
    """

    def __init__(self, endpoint: str, dcr_immutable_id: str):

        self.dcr_id = dcr_immutable_id

        self.client = LogsIngestionClient(
            endpoint=endpoint,
            credential=get_credential(),
        )

    def upload(
        self,
        feed: FeedConfig,
        records: list[dict],
    ) -> None:

        if not records:
            logging.info(
                "No records to upload for feed=%s",
                feed.name,
            )
            return

        batches = self._chunk_by_bytes(records, feed_name=feed.name)

        logging.info(
            "Uploading %s records in %s batch(es): feed=%s stream=%s",
            len(records),
            len(batches),
            feed.name,
            feed.stream_name,
        )

        for index, batch in enumerate(batches, start=1):
            try:
                self.client.upload(
                    rule_id=self.dcr_id,
                    stream_name=feed.stream_name,
                    logs=batch,
                )
            except HttpResponseError:
                logging.exception(
                    "Sentinel ingestion failed: feed=%s batch=%s/%s size=%s",
                    feed.name,
                    index,
                    len(batches),
                    len(batch),
                )
                raise

            logging.info(
                "Uploaded batch %s/%s (%s records): feed=%s",
                index,
                len(batches),
                len(batch),
                feed.name,
            )

        logging.info(
            "Successfully uploaded %s records: feed=%s",
            len(records),
            feed.name,
        )

    @staticmethod
    def _chunk_by_bytes(
        records: list[dict], feed_name: str = "unknown"
    ) -> list[list[dict]]:
        """Split records into batches whose JSON payload stays under 1 MB."""
        batches: list[list[dict]] = []
        current: list[dict] = []
        current_size = 2  # opening/closing brackets of a JSON array

        for record in records:
            encoded = json.dumps(record, separators=(",", ":"), default=str)
            # +1 for the comma between array elements
            record_size = len(encoded.encode("utf-8")) + 1

            # Safeguard: Handle individual records that exceed _MAX_BATCH_BYTES
            if record_size > _MAX_BATCH_BYTES:
                logging.error(
                    "Single record size (%s bytes) exceeds maximum allowed batch limit (%s bytes). Dropping record to preserve stream: feed=%s",
                    record_size,
                    _MAX_BATCH_BYTES,
                    feed_name,
                )
                continue

            if current and current_size + record_size > _MAX_BATCH_BYTES:
                batches.append(current)
                current = []
                current_size = 2

            current.append(record)
            current_size += record_size

        if current:
            batches.append(current)

        return batches
