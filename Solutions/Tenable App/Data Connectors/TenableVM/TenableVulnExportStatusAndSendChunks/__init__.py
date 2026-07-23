"""Vuln Export Status And Send Chunks file."""

import json
import logging
import os
import time

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableIO, TenableStatus, TenableExportType
from tenable.errors import APIError


connection_string = os.environ["AzureWebJobsStorage"]
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value
logs_starts_with = "TenableVM"
function_name = "TenableVulnExportStatusAndSendChunks"
MAX_EXECUTION_TIME = 570


def add_chunks_to_table(exportJobDetails, execution_start_time):
    """
    Add chunks to the table.

    Args:
        exportJobDetails (dict): Job details containing chunks_available, exportJobId, start_time, and status.
        execution_start_time (int): The Unix timestamp of the start time of the execution.
    Returns:
        None
    """
    logging.info(f"{logs_starts_with} {function_name}: Adding chunks to the table.")
    chunks = exportJobDetails.get("chunks_available", [])
    exportJobId = exportJobDetails.get("exportJobId", "")
    start_time = exportJobDetails.get("start_time", 0)
    job_status = exportJobDetails.get("status", "")
    last_chunk_id = None
    if len(chunks) > 0:
        vuln_table = ExportsTableStore(connection_string, vuln_export_table_name)
        update_checkpoint = False
        for chunk in chunks:
            if int(time.time()) >= execution_start_time + MAX_EXECUTION_TIME:
                logging.info(f"{logs_starts_with} {function_name}: 9:30 mins executed hence terminating the function.")
                return
            logging.info(
                f"{logs_starts_with} {function_name}: Function started: {time.time()-execution_start_time} seconds ago"
            )
            chunk_dtls = vuln_table.get(exportJobId, str(chunk))
            if chunk_dtls:
                current_chunk_status = chunk_dtls["jobStatus"]
                logging.warning(
                    f"{logs_starts_with} {function_name}: Avoiding vuln chunk duplicate processing"
                    f" -- {exportJobId} {chunk}. Current status: {current_chunk_status}"
                )
                continue
            if job_status.upper() == "FINISHED":
                last_chunk_id = str(chunk)
            logging.info(f"{logs_starts_with} {function_name}: Chunk added to the table -- {exportJobId} {chunk}")

            vuln_table.merge(
                exportJobId,
                str(chunk),
                {
                    "jobStatus": TenableStatus.queued.value,
                    "startTime": start_time,
                    "updateCheckpoint": update_checkpoint,
                    "jobType": TenableExportType.vuln.value,
                    "ingestTimestamp": time.time(),
                },
            )
        if last_chunk_id:
            vuln_table.merge(
                exportJobId,
                last_chunk_id,
                {
                    "updateCheckpoint": True,
                },
            )
    else:
        logging.info(f"{logs_starts_with} {function_name}: No chunk found to process.")
        return


def main(exportJob: str) -> object:
    """
    Activity function to check vuln export job status and add chunks to the table.

    Args:
        exportJob (str): The export job string containing the vuln job ID and start time.

    Returns:
        object: The job details as a string.
    """
    execution_start_time = time.time()
    jsonExportObject = json.loads(exportJob)
    exportJobId = jsonExportObject.get("vuln_job_id", "")
    start_time = jsonExportObject.get("start_time", 0)
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to check vulnerability export job status")
    logging.info(f"{logs_starts_with} {function_name}: Checking status at vulns/{exportJobId}/status")
    tio = TenableIO()
    try:
        job_details = tio.exports.status("vulns", exportJobId)
    except APIError as e:
        logging.warning(
            f"{logs_starts_with} {function_name}: Failure to retrieve vuln export job status from Tenable."
            f"Export Job ID: {exportJobId}"
        )
        logging.error(
            f"{logs_starts_with} {function_name}: Error in retrieving vuln export job status from Tenable. status code:"
            f" error.code {e.code}, reason: {e.response}"
        )
        raise Exception(
            f"Retrieving vuln export job status from Tenable failed with error code {e.code}, reason: {e.response}"
        )
    logging.info(f"{logs_starts_with} {function_name}: Received a response from vulns/{exportJobId}/status")
    logging.info(f"{logs_starts_with} {function_name}: {job_details}")

    tio_status = ["ERROR", "CANCELLED"]
    if job_details["status"] not in tio_status:
        try:
            job_details["exportJobId"] = exportJobId
            job_details["start_time"] = start_time
            add_chunks_to_table(job_details, execution_start_time)
        except Exception as e:
            logging.warning(f"{logs_starts_with} {function_name}: Error while adding chunks to table")
            logging.warning(f"{logs_starts_with} {function_name}: {job_details}")
            logging.warning(f"{logs_starts_with} {function_name}: Error: {e}")
    else:
        logging.info(f"{logs_starts_with} {function_name}: Vuln export job status: {job_details['status']}")

    return json.dumps(job_details)
