"""Start WAS Asset Export Job file."""

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
function_name = "TenableStartWASAssetExportJob"
connection_string = os.environ["AzureWebJobsStorage"]
was_assets_table = ExportsTableStore(connection_string, ExportsTableNames.TenableWASAssetExportTable.value)


def main(timestamp: int) -> str:
    """
    Create a new WAS asset export job using the pyTenable client.

    Args:
    timestamp (int): The timestamp after which WAS assets should be exported.

    Returns:
    str: The job ID of the created WAS asset export job as a string.
    """
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to create new WAS asset export job")
    update_chunk_status_for_old_jobs(was_assets_table)
    tio = TenableIO()
    logging.info(
        f"{logs_starts_with} {function_name}: Requesting a new wAS Asset Export Job from Tenable for timestamp={timestamp}"
    )
    try:
        job_id = tio.exports.assets_v2(updated_at=timestamp, chunk_size=100, use_iterator=False, types=["webapp"])
    except APIError as e:
        logging.warning(f"{logs_starts_with} {function_name}: Failure to create a new WAS asset export job.")
        logging.error(
            f"{logs_starts_with} {function_name}: Error in creating WAS asset export job status. status code: error.code {
                e.code}, reason: {
                e.response}"
        )
        raise Exception(
            f"{logs_starts_with} {function_name}: Creating an WAS asset export job from Tenable failed with error code {
                e.code}, reason: {
                e.response}"
        )
    logging.info(f"{logs_starts_with} {function_name}: Received a response from WAS Asset Export Job request {job_id}")
    return str(job_id)
