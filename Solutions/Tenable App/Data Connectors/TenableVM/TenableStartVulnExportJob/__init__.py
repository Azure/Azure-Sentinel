import logging
import os

from ..tenable_helper import TenableIO

severity = os.environ.get("LowestSeveritytoStore", "")
SEVERITIES = ["info", "low", "medium", "high", "critical"]


def main(timestamp: int) -> object:
    logging.info("using pyTenable client to create new vuln export job")
    tio = TenableIO()
    logging.info("requesting a new Vuln Export Job from Tenable for timestamp: {}".format(timestamp))
    # limiting number of assets to 50. For some bigger containers,
    # each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    if severity and severity.lower() in SEVERITIES:
        logging.info("Selected lowest severity: {}".format(severity))
        logging.info(
            "Fetching vulnerability Data for severity: {}".format(
                SEVERITIES[SEVERITIES.index(severity.lower()):]
            )
        )
        job_id = tio.exports.vulns(
            last_found=timestamp,
            num_assets=50,
            severity=SEVERITIES[SEVERITIES.index(severity.lower()):],
        )
    else:
        logging.warning(
            "Either 'Lowest Severity to Store' parameter is not set or value is not from allowed values"
            "(info,low,medium,high,critical)."
        )
        logging.info(
            "Fetching vulnerability Data for severity {} considering default Info as lowest severity value.".format(
                SEVERITIES
            )
        )
        job_id = tio.exports.vulns(
            last_found=timestamp, num_assets=50, severity=SEVERITIES
        )

    logging.info(f"received a response from Vuln Export Job request{job_id}")
    return job_id
