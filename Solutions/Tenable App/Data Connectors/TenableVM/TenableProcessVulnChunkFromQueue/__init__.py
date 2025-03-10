import os
import json
import logging
import azure.functions as func

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableIO, TenableStatus, TenableChunkPartitioner
from ..azure_sentinel import AzureSentinel
from tenable.errors import APIError

connection_string = os.environ["AzureWebJobsStorage"]
vuln_table_name = ExportsTableNames.TenableVulnExportTable.value
checkpoint_table_name = ExportsTableNames.TenableExportCheckpointTable.value
workspace_id = os.environ["WorkspaceID"]
workspace_key = os.environ["WorkspaceKey"]
log_analytics_uri = os.getenv("LogAnalyticsUri", "")
log_type = "Tenable_VM_Vuln_CL"

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)


def main(msg: func.QueueMessage) -> None:
    logging.info("Python queue trigger function processed a queue item: %s",
                 msg.get_body().decode("utf-8"))
    decoded_message = msg.get_body().decode("utf-8")
    vuln_table = ExportsTableStore(
        connection_string, vuln_table_name)

    try:
        export_job_details = json.loads(decoded_message)
        export_job_id = export_job_details.get("exportJobId", "")
        chunk_id = export_job_details.get("chunkId", "")
        start_time = export_job_details.get("startTime", 0)
        update_checkpoint = export_job_details.get("updateCheckpoint", False)

        if export_job_id == "" or chunk_id == "":
            logging.warning("missing information to process a chunk")
            logging.warning(f"message sent - {decoded_message}")
            raise Exception(
                f"cannot process without export job ID and chunk ID -- found job ID {export_job_id} - chunk ID {chunk_id}")
        else:
            logging.info(
                "using pyTenable client to download vulnerability export job chunk")
            logging.info(
                f"downloading chunk at vulns/{export_job_id}/chunks/{chunk_id}")
            tio = TenableIO()
            try:
                chunk = tio.exports.chunk("vulns", export_job_id, chunk_id)
                logging.info(
                    f"received a response from vulns/{export_job_id}/chunks/{chunk_id}")

                if len(chunk) == 0:
                    logging.info("No data found in chunk, chunk_id: {}, job_id: {}".format(chunk_id, export_job_id))
                else:
                    # limiting individual chunk uploaded to sentinel to be < 30 MB size.
                    sub_chunks = TenableChunkPartitioner.partition_chunks_into_30MB_sub_chunks(chunk)

                    for sub_chunk in sub_chunks:
                        serialized_sub_chunk = json.dumps(sub_chunk)

                        logging.info("Uploading sub-chunk with size: %d", len(serialized_sub_chunk))

                        # Send to Azure Sentinel here
                        az_sentinel = AzureSentinel(
                            workspace_id, workspace_key, log_type, log_analytics_uri)

                        az_code = az_sentinel.post_data(serialized_sub_chunk)

                        logging.warning(
                            f"Azure Sentinel reports the following status code: {az_code}")

                vuln_table.update_if_found(export_job_id, str(chunk_id), {
                    "jobStatus": TenableStatus.finished.value
                })
                if update_checkpoint:
                    logging.info(
                        "Updating Vulns checkpoint to value: {}".format(start_time)
                    )
                    checkpoint_table = ExportsTableStore(
                        connection_string, checkpoint_table_name
                    )
                    checkpoint_table.merge(
                        "vulns", "timestamp", {"vulns_timestamp": start_time}
                    )
            except APIError as e:
                logging.warning(
                    f"Failure to retrieve vulnerability data from Tenable. Response code: {e.code} Request ID: {e.uuid} Export Job ID: {export_job_id} Chunk ID: {chunk_id}")
                vuln_table.update_if_found(export_job_id, str(chunk_id), {
                    "jobStatus": TenableStatus.failed.value,
                    "tenableFailedRequestId": e.uuid,
                    "tenableFailedRequestStatusCode": e.code
                })
                raise Exception(
                    f"Retrieving from Tenable failed with status code {e.code}")

    except Exception as e:
        vuln_table.update_if_found(export_job_id, str(chunk_id), {
            "jobStatus": TenableStatus.failed.value
        })
        logging.warning(
            f"there was an error processing chunks. message sent - {decoded_message}")
        logging.warning(e)
        raise e
