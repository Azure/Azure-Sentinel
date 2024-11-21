"""Queue trigger function for ingesting compliance export job chunks into Sentinel."""

import json
import logging
import os

import azure.functions as func

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..azure_sentinel import AzureSentinel
from ..tenable_helper import TenableIO, TenableStatus, TenableChunkPartitioner
from tenable.errors import APIError

connection_string = os.environ["AzureWebJobsStorage"]
compliance_table_name = ExportsTableNames.TenableComplianceExportTable.value
checkpoint_table_name = ExportsTableNames.TenableExportCheckpointTable.value
workspace_id = os.environ["WorkspaceID"]
workspace_key = os.environ["WorkspaceKey"]
log_analytics_uri = os.getenv("LogAnalyticsUri", "")
log_type = "Tenable_VM_Compliance_CL"


def main(msg: func.QueueMessage) -> None:
    """Ingest compliance export job chunks into Sentinel."""
    logging.info(
        "Python queue trigger function processed a queue item: %s",
        msg.get_body().decode("utf-8"),
    )
    decoded_message = msg.get_body().decode("utf-8")
    compliance_table = ExportsTableStore(connection_string, compliance_table_name)

    try:
        export_job_details = json.loads(decoded_message)
        export_job_id = export_job_details.get("exportJobId", "")
        chunk_id = export_job_details.get("chunkId", "")
        start_time = export_job_details.get("startTime", 0)
        update_checkpoint = export_job_details.get("updateCheckpoint", False)

        if export_job_id == "" or chunk_id == "":
            logging.warning(
                "missing information to process a chunk: message sent - {}".format(
                    decoded_message
                )
            )
            raise Exception(
                "cannot process without export job ID and chunk ID -- found job ID {} - chunk ID {}".format(
                    export_job_id, chunk_id
                )
            )
        else:
            logging.info(
                "using pyTenable client to download compliance export job chunk"
            )
            logging.info(
                "downloading chunk at compliance/{}/chunks/{}".format(
                    export_job_id, chunk_id
                )
            )
            tio = TenableIO()
            try:
                chunk = tio.exports.download_chunk(
                    "compliance", export_job_id, chunk_id
                )
                logging.info(
                    "received a response from compliance/{}/chunks/{}".format(
                        export_job_id, chunk_id
                    )
                )
                if len(chunk) == 0:
                    logging.info(
                        "No data found in chunk, chunk_id: {}, job_id: {}".format(
                            chunk_id, export_job_id
                        )
                    )
                else:
                    # limiting individual chunk uploaded to sentinel to be < 30 MB size.
                    sub_chunks = TenableChunkPartitioner.partition_chunks_into_30MB_sub_chunks(chunk)

                    for sub_chunk in sub_chunks:
                        serialized_sub_chunk = json.dumps(sub_chunk)

                        logging.info(
                            "Uploading sub-chunk with size: %d",
                            len(serialized_sub_chunk),
                        )

                        # Send to Azure Sentinel here
                        az_sentinel = AzureSentinel(
                            workspace_id, workspace_key, log_type, log_analytics_uri
                        )

                        az_code = az_sentinel.post_data(serialized_sub_chunk)

                        logging.warning(
                            f"Azure Sentinel reports the following status code: {az_code}"
                        )

                compliance_table.update_if_found(
                    export_job_id,
                    str(chunk_id),
                    {"jobStatus": TenableStatus.finished.value},
                )
                if update_checkpoint:
                    logging.info(
                        "Updating Compliance checkpoint to value: {}".format(start_time)
                    )
                    checkpoint_table = ExportsTableStore(
                        connection_string, checkpoint_table_name
                    )
                    checkpoint_table.merge(
                        "compliance", "timestamp", {"compliance_timestamp": start_time}
                    )
            except APIError as api_err:
                logging.warning(
                    "Failure to retrieve compliance data from Tenable. Response code: {}"
                    " Request ID: {} Export Job ID: {} Chunk ID: {}".format(
                        api_err.code, api_err.uuid, export_job_id, chunk_id
                    )
                )
                compliance_table.update_if_found(
                    export_job_id,
                    str(chunk_id),
                    {
                        "jobStatus": TenableStatus.failed.value,
                        "tenableFailedRequestId": api_err.uuid,
                        "tenableFailedRequestStatusCode": api_err.code,
                    },
                )
                raise Exception(
                    "Retrieving from Tenable failed with status code {}".format(
                        api_err.code
                    )
                )

    except Exception as err:
        compliance_table.update_if_found(
            export_job_id, str(chunk_id), {"jobStatus": TenableStatus.failed.value}
        )
        logging.warning(
            "there was an error processing chunks: message sent - {}: error - {}".format(
                decoded_message, err
            )
        )
        raise err
