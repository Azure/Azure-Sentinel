import logging

from azure.core.exceptions import HttpResponseError

log = logging.getLogger(__name__)


class IngestionApiClient:
    def __init__(self, azure_ingestion_client, dcr_rule_id, dcr_stream):
        self._ingestion_client = azure_ingestion_client
        self._dcr_rule_id = dcr_rule_id
        self._dcr_stream = dcr_stream

    def upload_events(self, events):
        log.info("Uploading events to Log Workspace")
        try:
            self._ingestion_client.upload(
                rule_id=self._dcr_rule_id, stream_name=self._dcr_stream, logs=events
            )
            log.info("Events are uploaded")
        except HttpResponseError as e:
            raise Exception("Couldn't send data to Azure") from e
