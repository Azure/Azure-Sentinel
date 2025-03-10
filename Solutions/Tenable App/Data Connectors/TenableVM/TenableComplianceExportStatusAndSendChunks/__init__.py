"""Activity function to check compliance export job status and send chunks to queue."""

import json
import logging
import os

from ..exports_queue import ExportsQueue, ExportsQueueNames
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableIO, TenableStatus, TenableExportType, update_checkpoint_for_last_chunk

connection_string = os.environ["AzureWebJobsStorage"]
compliance_table_name = ExportsTableNames.TenableComplianceExportTable.value
compliance_queue_name = ExportsQueueNames.TenableComplianceExportsQueue.value


def send_chunks_to_queue(export_job_details):
    """
    Send chunks of a compliance export job to queue for processing.

    Args:
        export_job_details: a dictionary containing the exportJobId and chunks_available
    """
    logging.info("Sending chunk to queue.")
    chunks = export_job_details.get("chunks_available", [])
    export_job_id = export_job_details.get("exportJobId", "")
    start_time = export_job_details.get("start_time", 0)
    job_status = export_job_details.get("status", "")

    if len(chunks) > 0:
        compliance_table = ExportsTableStore(connection_string, compliance_table_name)
        update_checkpoint = False
        for chunk in chunks:
            update_checkpoint = update_checkpoint_for_last_chunk(chunk, chunks, job_status)
            chunk_dtls = compliance_table.get(export_job_id, str(chunk))
            if chunk_dtls:
                current_chunk_status = chunk_dtls["jobStatus"]
                if (
                    current_chunk_status == TenableStatus.sent_to_queue.value
                    or current_chunk_status == TenableStatus.finished.value
                ):
                    logging.warning(
                        "Avoiding compliance chunk duplicate processing -- {} {}. Current status: {}".format(
                            export_job_id, chunk, current_chunk_status
                        )
                    )
                    continue

            compliance_table.merge(
                export_job_id,
                str(chunk),
                {
                    "jobStatus": TenableStatus.sending_to_queue.value,
                    "jobType": TenableExportType.compliance.value,
                },
            )

            compliance_queue = ExportsQueue(connection_string, compliance_queue_name)
            try:
                sent = compliance_queue.send_chunk_info(export_job_id, chunk, start_time, update_checkpoint)
                logging.warning("chunk queued -- {} {}".format(export_job_id, chunk))
                logging.warning(sent)
                compliance_table.merge(
                    export_job_id,
                    str(chunk),
                    {"jobStatus": TenableStatus.sent_to_queue.value},
                )
            except Exception as err:
                logging.warning(
                    "Failed to send {} - {} to be processed".format(
                        export_job_id, chunk
                    )
                )
                logging.warning(err)

                compliance_table.merge(
                    export_job_id,
                    str(chunk),
                    {
                        "jobStatus": TenableStatus.sent_to_queue_failed.value,
                        "jobType": TenableExportType.compliance.value,
                    },
                )
    else:
        logging.info("no chunk found to process.")
        return None


def main(exportJob: str) -> object:
    """Check the status of compliance export job id."""
    json_export_object = json.loads(exportJob)
    export_job_id = json_export_object.get("compliance_job_id", "")
    start_time = json_export_object.get("start_time", 0)
    logging.info("using pyTenable client to check compliance export job status")
    logging.info("checking status at compliance/{}/status".format(export_job_id))
    tio = TenableIO()
    job_details = tio.exports.status("compliance", export_job_id)
    logging.info("received a response from compliance/{}/status".format(export_job_id))
    logging.info(job_details)

    tio_status = ["ERROR", "CANCELLED"]
    if job_details["status"] not in tio_status:
        try:
            job_details["exportJobId"] = export_job_id
            job_details["start_time"] = start_time
            send_chunks_to_queue(job_details)
        except Exception as err:
            logging.warning("error while sending chunks to queue")
            logging.warning(job_details)
            logging.warning(err)

    return job_details
