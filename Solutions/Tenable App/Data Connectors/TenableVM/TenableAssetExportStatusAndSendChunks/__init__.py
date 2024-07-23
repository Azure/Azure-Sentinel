import logging
import os

from ..exports_queue import ExportsQueue, ExportsQueueNames
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableIO, TenableStatus, TenableExportType

connection_string = os.environ['AzureWebJobsStorage']
assets_table_name = ExportsTableNames.TenableAssetExportTable.value
assets_queue_name = ExportsQueueNames.TenableAssetExportsQueue.value


def send_chunks_to_queue(exportJobDetails):
    logging.info(f'Sending chunk to queue.')
    chunks = exportJobDetails.get('chunks_available', [])
    exportJobId = exportJobDetails.get('exportJobId', '')

    if len(chunks) > 0:
        assets_table = ExportsTableStore(connection_string, assets_table_name)
        for chunk in chunks:
            chunk_dtls = assets_table.get(exportJobId, str(chunk))
            if chunk_dtls:
                current_chunk_status = chunk_dtls['jobStatus']
                if (
                        current_chunk_status == TenableStatus.sent_to_queue.value or
                        current_chunk_status == TenableStatus.finished.value
                ):
                    logging.warning(f'Avoiding asset chunk duplicate processing -- {exportJobId} {chunk}. Current status: {current_chunk_status}')
                    continue

            assets_table.merge(exportJobId, str(chunk), {
                'jobStatus': TenableStatus.sending_to_queue.value,
                'jobType': TenableExportType.asset.value
            })

            assets_queue = ExportsQueue(connection_string, assets_queue_name)
            try:
                sent = assets_queue.send_chunk_info(exportJobId, chunk)
                logging.warn(f'chunk queued -- {exportJobId} {chunk}')
                logging.warn(sent)
                assets_table.merge(exportJobId, str(chunk), {
                    'jobStatus': TenableStatus.sent_to_queue.value
                })
            except Exception as e:
                logging.warn(
                    f'Failed to send {exportJobId} - {chunk} to be processed')
                logging.warn(e)

                assets_table.merge(exportJobId, str(chunk), {
                    'jobStatus': TenableStatus.sent_to_queue_failed.value,
                    'jobType': TenableExportType.asset.value
                })
    else:
        logging.info('no chunk found to process.')
        return


def main(exportJobId: str) -> object:
    logging.info('using pyTenable client to check asset export job status')
    logging.info(
        f'checking status at assets/{exportJobId}/status')
    tio = TenableIO()
    job_details = tio.exports.status('assets', exportJobId)
    logging.info(
        f'received a response from assets/{exportJobId}/status')
    logging.info(job_details)

    tio_status = ['ERROR', 'CANCELLED']
    if job_details['status'] not in tio_status:
        try:
            job_details['exportJobId'] = exportJobId
            send_chunks_to_queue(job_details)
        except Exception as e:
            logging.warn('error while sending chunks to queue')
            logging.warn(job_details)
            logging.warn(e)

    return job_details
