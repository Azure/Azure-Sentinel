import logging

from ..tenable_helper import TenableIO


def main(timestamp: int) -> object:
    logging.info('using pyTenable client to create new vuln export job')
    tio = TenableIO()
    logging.info(
        f'requesting a new Vuln Export Job from Tenable')
    job_id = tio.exports.vulns(updated_at=timestamp)

    logging.info(f'received a response from Vuln Export Job request')
    logging.info(job_id)
    return job_id
