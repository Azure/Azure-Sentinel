"""Vuln DownloadChunk Orchestrator file."""

import json
import logging
import os

import azure.durable_functions as df

from datetime import timedelta
from ..exports_store import (
    ExportsTableStore,
    ExportsTableNames,
    list_tables_in_storage_account,
)

connection_string = os.environ["AzureWebJobsStorage"]
vuln_table_name = ExportsTableNames.TenableVulnExportTable.value
vuln_table = ExportsTableStore(connection_string, vuln_table_name)
download_chunk_schedule_minutes = 1
retry_interval = 5

logs_starts_with = "TenableVM"
function_name = "TenableVulnDownloadChunkOrchestrator"
vuln_download_and_process_chunk_activity_name = "TenableVulnDownloadAndProcessChunks"


def check_table_exist():
    """Check if the vuln table exists in the storage account.

    Returns:
        True if the table exists, False otherwise.
    """
    tables = list_tables_in_storage_account(connection_string)
    for table in tables:
        if table.name == vuln_table_name:
            logging.info(f"{logs_starts_with} {function_name}: {vuln_table_name} table exists.")
            return True
    return False


def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to handle Tenable.io Vuln Export chunks.

    This function is responsible to check if the vulns table exists in the storage account.
    If the table exists, it will query for all queued chunks and call the activity function
    `TenablevulnDownloadAndProcessChunks` to download and process the chunks.
    If there are no more chunks to process, it will go to sleep for 1 minute before checking again.
    If the table does not exist, it will go to sleep for 1 minute before checking again.

    Args:
        context (df.DurableOrchestrationContext): The durable orchestration context

    Returns:
        None
    """
    logging.info(f"{logs_starts_with} {function_name}: Starting execution for TenablevulnDownloadChunkOrchestrator")
    logging.info(
        f"{logs_starts_with} {function_name}: instance id: {context.instance_id} at {context.current_utc_datetime}"
    )
    jobs_with_finished_chunks = {}
    flag = check_table_exist()
    global download_chunk_schedule_minutes
    if not flag:
        logging.info(
            f"{logs_starts_with} {function_name}:{vuln_table_name} table is not created. waiting for next execution."
        )
        next_check = context.current_utc_datetime + timedelta(minutes=download_chunk_schedule_minutes)
        yield context.create_timer(next_check)
        context.continue_as_new(None)
    while True:
        download_chunk_schedule_minutes = 1
        queued_chunks = vuln_table.query_for_all_queued_chunks()
        queued_chunks_list = list(queued_chunks)
        logging.info(f"{logs_starts_with} {function_name}: Number of queued chunks: {len(queued_chunks_list)}")
        if len(queued_chunks_list) == 0:
            logging.info(
                f"{logs_starts_with} {function_name}: No more chunks found to process. Going to sleep for 1 minute..."
            )
            break
        sorted_chunks = sorted(queued_chunks_list, key=lambda e: e["ingestTimestamp"])

        str_activity_data = json.dumps(sorted_chunks)
        status, jobs_with_finished_chunks = yield context.call_activity(
            vuln_download_and_process_chunk_activity_name, str_activity_data
        )
        if not status:
            download_chunk_schedule_minutes = retry_interval
            logging.error(
                f"{logs_starts_with} {function_name}: Activity failed with status code "
                f"401 or 403. Sleeping for {download_chunk_schedule_minutes} minutes...")
            break

        try:
            jobs_with_finished_chunks = json.loads(jobs_with_finished_chunks)
        except json.JSONDecodeError as json_err:
            logging.error(
                f"{logs_starts_with} {function_name}: Error while loading JSON data from activity. Error: {json_err}"
            )
            raise Exception(json_err)
        logging.info(f"{logs_starts_with} {function_name}: Number of finished chunks by job id: {jobs_with_finished_chunks}")

    next_check = context.current_utc_datetime + timedelta(minutes=download_chunk_schedule_minutes)
    yield context.create_timer(next_check)
    context.continue_as_new(None)


main = df.Orchestrator.create(orchestrator_function)
