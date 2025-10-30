import logging
import json
from enum import Enum

from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError


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
                logging.warn(f'Queue {self.queue_name} already exists')

    def send_chunk_info(self, export_job_id, chunk_id):
        with QueueClient.from_connection_string(self.connection_string, self.queue_name,
                                                message_encode_policy=BinaryBase64EncodePolicy(),
                                                message_decode_policy=BinaryBase64DecodePolicy()) as queue_client:
            chunk_info = {'exportJobId': export_job_id, 'chunkId': chunk_id}
            return queue_client.send_message(json.dumps(chunk_info).encode('utf-8'))

class ExportsQueueNames(Enum):
    TenableAssetExportsQueue = 'tenable-asset-export-queue'
    TenableVulnExportsQueue = 'tenable-vuln-export-queue'
    TenableAssetExportsPoisonQueue = 'tenable-asset-export-queue-poison'
    TenableVulnExportsPoisonQueue = 'tenable-vuln-export-queue-poison'
