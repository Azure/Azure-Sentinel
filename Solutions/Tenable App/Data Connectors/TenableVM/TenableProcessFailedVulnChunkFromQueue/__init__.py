import logging
import os
import json
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableStatus

import azure.functions as func

connection_string = os.environ["AzureWebJobsStorage"]
vuln_table_name = ExportsTableNames.TenableVulnExportTable.value


def main(msg: func.QueueMessage) -> None:
    logging.info("Python queue trigger vuln failure function processed a queue item: %s",
                 msg.get_body().decode("utf-8"))
    decoded_message = msg.get_body().decode("utf-8")

    try:
        export_job_details = json.loads(decoded_message)
        export_job_id = export_job_details["exportJobId"] if "exportJobId" in export_job_details else ""
        chunk_id = export_job_details["chunkId"] if "chunkId" in export_job_details else ""

        if export_job_id == "" or chunk_id == "":
            logging.warning("missing information to process a chunk")
            logging.warning(f"message sent - {decoded_message}")
            logging.warning(
                f"cannot process without export job ID and chunk ID -- found job ID {export_job_id} - chunk ID {chunk_id}")
            logging.warning("Removing from vuln poison queue")
            return

        vuln_table = ExportsTableStore(
            connection_string, vuln_table_name)
        if vuln_table.get(export_job_id, chunk_id) is not None:
            vuln_table.merge(export_job_id, str(chunk_id), {
                "jobStatus": TenableStatus.failed.value
            })
        return
    except Exception as e:
        logging.warning("Could not process job or chunk")
        logging.warning(f"Raised this exception {e}")
        logging.warning("Removing from vuln poison queue")
        return
