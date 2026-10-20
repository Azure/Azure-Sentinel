"""Send events to Microsoft Sentinel through the Logs Ingestion API and the existing data collection rule."""
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

from . import consts
from .exceptions import CensysException
from .logger import applogger


class SentinelIngestor:
    """Uploads risk events to the data collection rule stream."""

    def __init__(self, endpoint: str, rule_id: str, stream_name: str, scope: str):
        """Create the ingestion client. DefaultAzureCredential uses the Function App managed identity."""
        self.rule_id = rule_id
        self.stream_name = stream_name
        if ".us" in scope:
            credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
        else:
            credential = DefaultAzureCredential()
        self.client = LogsIngestionClient(endpoint, credential=credential, credential_scopes=[scope])

    def upload(self, events: list) -> None:
        """Upload one page of events. Raises when any part of the upload fails, so the checkpoint is not advanced."""
        logs = [{field: event.get(field) for field in consts.EVENT_FIELDS} for event in events]
        try:
            self.client.upload(rule_id=self.rule_id, stream_name=self.stream_name, logs=logs)
        except ClientAuthenticationError as err:
            applogger.error(f"{consts.LOG_PREFIX}: authentication error while uploading to Sentinel: {err}")
            raise CensysException(f"Authentication error while uploading to Sentinel: {err}")
        except HttpResponseError as err:
            applogger.error(f"{consts.LOG_PREFIX}: HTTP error while uploading to Sentinel: {err}")
            raise CensysException(f"HTTP error while uploading to Sentinel: {err}")
        except Exception as err:
            applogger.error(f"{consts.LOG_PREFIX}: unexpected error while uploading to Sentinel: {err}")
            raise CensysException(f"Unexpected error while uploading to Sentinel: {err}")
