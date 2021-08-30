import logging

from ..tenable_helper import TenableIO


def main(timestamp: int) -> object:
    logging.info('using pyTenable client to create new asset export job')
    tio = TenableIO()
    logging.info(
        f'requesting a new Asset Export Job from Tenable')
    job_id = tio.exports.assets(updated_at=timestamp)

    logging.info(f'received a response from Asset Export Job request')
    logging.info(job_id)
    return job_id
