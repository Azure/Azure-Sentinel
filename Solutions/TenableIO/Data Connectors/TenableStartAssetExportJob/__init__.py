import logging

from ..tenable_helper import TenableIO


def main(timestamp: int) -> object:
    logging.info('using pyTenable client to create new asset export job')
    tio = TenableIO()
    logging.info(
        f'requesting a new Asset Export Job from Tenable')
    # limiting chunk size to contain 100 assets details. For some bigger
    # containers, each chunk is reported to be some hundreds of MBs resulting
    # into azure function crash due to OOM errors.
    job_id = tio.exports.assets(updated_at=timestamp, chunk_size=100)

    logging.info(f'received a response from Asset Export Job request')
    logging.info(job_id)
    return job_id
