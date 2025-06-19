"""Start Asset Export Job file."""

import logging
import os

from ..tenable_helper import TenableIO
from tenable.errors import APIError
from ..exports_store import (
    ExportsTableStore,
    ExportsTableNames,
    update_chunk_status_for_old_jobs,
)

logs_starts_with = "TenableVM"
function_name = "TenableStartAssetExportJob"
connection_string = os.environ["AzureWebJobsStorage"]
assets_table = ExportsTableStore(connection_string, ExportsTableNames.TenableAssetExportTable.value)


def main(timestamp: int) -> object:
    """
    Create a new asset export job using the pyTenable client.

    Args:
    timestamp (int): The timestamp after which assets should be exported.

    Returns:
    object: The job ID of the created asset export job as a string.
    """
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to create new asset export job")
    update_chunk_status_for_old_jobs(assets_table)
    tio = TenableIO()
    logging.info(
        f"{logs_starts_with} {function_name}: Requesting a new Asset Export Job from Tenable for timestamp={timestamp}"
    )
    # limiting chunk size to contain 100 assets details. For some bigger
    # containers, each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    try:
        job_id = tio.exports.assets(updated_at=timestamp, chunk_size=100, use_iterator=False)
    except APIError as e:
        logging.warning(f"{logs_starts_with} {function_name}: Failure to create a new asset export job.")
        logging.error(
            f"{logs_starts_with} {function_name}: Error in creating asset export job status. status code: error.code {
                e.code}, reason: {
                e.response}"
        )
        raise Exception(
            f"Creating an asset export job from Tenable failed with error code {e.code}, reason: {e.response}"
        )
    logging.info(f"{logs_starts_with} {function_name}: Received a response from Asset Export Job request {job_id}")
    return str(job_id)
