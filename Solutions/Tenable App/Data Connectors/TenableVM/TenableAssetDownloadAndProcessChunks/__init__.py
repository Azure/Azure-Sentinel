"""Asset DownloadChunk Activity file."""

import json
import logging
import os

from ..exports_store import (
    ExportsTableStore,
    ExportsTableNames,
)
from ..azure_sentinel import MicrosoftSentinel
from ..tenable_helper import TenableIO, TenableStatus, TenableChunkPartitioner
from tenable.errors import APIError
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
import time

connection_string = os.environ["AzureWebJobsStorage"]
assets_table_name = ExportsTableNames.TenableAssetExportTable.value
checkpoint_table_name = ExportsTableNames.TenableExportCheckpointTable.value
azure_data_collection_endpoint = os.environ["AZURE_DATA_COLLECTION_ENDPOINT"]
dcr_rule_id = os.environ["AZURE_DATA_COLLECTION_RULE_ID_MAIN_TABLES"]
scope = os.environ["SCOPE"]
log_type = os.getenv("AssetTableName", "Tenable_VM_Asset")
logs_starts_with = "TenableVM"
function_name = "TenableAssetDownloadAndProcessChunks"
assets_table = ExportsTableStore(connection_string, assets_table_name)
MAX_EXECUTION_TIME = 570


def download_chunk_details(job_id, chunk_id):
    """
    Download the specified chunk from the TenableIO API using the pyTenable client.

    Returns the chunk data. If the download fails, the function will retry up to 3 times
    before giving up. If the download is successful, the function will return True and the
    chunk data. If the download fails and the error code indicates a 401, 403, or other
    non-retriable error, the function will return False and None. If the download fails
    and the error code indicates a retryable error (429 or 400), the function will retry
    after a brief delay.

    If the download is retried due to a retryable error, the function will log a message
    indicating the error code and the retry delay. If the download fails after all retries
    have been exhausted, the function will log a message indicating the error code and
    update the assets table to indicate that the chunk has failed.

    Parameters
    ----------
    job_id : str
        The ID of the export job that the chunk belongs to
    chunk_id : str
        The ID of the chunk to download

    Returns
    -------
    tuple
        A tuple containing a boolean indicating whether the download was successful
        (True or False), and the chunk data (or None if the download failed)
    """
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to download asset export job chunk")
    logging.info(f"{logs_starts_with} {function_name}: Downloading chunk at assets/exports/{job_id}/chunks/{chunk_id}")
    tio = TenableIO()
    retries = 3
    status_code = None
    while retries > 0:
        try:
            chunk = tio.exports.download_chunk("assets", job_id, chunk_id)
            logging.info(
                f"{logs_starts_with} {function_name}:Received a response from assets/{job_id}/chunks/{chunk_id}"
            )
            return True, chunk
        except APIError as e:
            status_code = e.code
            if status_code in [401, 403]:
                logging.info(
                    f"{logs_starts_with} {function_name}: Failed to retrive asset chunk data. Error code {status_code}"
                )
                return False, None
            elif status_code in [429, 400]:
                if e.response.headers.get("retry-after"):
                    sleep_time = max(180, int(e.response.headers["retry-after"]))
                    logging.info(
                        f"{logs_starts_with} {function_name}: Received a {status_code} error."
                        f" Retrying in {sleep_time} seconds."
                    )
                    time.sleep(sleep_time)
                else:
                    logging.info(
                        f"{logs_starts_with} {function_name}: Received a {status_code} error."
                        " Retrying after 60 seconds."
                    )
                    time.sleep(60)
                retries -= 1
            else:
                logging.warning(
                    f"{logs_starts_with} {function_name}: Failure to retrieve asset data from Tenable."
                    f" Export Job ID: {job_id} Chunk ID: {chunk_id}. Error code {status_code}"
                )
                assets_table.update_if_found(
                    job_id,
                    str(chunk_id),
                    {
                        "jobStatus": TenableStatus.failed.value,
                        "tenableFailedRequestStatusCode": status_code,
                    },
                )
                return True, None
    logging.warning(
        f"{logs_starts_with} {function_name}: Failure to retrieve asset data from Tenable."
        f" Export Job ID: {job_id} Chunk ID: {chunk_id}"
    )
    assets_table.update_if_found(
        job_id,
        str(chunk_id),
        {
            "jobStatus": TenableStatus.failed.value,
            "tenableFailedRequestStatusCode": status_code,
        },
    )
    return True, None


