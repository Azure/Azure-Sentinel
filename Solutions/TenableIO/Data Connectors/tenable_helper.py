import os
import logging
import json

from tenable.io import TenableIO as BaseIO
from tenable.io.exports import ExportsAPI
from enum import Enum
from queue import Queue
from typing import List, Dict


class ExportsAPIExtended(ExportsAPI):
    def vulns(self, **kwargs) -> str:
        return super().vulns(**kwargs).uuid

    def assets(self, **kwargs) -> str:
        return super().assets(**kwargs).uuid

    def status(self, export_type: str, uuid: str) -> dict:
        return self._api.get(
            f'{export_type}/export/{uuid}/status'
        ).json()

    def chunk(self, export_type: str, uuid: str, chunk: int) -> list:
        return self._api.get(
            f'{export_type}/export/{uuid}/chunks/{chunk}'
        ).json()


class TenableIO(BaseIO):
    def __init__(self, **kwargs):
        kwargs['vendor'] = os.getenv('PyTenableUAVendor', 'Microsoft')
        kwargs['product'] = os.getenv('PyTenableUAProduct', 'Azure Sentinel')
        kwargs['build'] = os.getenv('PyTenableUABuild', '0.0.1')
        super().__init__(**kwargs)

    @property
    def exports(self):
        return ExportsAPIExtended(self)


class TenableStatus(Enum):
    finished = 'FINISHED'
    failed = 'FAILED'
    no_job = 'NO_JOB_FOUND'
    processing = 'PROCESSING'
    sending_to_queue = 'SENDING_TO_QUEUE'
    sent_to_queue = 'SENT_TO_QUEUE'
    sent_to_queue_failed = 'SENT_TO_QUEUE_FAILED'
    sent_to_sub_orchestrator = 'SENT_TO_SUB_ORCHESTRATOR'

class TenableExportType(Enum):
    asset = 'ASSET_EXPORT_JOB'
    vuln = 'VULN_EXPORT_JOB'


class TenableChunkPartitioner:
    KB = 1024
    MB = KB * KB
    MAX_UPLOAD_SIZE = 30 * MB
    MAX_REQUEST_HEADERS_OVERHEAD = 2 * MB

    @staticmethod
    def partition_chunks_into_30MB_sub_chunks(inputChunk: List[Dict]) -> List[List[Dict]]:
        '''
        This method divides export chunks received from Tenable.io response, into multiple sub-chunks
        such that each sub-chunk is <= 30MB.
        
        This is necessary as per
        https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api#data-limits.

        Parameters:
            inputChunk (List[Dict]): List containing vuln/assets objects in chunk.

        Returns:
            List[List[Dict]] -> List containing one or more sub-chunks created out of input chunk.
        '''
        queue = Queue()
        output_sub_chunks = []

        queue.put_nowait(inputChunk)

        while queue.qsize() > 0:
            sub_chunk = queue.get_nowait()
            sub_chunk_size = len(json.dumps(sub_chunk))
            sub_chunk_length = len(sub_chunk)

            logging.info(
                'Fetched sub-chunk from queue with %d elements & %d size(in bytes)',
                sub_chunk_length, sub_chunk_size
            )

            request_size = sub_chunk_size + TenableChunkPartitioner.MAX_REQUEST_HEADERS_OVERHEAD
            if request_size <= TenableChunkPartitioner.MAX_UPLOAD_SIZE:
                output_sub_chunks.append(sub_chunk)

                logging.info(
                    'Added sub-chunk %d elements & %d size(in bytes) to list of output chunks.',
                    sub_chunk_length,
                    sub_chunk_size
                )
            else:
                divider_index = int(sub_chunk_length / 2)
                left_chunk = sub_chunk[:divider_index]
                right_chunk = sub_chunk[divider_index:]

                queue.put_nowait(left_chunk)
                queue.put_nowait(right_chunk)

                logging.info('Re-enqueued 2 sub-chunks with elements: %d <-> %d', len(left_chunk), len(right_chunk))

        logging.info('Created %d output sub-chunks.', len(output_sub_chunks))

        return output_sub_chunks
