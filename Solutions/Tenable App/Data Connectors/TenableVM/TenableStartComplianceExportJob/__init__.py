"""Activity function to start a new compliance export job."""

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
function_name = "TenableStartComplianceExportJob"
connection_string = os.environ["AzureWebJobsStorage"]
compliance_table = ExportsTableStore(connection_string, ExportsTableNames.TenableComplianceExportTable.value)


def main(timestamp: int) -> str:
    """
    Create a new compliance export job using the pyTenable client.

    Args:
    timestamp (int): The timestamp to filter compliance details.

    Returns:
    str: The job ID of the created compliance export job as a string.
    """
    logging.info(
        f"{logs_starts_with} {function_name}: Using pyTenable client to create new compliance export job"
    )
    update_chunk_status_for_old_jobs(compliance_table)
    tio = TenableIO()
    logging.info(
        f"{logs_starts_with} {function_name}: Requesting a new compliance Export Job from Tenable for timestamp={timestamp}"
    )
    compliance_state = ["OPEN", "REOPENED", "FIXED"]
    try:
        if timestamp == 0:
            logging.info(f"{logs_starts_with} {function_name}: Timestamp is 0. Fetching all compliance details")
            job_id = tio.exports.compliance(use_iterator=False, num_findings=50, state=compliance_state)
        else:
            logging.info(f"{logs_starts_with} {function_name}: Fetching compliance details for timestamp: {timestamp}")
            job_id = tio.exports.compliance(
                use_iterator=False, num_findings=50, indexed_at=timestamp, state=compliance_state
            )
    except APIError as e:
        logging.warning(
            f"{logs_starts_with} {function_name}: Failure to create a new compliance export job."
        )
        logging.error(
            f"{logs_starts_with} {function_name}: Error in creating"
            f" compliance export job status. status code: error.code {e.code}, reason: {e.response}"
        )
        raise Exception(
            f"{logs_starts_with} {function_name}: Creating a compliance"
            f" export job from Tenable failed with error code {e.code}, reason: {e.response}"
        )
    logging.info(
        f"{logs_starts_with} {function_name}: Received a response from compliance Export Job request {job_id}"
    )
    return str(job_id)
