"""Activity function to start a new compliance export job."""

import logging

from ..tenable_helper import TenableIO


def main(timestamp: int) -> object:
    """
    Create a new compliance export job using the pyTenable client.

    Args:
    timestamp (int): The timestamp to filter compliance details.

    Returns:
    object: The job ID of the created compliance export job as a string.
    """
    logging.info("using pyTenable client to create new compliance export job")
    tio = TenableIO()
    logging.info("requesting a new Compliance Export Job from Tenable")
    # limiting chunk size to contain 100 compliance details. For some bigger
    # containers, each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    if timestamp == 0:
        logging.info("Timestamp is 0. Fetching all compliance details")
        job_id = tio.exports.compliance(use_iterator=False, num_findings=100)
    else:
        logging.info("Fetching compliance details for timestamp: {}".format(timestamp))
        job_id = tio.exports.compliance(
            use_iterator=False, num_findings=100, indexed_at=timestamp
        )

    logging.info(
        "received a response from Compliance Export Job request. job_id = {}".format(
            job_id
        )
    )
    return str(job_id)
