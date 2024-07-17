import logging

from ..tenable_helper import TenableIO


def main(timestamp: int) -> object:
    logging.info('using pyTenable client to create new vuln export job')
    tio = TenableIO()
    logging.info(
        f'requesting a new Vuln Export Job from Tenable')
    # limiting number of assets to 50. For some bigger containers, 
    # each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    job_id = tio.exports.vulns(last_found=timestamp, num_assets=50)

    logging.info(f'received a response from Vuln Export Job request')
    logging.info(job_id)
    return job_id
