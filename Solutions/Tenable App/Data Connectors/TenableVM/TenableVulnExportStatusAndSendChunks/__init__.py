import logging
import os

from ..exports_queue import ExportsQueue, ExportsQueueNames
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableIO, TenableStatus, TenableExportType

# from tenable.io import TenableIO

connection_string = os.environ['AzureWebJobsStorage']
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value
vuln_queue_name = ExportsQueueNames.TenableVulnExportsQueue.value


def send_chunks_to_queue(exportJobDetails):
    logging.info(f'Sending chunk to queue.')
    chunks = exportJobDetails.get('chunks_available', [])
    exportJobId = exportJobDetails.get('exportJobId', '')

    if len(chunks) > 0:
        vuln_table = ExportsTableStore(
            connection_string, vuln_export_table_name)
        for chunk in chunks:
            chunk_dtls = vuln_table.get(exportJobId, str(chunk))
            if chunk_dtls:
                current_chunk_status = chunk_dtls['jobStatus']
                if (
                        current_chunk_status == TenableStatus.sent_to_queue.value or
                        current_chunk_status == TenableStatus.finished.value
                ):
                    logging.warning(
                        f'Avoiding vuln chunk duplicate processing -- {exportJobId} {chunk}. Current status: {current_chunk_status}')
                    continue

            vuln_table.post(exportJobId, str(chunk), {
                'jobStatus': TenableStatus.sending_to_queue.value,
                'jobType': TenableExportType.vuln.value
            })

            vuln_queue = ExportsQueue(connection_string, vuln_queue_name)

            try:
                sent = vuln_queue.send_chunk_info(exportJobId, chunk)
                logging.warn(f'chunk queued -- {exportJobId} {chunk}')
                logging.warn(sent)
                vuln_table.merge(exportJobId, str(chunk), {
                    'jobStatus': TenableStatus.sent_to_queue.value
                })
            except Exception as e:
                logging.warn(
                    f'Failed to send {exportJobId} - {chunk} to be processed')
                logging.warn(e)

                vuln_table.merge(exportJobId, str(chunk), {
                    'jobStatus': TenableStatus.sent_to_queue_failed.value,
                    'jobType': TenableExportType.asset.value
                })
    else:
        logging.info('no chunk found to process.')
        return


def main(exportJobId: str) -> object:
    logging.info('using pyTenable client to check asset export job status')
    logging.info(
        f'checking status at vulns/{exportJobId}/status')
    tio = TenableIO()
    job_details = tio.exports.status('vulns', exportJobId)
    # r = tio.get(f'{get_vuln_export_url()}/{exportJobId}/status')
    logging.info(
        f'received a response from vulns/{exportJobId}/status')
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
