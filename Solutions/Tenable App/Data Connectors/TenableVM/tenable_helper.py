import os
import logging
import json

from tenable.io import TenableIO as BaseIO
from tenable.io.exports.api import ExportsAPI
from enum import Enum
from queue import Queue
from typing import List, Dict

logs_starts_with = "TenableVM"
function_name = "tenable_helper"


class TenableIO(BaseIO):
    def __init__(self, **kwargs):
        """Initializes the TenableIO object with the following parameters
        (default values can be overridden with environment variables):
        - vendor: str (default: "Microsoft")
        - product: str (default: "Azure Sentinel")
        - build: str (default: "3.1.0")
        """
        kwargs["vendor"] = os.getenv("PyTenableUAVendor", "Microsoft")
        kwargs["product"] = os.getenv("PyTenableUAProduct", "Azure Sentinel")
        kwargs["build"] = os.getenv("PyTenableUABuild", "3.1.0")
        super().__init__(**kwargs)

    @property
    def exports(self):
        """
        Gets the Exports API object.

        Returns:
            ExportsAPI: The Exports API object.
        """
        return ExportsAPI(self)


class TenableStatus(Enum):

    # Job Status
    processing = "PROCESSING"
    sent_to_sub_orchestrator = "SENT_TO_SUB_ORCHESTRATOR"
    no_job = "NO_JOB_FOUND"

    # Chunk Status
    queued = "QUEUED"
    expired = "EXPIRED"

    # Status for both chunks and jobs
    finished = "FINISHED"
    failed = "FAILED"


class TenableExportType(Enum):
    asset = "ASSET_EXPORT_JOB"
    vuln = "VULN_EXPORT_JOB"
    compliance = "COMPLIANCE_EXPORT_JOB"
    was_asset = "WAS_ASSET_EXPORT_JOB"
    was_vuln = "WAS_VULN_EXPORT_JOB"


class TenableChunkPartitioner:
    KB = 1024
    MB = KB * KB
    MAX_UPLOAD_SIZE = 30 * MB
    MAX_REQUEST_HEADERS_OVERHEAD = 2 * MB

    @staticmethod
    def partition_chunks_into_30mb_sub_chunks(input_chunk: List[Dict]) -> List[List[Dict]]:
        """
        This method divides export chunks received from Tenable.io response, into multiple sub-chunks
        such that each sub-chunk is <= 30MB.

        This is necessary as per
        https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api#data-limits.

        Parameters:
            input_chunk (List[Dict]): List containing vuln/assets/compliance objects in chunk.

        Returns:
            List[List[Dict]] -> List containing one or more sub-chunks created out of input chunk.
        """
        queue = Queue()
        output_sub_chunks = []

        queue.put_nowait(input_chunk)

        while queue.qsize() > 0:
            sub_chunk = queue.get_nowait()
            sub_chunk_size = len(json.dumps(sub_chunk))
            sub_chunk_length = len(sub_chunk)

            logging.info(
                f"{logs_starts_with} {function_name}: Fetched sub-chunk from queue with"
                f" {sub_chunk_length} elements & {sub_chunk_size} size(in bytes)"
            )

            request_size = sub_chunk_size + TenableChunkPartitioner.MAX_REQUEST_HEADERS_OVERHEAD
            if request_size <= TenableChunkPartitioner.MAX_UPLOAD_SIZE:
                output_sub_chunks.append(sub_chunk)

                logging.info(
                    f"{logs_starts_with} {function_name}: Added sub-chunk {sub_chunk_length}"
                    f" elements & {sub_chunk_size} size(in bytes) to list of output chunks."
                )
            else:
                divider_index = int(sub_chunk_length / 2)
                left_chunk = sub_chunk[:divider_index]
                right_chunk = sub_chunk[divider_index:]

                queue.put_nowait(left_chunk)
                queue.put_nowait(right_chunk)

                logging.info(
                    f"{logs_starts_with} {function_name}: Re-enqueued 2 sub-chunks with elements: {
                        len(left_chunk)} <-> {
                        len(right_chunk)}"
                )

        logging.info(f"{logs_starts_with} {function_name}: Created {len(output_sub_chunks)} output sub-chunks.")

        return output_sub_chunks
