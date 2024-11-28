import logging
import json
from enum import Enum

from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy
from azure.core.exceptions import ResourceExistsError


class ExportsQueue:
    def __init__(self, connection_string, queue_name):
        self.connection_string = connection_string
        self.queue_name = queue_name

    def create(self):
        with QueueClient.from_connection_string(self.connection_string, self.queue_name,
                                                message_encode_policy=BinaryBase64EncodePolicy(),
                                                message_decode_policy=BinaryBase64DecodePolicy()) as queue_client:
            try:
                queue_client.create_queue()
            except ResourceExistsError:
                logging.warning(f"Queue {self.queue_name} already exists")

    def send_chunk_info(self, export_job_id, chunk_id, start_time, update_checkpoint=False):
        with QueueClient.from_connection_string(self.connection_string, self.queue_name,
                                                message_encode_policy=BinaryBase64EncodePolicy(),
                                                message_decode_policy=BinaryBase64DecodePolicy()) as queue_client:
            chunk_info = {"exportJobId": export_job_id, "chunkId": chunk_id, "startTime": start_time, "updateCheckpoint": update_checkpoint}
            return queue_client.send_message(json.dumps(chunk_info).encode("utf-8"))

class ExportsQueueNames(Enum):
    TenableAssetExportsQueue = "tenable-asset-export-queue"
    TenableVulnExportsQueue = "tenable-vuln-export-queue"
    TenableComplianceExportsQueue = "tenable-compliance-export-queue"
    TenableAssetExportsPoisonQueue = "tenable-asset-export-queue-poison"
    TenableVulnExportsPoisonQueue = "tenable-vuln-export-queue-poison"
    TenableComplianceExportsPoisonQueue = "tenable-compliance-export-queue-poison"
