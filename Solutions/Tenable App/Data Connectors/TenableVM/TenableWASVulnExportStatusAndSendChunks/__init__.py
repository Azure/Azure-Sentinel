"""WAS Vulnerability Export Status And Send Chunks file."""

import json
import logging
import os
import time

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import (
    TenableIO,
    TenableStatus,
    TenableExportType,
    update_checkpoint_for_last_chunk,
)
from tenable.errors import APIError

connection_string = os.environ["AzureWebJobsStorage"]
was_vuln_table_name = ExportsTableNames.TenableWASVulnExportTable.value
logs_starts_with = "TenableVM"
function_name = "TenableWASVulnExportStatusAndSendChunks"
MAX_EXECUTION_TIME = 570


def add_chunks_to_table(export_job_details, execution_start_time):
    """
    Add chunks to the table.

    Args:
        export_job_details (dict): Job details containing chunks_available, exportJobId, start_time, and status.
        execution_start_time (int): The Unix timestamp of the start time of the execution.
    Returns:
        None
    """
    logging.info(f"{logs_starts_with} {function_name}: Adding chunks to the table.")
    chunks = export_job_details.get("chunks_available", [])
    export_job_id = export_job_details.get("exportJobId", "")
    start_time = export_job_details.get("start_time", 0)
    job_status = export_job_details.get("status", "")

    if len(chunks) > 0:
        was_vuln_table = ExportsTableStore(connection_string, was_vuln_table_name)
        update_checkpoint = False
        for chunk in chunks:
            if int(time.time()) >= execution_start_time + MAX_EXECUTION_TIME:
                logging.info(f"{logs_starts_with} {function_name}: 9:30 mins executed hence terminating the function.")
                return
            update_checkpoint = update_checkpoint_for_last_chunk(chunk, chunks, job_status)
            chunk_dtls = was_vuln_table.get(export_job_id, str(chunk))
            if chunk_dtls:
                chunk_status = chunk_dtls["jobStatus"]
                logging.info(
                    f"{logs_starts_with} {function_name}: Avoiding was vuln chunk duplicate processing"
                    f" -- {export_job_id} {chunk}. Current status: {chunk_status}"
                )
                continue

            logging.info(f"{logs_starts_with} {function_name}: Chunk added to the table -- {export_job_id} {chunk}")
            was_vuln_table.merge(
                export_job_id,
                str(chunk),
                {
                    "jobStatus": TenableStatus.queued.value,
                    "startTime": start_time,
                    "updateCheckpoint": update_checkpoint,
                    "jobType": TenableExportType.was_vuln.value,
                    "ingestTimestamp": time.time(),
                },
            )
    else:
        logging.info(f"{logs_starts_with} {function_name}: No chunk found to process.")


def main(exportJob: str) -> object:
    """
    Activity function to check was vuln export job status and add chunks to the table.

    Args:
        exportJob (str): The export job string containing the was vuln job ID and start time.

    Returns:
        object: The job details as a dictionary.
    """
    execution_start_time = time.time()
    json_export_object = json.loads(exportJob)
    export_job_id = json_export_object.get("was_vuln_job_id", "")
    start_time = json_export_object.get("start_time", 0)
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to check was vuln export job status")
    logging.info(f"{logs_starts_with} {function_name}: checking status at was/v1/export/vulns/{export_job_id}/status")
    tio = TenableIO()

    try:
        job_details = tio.exports.status("was", export_job_id)
    except APIError as e:
        logging.warning(
            f"{logs_starts_with} {function_name}: Failure to retrieve was vuln export job status from Tenable."
            f"Export Job ID: {export_job_id}"
        )
        logging.error(
            f"Error in retrieving was vuln export job status from Tenable. status code:"
            f" error.code {e.code}, reason: {e.response}"
        )
        raise Exception(
            f"Retrieving was vuln export job status from Tenable failed with error code {e.code}, reason: {e.response}"
        )

    logging.info(
        f"{logs_starts_with} {function_name}: Received a response from was/v1/export/vulns/{export_job_id}/status"
    )
    logging.info(f"{logs_starts_with} {function_name}: {job_details}")

    tio_status = ["ERROR", "CANCELLED"]
    if job_details["status"] not in tio_status:
        try:
            job_details["exportJobId"] = export_job_id
            job_details["start_time"] = start_time
            add_chunks_to_table(job_details, execution_start_time)
        except Exception as e:
            logging.warning(f"{logs_starts_with} {function_name}: Error while adding chunks to table")
            logging.warning(f"{logs_starts_with} {function_name}: {job_details}")
            logging.warning(f"{logs_starts_with} {function_name}: Error: {e}")
    else:
        logging.info(f"{logs_starts_with} {function_name}: WAS vuln export job status: {job_details['status']}")

    return json.dumps(job_details)
