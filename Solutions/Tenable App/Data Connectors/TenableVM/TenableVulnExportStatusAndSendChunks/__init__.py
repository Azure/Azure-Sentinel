import json
import logging
import os

from ..exports_queue import ExportsQueue, ExportsQueueNames
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableIO, TenableStatus, TenableExportType, update_checkpoint_for_last_chunk

# from tenable.io import TenableIO

connection_string = os.environ["AzureWebJobsStorage"]
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value
vuln_queue_name = ExportsQueueNames.TenableVulnExportsQueue.value


def send_chunks_to_queue(exportJobDetails):
    logging.info(f"Sending chunk to queue.")
    chunks = exportJobDetails.get("chunks_available", [])
    exportJobId = exportJobDetails.get("exportJobId", "")
    start_time = exportJobDetails.get("start_time", 0)
    job_status = exportJobDetails.get("status", "")

    if len(chunks) > 0:
        vuln_table = ExportsTableStore(
            connection_string, vuln_export_table_name)
        update_checkpoint = False
        for chunk in chunks:
            update_checkpoint = update_checkpoint_for_last_chunk(chunk, chunks, job_status)
            chunk_dtls = vuln_table.get(exportJobId, str(chunk))
            if chunk_dtls:
                current_chunk_status = chunk_dtls["jobStatus"]
                if (
                        current_chunk_status == TenableStatus.sent_to_queue.value or
                        current_chunk_status == TenableStatus.finished.value
                ):
                    logging.warning(
                        f"Avoiding vuln chunk duplicate processing -- {exportJobId} {chunk}. Current status: {current_chunk_status}")
                    continue

            vuln_table.post(exportJobId, str(chunk), {
                "jobStatus": TenableStatus.sending_to_queue.value,
                "jobType": TenableExportType.vuln.value
            })

            vuln_queue = ExportsQueue(connection_string, vuln_queue_name)

            try:
                sent = vuln_queue.send_chunk_info(
                    exportJobId, chunk, start_time, update_checkpoint
                )
                logging.warning(f"chunk queued -- {exportJobId} {chunk}")
                logging.warning(sent)
                vuln_table.merge(exportJobId, str(chunk), {
                    "jobStatus": TenableStatus.sent_to_queue.value
                })
            except Exception as e:
                logging.warning(
                    f"Failed to send {exportJobId} - {chunk} to be processed")
                logging.warning(e)

                vuln_table.merge(exportJobId, str(chunk), {
                    "jobStatus": TenableStatus.sent_to_queue_failed.value,
                    "jobType": TenableExportType.vuln.value
                })
    else:
        logging.info("no chunk found to process.")
        return


def main(exportJob: str) -> object:
    jsonExportObject = json.loads(exportJob)
    exportJobId = jsonExportObject.get("vuln_job_id", "")
    start_time = jsonExportObject.get("start_time", 0)
    logging.info("using pyTenable client to check vulnerability export job status")
    logging.info(
        f"checking status at vulns/{exportJobId}/status")
    tio = TenableIO()
    job_details = tio.exports.status("vulns", exportJobId)
    # r = tio.get(f"{get_vuln_export_url()}/{exportJobId}/status")
    logging.info(
        f"received a response from vulns/{exportJobId}/status")
    logging.info(job_details)

    tio_status = ["ERROR", "CANCELLED"]
    if job_details["status"] not in tio_status:
        try:
            job_details["exportJobId"] = exportJobId
            job_details["start_time"] = start_time
            send_chunks_to_queue(job_details)
        except Exception as e:
            logging.warning("error while sending chunks to queue")
            logging.warning(job_details)
            logging.warning(e)

    return job_details