def send_chunk_details_to_sentinel(job_id, chunk_id, chunk, execution_start_time):
    """
    Send a chunk of data from a Tenable asset export job to Azure Sentinel.

    This function sends the data for ingestion into the Log Analytics workspace.

    Args:
        job_id (str): The ID of the export job.
        chunk_id (str): The ID of the chunk.
        chunk (list): The list of asset data.
        execution_start_time (int): The Unix timestamp of the start time of the execution.
    """
    try:
        if len(chunk) == 0:
            logging.info(
                f"{logs_starts_with} {function_name}:No data found in chunk, chunk_id: {chunk_id}, job_id: {job_id}"
            )
        else:
            # limiting individual chunk uploaded to sentinel to be < 30 MB size.
            sub_chunks = TenableChunkPartitioner.partition_chunks_into_30mb_sub_chunks(chunk)

            for sub_chunk in sub_chunks:
                if int(time.time()) >= execution_start_time + MAX_EXECUTION_TIME:
                    logging.info(
                        f"{logs_starts_with} {function_name}: 9:30 mins executed hence terminating the function."
                    )
                    return False

                logging.info(
                    f"{logs_starts_with} {function_name}:Uploading sub-chunk with size: %d",
                    len(json.dumps(sub_chunk)),
                )

                if ".us" in scope:
                    creds = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
                else:
                    creds = DefaultAzureCredential()
                azure_client = LogsIngestionClient(azure_data_collection_endpoint, credential=creds, credential_scopes=[scope])
                ms_sentinel_obj = MicrosoftSentinel(azure_client)
                # Send to Azure Sentinel here
                ms_sentinel_obj.post_data(sub_chunk, log_type, dcr_rule_id)

                logging.info(
                    f"{logs_starts_with} {function_name}: Posted {len(sub_chunk)} data into log analytics"
                    f" workspace table {log_type}."
                )

        assets_table.update_if_found(job_id, str(chunk_id), {"jobStatus": TenableStatus.finished.value})
        return True
    except Exception as e:
        assets_table.update_if_found(
            job_id,
            str(chunk_id),
            {"jobStatus": TenableStatus.failed.value},
        )
        logging.error(f"{logs_starts_with} {function_name}: Error occurred while posting chunk data to Sentinel. {e}")
        return False


def update_chunk_count_for_job(chunk, jobs_with_finished_chunks, job_id):
    """
    Update the count of chunks finished for a given job_id.

    Args:
        chunk (dict): A dictionary containing the PartitionKey and RowKey of the chunk.
        jobs_with_finished_chunks (dict): A dictionary where the keys are the job_id and
            the values are the number of chunks finished for that job.
        job_id (str): The ID of the job to update the count for.
    """
    if chunk.get("PartitionKey") not in jobs_with_finished_chunks:
        jobs_with_finished_chunks[job_id] = 1
    else:
        jobs_with_finished_chunks[job_id] += 1


def main(sortedChunks: str):
    """
    Download and Ingest Chunks data into log analytics workspace in MS Sentinel.

    This function takes sorted Chunks, Download it's data and ingest into log analytics workspace.

    Args:
        sortedChunks (str): A JSON string containing a sorted list of chunks.

    Returns:
        A JSON string containing the number of chunks processed per job id.
    """
    execution_start_time = time.time()
    chunk_ids_data = json.loads(sortedChunks)
    jobs_with_finished_chunks = {}
    previous_job_id = None
    status = True
    for chunk in chunk_ids_data:
        if int(time.time()) >= execution_start_time + MAX_EXECUTION_TIME:
            logging.info(f"{logs_starts_with} {function_name}: 9:30 mins executed hence terminating the function.")
            break
        job_id = chunk.get("PartitionKey")
        chunk_id = chunk.get("RowKey")
        start_time = chunk.get("startTime")
        update_checkpoint = chunk.get("updateCheckpoint")
        status, chunk_data = download_chunk_details(job_id, chunk_id)
        if not status:
            logging.info(
                f"{logs_starts_with} {function_name}: Failure to retrieve asset data from Tenable."
                " Returning to orchestrator."
            )
            return status, json.dumps(jobs_with_finished_chunks)
        if update_checkpoint:
            logging.info(f"{logs_starts_with} {function_name}: Updating Assets checkpoint to value: {start_time}")
            checkpoint_table = ExportsTableStore(connection_string, checkpoint_table_name)
            checkpoint_table.merge("assets", "timestamp", {"assets_timestamp": start_time})
        if chunk_data is None:
            logging.info(
                f"{logs_starts_with} {function_name}: Not able to download data for the chunk : {chunk_id} Continuing to next chunk."
            )
            continue
        elif len(chunk_data) == 0:
            logging.info(
                f"{logs_starts_with} {function_name}: No chunk data found for chunk: {chunk_id}"
                " Continuing to next chunk."
            )
            assets_table.update_if_found(job_id, str(chunk_id), {"jobStatus": TenableStatus.finished.value})
            continue
        update_count = send_chunk_details_to_sentinel(job_id, chunk_id, chunk_data, execution_start_time)
        if previous_job_id is not None and job_id != previous_job_id:
            logging.info(
                f"{logs_starts_with} {function_name}: Completed downloading and processing of "
                f"{jobs_with_finished_chunks[previous_job_id]} chunks for job id: {previous_job_id}"
            )
            previous_job_id = job_id
        if not update_count:
            continue
        update_chunk_count_for_job(chunk, jobs_with_finished_chunks, job_id)
    logging.info(
        f"{logs_starts_with} {function_name}: Completed downloading and processing of"
        f" chunks available in {assets_table_name} table."
    )

    return status, json.dumps(jobs_with_finished_chunks)
