import asyncio
import json
import logging
from collections import deque
from typing import List, Dict, Any

from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from azure.core.exceptions import HttpResponseError


class SentinelConnector:
    """
    Connector for the Azure Monitor Logs Ingestion API.

    This replaces the deprecated HTTP Data Collector API with the new
    Logs Ingestion API that uses Microsoft Entra ID authentication.

    Requires:
    - Data Collection Endpoint (DCE) URI
    - Data Collection Rule (DCR) Immutable ID
    - Stream name (usually "Custom-{TableName}")
    - Managed Identity or Azure AD credentials
    """

    def __init__(
        self,
        dce_endpoint: str,
        dcr_immutable_id: str,
        stream_name: str,
        queue_size: int = 2000,
        queue_size_bytes: int = 25 * (2**20),
    ):
        """
        Initialize the Sentinel connector.

        Args:
            dce_endpoint: Data Collection Endpoint URI
                (e.g., https://dce-xxx.eastus-1.ingest.monitor.azure.com)
            dcr_immutable_id: Data Collection Rule Immutable ID
                (e.g., dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
            stream_name: Stream name defined in the DCR
                (e.g., Custom-ZeroFoxAlertPoller_CL)
            queue_size: Number of events to buffer before flushing
            queue_size_bytes: Maximum size in bytes before splitting requests
        """
        self.dce_endpoint = dce_endpoint
        self.dcr_immutable_id = dcr_immutable_id
        self.stream_name = stream_name
        self.queue_size = queue_size
        self.queue_size_bytes = queue_size_bytes
        self._queue = deque()
        self.lock = asyncio.Lock()
        self.successfull_sent_events_number = 0
        self.failed_sent_events_number = 0

        # Use DefaultAzureCredential which supports:
        # - Managed Identity (in Azure Functions)
        # - Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
        # - Azure CLI credentials (for local development)
        self.credential = DefaultAzureCredential()
        self.client = LogsIngestionClient(
            endpoint=dce_endpoint,
            credential=self.credential
        )

    async def send(self, batch: List[Dict[str, Any]]):
        """
        Add batch to queue and flush if queue is full.

        Args:
            batch: List of log records to send
        """
        self._queue.extend(batch)
        if len(self._queue) >= self.queue_size:
            await self.flush()
            self._queue.clear()

    async def flush(self):
        """Flush all queued events to Azure Monitor."""
        await self._flush(list(self._queue))
        self._queue.clear()

    async def _flush(self, data: List[Dict[str, Any]]):
        """
        Send data to Azure Monitor Logs Ingestion API.

        Args:
            data: List of log records to send
        """
        if not data:
            return

        split_data = self._split_big_request(data)

        for batch in split_data:
            await self._post_data(batch)

    async def _post_data(self, body: List[Dict[str, Any]]):
        """
        Post data using the Logs Ingestion API.

        Args:
            body: List of log records to send
        """
        events_number = len(body)

        try:
            # The SDK is synchronous, wrap in executor for async compatibility
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.upload(
                    rule_id=self.dcr_immutable_id,
                    stream_name=self.stream_name,
                    logs=body
                )
            )

            logging.info(
                f"{events_number} events have been successfully sent to Microsoft Sentinel"
            )
            self.successfull_sent_events_number += events_number

        except HttpResponseError as e:
            logging.error(
                f"Error during sending events to Microsoft Sentinel. "
                f"Status: {e.status_code}, Message: {e.message}"
            )
            self.failed_sent_events_number += events_number
        except Exception as e:
            logging.error(f"Unexpected error sending events: {str(e)}")
            self.failed_sent_events_number += events_number

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - flush remaining events and cleanup."""
        await self.flush()
        self.client.close()

    def _check_size(self, queue: List) -> bool:
        """
        Check if queue is within size limits.

        Args:
            queue: List of log records to check

        Returns:
            True if queue size is within limits
        """
        data_bytes_len = len(json.dumps(queue).encode())
        return data_bytes_len < self.queue_size_bytes

    def _split_big_request(self, queue: List) -> List[List]:
        """
        Split large requests into smaller batches recursively.

        Args:
            queue: List of log records to split

        Returns:
            List of batches, each within size limits
        """
        if self._check_size(queue):
            return [queue]
        else:
            middle = len(queue) // 2
            queues_list = [queue[:middle], queue[middle:]]
            return (
                self._split_big_request(queues_list[0]) +
                self._split_big_request(queues_list[1])
            )
