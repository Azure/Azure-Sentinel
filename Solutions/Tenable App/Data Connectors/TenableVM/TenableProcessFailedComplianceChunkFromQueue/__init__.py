"""Queue trigger function for processing failed compliance export job chunks."""

import logging
import os
import json
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableStatus

import azure.functions as func

connection_string = os.environ["AzureWebJobsStorage"]
compliance_table_name = ExportsTableNames.TenableComplianceExportTable.value


def main(msg: func.QueueMessage) -> None:
    """Process failed compliance export job chunks.

    Args:
        msg (func.QueueMessage): Queue message
    """
    logging.info(
        "Python queue trigger compliance failure function processed a queue item: %s",
        msg.get_body().decode("utf-8"),
    )
    decoded_message = msg.get_body().decode("utf-8")

    try:
        export_job_details = json.loads(decoded_message)
        export_job_id = (
            export_job_details["exportJobId"]
            if "exportJobId" in export_job_details
            else ""
        )
        chunk_id = (
            export_job_details["chunkId"] if "chunkId" in export_job_details else ""
        )

        if export_job_id == "" or chunk_id == "":
            logging.warning("missing information to process a chunk")
            logging.warning("message sent - {}".format(decoded_message))
            logging.warning(
                "cannot process without export job ID and chunk ID -- found job ID {} - chunk ID {}".format(
                    export_job_id, chunk_id
                )
            )
            logging.warning("Removing from compliance poison queue")
            return

        compliance_table = ExportsTableStore(connection_string, compliance_table_name)
        if compliance_table.get(export_job_id, chunk_id) is not None:
            compliance_table.merge(
                export_job_id, str(chunk_id), {"jobStatus": TenableStatus.failed.value}
            )
        return
    except Exception as err:
        logging.warning("Could not process job or chunk")
        logging.warning("Raised this exception {}".format(err))
        logging.warning("Removing from compliance poison queue")
        return
