"""Start Vuln Export Job file."""

import logging
import os

from ..tenable_helper import TenableIO
from tenable.errors import APIError
from ..exports_store import (
    ExportsTableStore,
    ExportsTableNames,
    update_chunk_status_for_old_jobs,
)
severity = os.environ.get("LowestSeveritytoStore", "")
SEVERITIES = ["info", "low", "medium", "high", "critical"]

logs_starts_with = "TenableVM"
function_name = "TenableStartVulnExportJob"
connection_string = os.environ["AzureWebJobsStorage"]
vulns_table = ExportsTableStore(connection_string, ExportsTableNames.TenableVulnExportTable.value)


def main(timestamp: int) -> object:
    """
    Create a new vuln export job using the pyTenable client.

    Args:
    timestamp (int): The timestamp after which vuln should be exported.

    Returns:
    object: The job ID of the created vuln export job as a string.
    """
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to create new vuln export job")
    update_chunk_status_for_old_jobs(vulns_table)
    tio = TenableIO()
    logging.info(
        f"{logs_starts_with} {function_name}: Requesting a new Vuln Export Job from Tenable for timestamp: {timestamp}"
    )
    # limiting number of assets to 500. For some bigger containers,
    # each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    if severity and severity.lower() in SEVERITIES:
        logging.info("Selected lowest severity: {}".format(severity))
        logging.info(
            "Fetching vulnerability Data for severity: {}".format(SEVERITIES[SEVERITIES.index(severity.lower()):])
        )
        try:
            job_id = tio.exports.vulns(
                last_found=timestamp,
                num_assets=50,
                severity=SEVERITIES[SEVERITIES.index(severity.lower()):],
                use_iterator=False,
                state=["FIXED", "OPEN", "REOPENED"],
            )
        except APIError as e:
            logging.warning(f"{logs_starts_with} {function_name}: Failure to create a new vuln export job.")
            logging.error(
                f"{logs_starts_with} {function_name}: Error in creating vuln export job status. status code: error.code {
                    e.code}, reason: {
                    e.response}"
            )
            raise Exception(
                f"{logs_starts_with} {function_name}: Creating an vuln export job from Tenable failed with error code {
                    e.code}, reason: {
                    e.response}"
            )
    else:
        logging.warning(
            f"{logs_starts_with} {function_name}: Either 'Lowest Severity to Store' parameter is not set or value is not from allowed"
            " values (info,low,medium,high,critical)."
        )
        logging.info(
            f"{logs_starts_with} {function_name}: Fetching vulnerability Data for severity {SEVERITIES}"
            " considering default Info as lowest severity value."
        )
        try:
            job_id = tio.exports.vulns(
                last_found=timestamp,
                num_assets=50,
                severity=SEVERITIES,
                use_iterator=False,
                state=["FIXED", "OPEN", "REOPENED"],
            )
        except APIError as e:
            logging.warning(f"{logs_starts_with} {function_name}: Failure to create a new vuln export job.")
            logging.error(
                f"{logs_starts_with} {function_name}: Error in creating vuln export job status. status code: error.code {
                    e.code}, reason: {
                    e.response}"
            )
            raise Exception(
                f"{logs_starts_with} {function_name}: Creating an vuln export job from Tenable failed with error code {
                    e.code}, reason: {
                    e.response}"
            )

    logging.info(f"{logs_starts_with} {function_name}: Received a response from Vuln Export Job request {job_id}")
    return str(job_id)
