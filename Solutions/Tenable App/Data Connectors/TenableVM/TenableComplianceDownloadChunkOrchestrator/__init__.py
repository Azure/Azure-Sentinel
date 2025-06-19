"""Compliance DownloadChunk Orchestrator file."""

import json
import logging
import os

import azure.durable_functions as df

from datetime import timedelta
from ..exports_store import (
    ExportsTableStore,
    ExportsTableNames,
)

connection_string = os.environ["AzureWebJobsStorage"]
compliance_table_name = ExportsTableNames.TenableComplianceExportTable.value
compliance_table = ExportsTableStore(connection_string, compliance_table_name)
download_chunk_schedule_minutes = 1

logs_starts_with = "TenableVM"
function_name = "TenableComplianceDownloadChunkOrchestrator"
compliance_download_and_process_chunk_activity_name = "TenableComplianceDownloadAndProcessChunks"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to handle Tenable.io Compliance Export chunks.

    This function is responsible to check if the compliance table exists in the storage account.
    If the table exists, it will query for all queued chunks and call the activity function
    `TenableComplianceDownloadAndProcessChunks` to download and process the chunks.
    If there are no more chunks to process, it will go to sleep for 1 minute before checking again.
    If the table does not exist, it will go to sleep for 1 minute before checking again.

    Args:
        context (df.DurableOrchestrationContext): The durable orchestration context

    Returns:
        None
    """
    logging.info(
        f"{logs_starts_with} {function_name}: Starting execution for TenableComplianceDownloadChunkOrchestrator"
    )
    logging.info(
        f"{logs_starts_with} {function_name}: instance id: {context.instance_id} at {context.current_utc_datetime}"
    )
    jobs_with_finished_chunks = {}

    download_chunk_schedule_minutes = 1
    status, jobs_with_finished_chunks = yield context.call_activity(
        compliance_download_and_process_chunk_activity_name
    )
    logging.info(f"{logs_starts_with} {function_name}: Activity status: {status}")
    logging.info(f"{logs_starts_with} {function_name}: Jobs with finished chunks: {jobs_with_finished_chunks}")
    if jobs_with_finished_chunks:
        try:
            jobs_with_finished_chunks = json.loads(jobs_with_finished_chunks)
        except json.JSONDecodeError as json_err:
            logging.error(
                f"{logs_starts_with} {function_name}: Error while loading JSON data from activity. Error: {json_err}"
            )
            raise Exception(json_err)
        logging.info(f"{logs_starts_with} {function_name}: Number of finished chunks by job id: {jobs_with_finished_chunks}")
    if not status:
        logging.error(
            f"{logs_starts_with} {function_name}: Activity failed with status code "
            f"401 or 403. Sleeping for {download_chunk_schedule_minutes} minutes...")

    next_check = context.current_utc_datetime + timedelta(minutes=download_chunk_schedule_minutes)
    logging.info(f"{logs_starts_with} {function_name}: Will check next at time: {next_check}")
    yield context.create_timer(next_check)
    yield context.continue_as_new(None)


main = df.Orchestrator.create(orchestrator_function)
