import logging
import os

from ..tenable_helper import TenableIO
from tenable.errors import APIError
from ..exports_store import (
    ExportsTableStore,
    ExportsTableNames,
    update_chunk_status_for_old_jobs
)

severity = os.environ.get("LowestSeveritytoStoreWAS", "INFO")
SEVERITIES = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

logs_starts_with = "TenableVM"
function_name = "TenableStartWASVulnExportJob"
connection_string = os.environ["AzureWebJobsStorage"]
was_vulns_table = ExportsTableStore(connection_string, ExportsTableNames.TenableWASVulnExportTable.value)


def main(timestamp: int) -> str:
    """
    Create a new WAS Vuln export job using the pyTenable client.

    Args:
    timestamp (int): The timestamp after which assets should be exported.

    Returns:
    object: The job ID of the created asset export job as a string.
    """
    logging.info(f"{logs_starts_with} {function_name}: Using pyTenable client to create new WAS vuln export job")
    update_chunk_status_for_old_jobs(was_vulns_table)
    tio = TenableIO()
    logging.info(
        f"{logs_starts_with} {function_name}: Requesting a new WAS Vuln Export Job from Tenable for timestamp: {timestamp}"
    )
    # limiting number of assets to 50. For some bigger containers,
    # each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    if severity and severity.upper() in SEVERITIES:
        logging.info(f"{logs_starts_with} {function_name}: Selected lowest severity: {severity}")
        logging.info(
            f"{logs_starts_with} {function_name}: Fetching WAS vulnerability Data for severity: {
                SEVERITIES[
                    SEVERITIES.index(
                        severity.upper()):]}"
        )
        try:
            job_id = tio.exports.was(
                use_iterator=False,
                num_assets=50,
                indexed_at=timestamp,
                severity=SEVERITIES[SEVERITIES.index(severity.upper()):],
                state=["OPEN", "REOPENED", "FIXED"],
            )
        except APIError as e:
            logging.warning(f"{logs_starts_with} {function_name}: Failure to create a new WAS vuln export job.")
            logging.error(
                f"{logs_starts_with} {function_name}: Error in creating WAS vuln export job status. status code: error.code {
                    e.code}, reason: {
                    e.response}"
            )
            raise Exception(
                f"{logs_starts_with} {function_name}: Creating an WAS vuln export job from Tenable failed with error code"
                f"{e.code}, reason: {e.response}"
            )
    else:
        logging.warning(
            f"{logs_starts_with} {function_name}: Either 'Lowest Severity to Store' parameter is not set or value is not from allowed"
            " values (info,low,medium,high,critical)."
        )
        logging.info(
            f"{logs_starts_with} {function_name}: Fetching WAS vulnerability Data for severity {SEVERITIES} "
            "considering default Info as lowest severity value."
        )
        try:
            job_id = tio.exports.was(
                use_iterator=False,
                num_assets=50,
                indexed_at=timestamp,
                severity=SEVERITIES,
                state=["OPEN", "REOPENED", "FIXED"],
            )
        except APIError as e:
            logging.warning(f"{logs_starts_with} {function_name}: Failure to create a new WAS vuln export job.")
            logging.error(
                f"{logs_starts_with} {function_name}: Error in creating WAS vuln export job status. status code: error.code {
                    e.code}, reason: {
                    e.response}"
            )
            raise Exception(
                f"{logs_starts_with} {function_name}: Creating an WAS vuln export job from Tenable failed with error code {
                    e.code}, reason: {
                    e.response}"
            )

    logging.info(f"{logs_starts_with} {function_name}: Received a response from WAS Vuln Export Job request {job_id}")
    return str(job_id)
