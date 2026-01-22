"""Orchestrator function for compliance export jobs."""

import json
import os
import logging
from datetime import timedelta
from ..tenable_helper import TenableExportType, TenableStatus

import azure.durable_functions as df

compliance_status_and_chunk = "TenableComplianceExportStatusAndSendChunks"
export_poll_schedule_minutes = int(os.getenv("TenableExportPollScheduleInMinutes", "1"))
logs_starts_with = "TenableVM"
function_name = "TenableComplianceExportOrchestrator"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to handle Tenable.io Compliance Export Jobs.

    It calls activity function to check job status. If finished, returns the chunks available.

    Args:
        context: The durable orchestration context

    Returns:
        A dictionary containing the status of the job, the job ID, the chunks available,
        the compliance instance ID and the type of export
    """
    logging.info(
        f"{logs_starts_with} {function_name}: Started compliance export orchestrator."
    )
    job_details = context.get_input()
    logging.info(
        f"{logs_starts_with} {function_name}: Loaded job details from orchestrator: {job_details}"
    )

    compliance_job_id = job_details["complianceJobId"] if "complianceJobId" in job_details else ""
    if compliance_job_id == "":
        return {
            "status": TenableStatus.no_job.value,
            "id": "",
            "chunks": [],
            "complianceInstanceId": context.instance_id,
            "type": TenableExportType.compliance.value,
        }

    chunks = []
    start_time = job_details.get("start_time", 0)
    str_activity_data = json.dumps(
        {"compliance_job_id": compliance_job_id, "start_time": start_time}
    )

    while True:
        logging.info(
            f"{logs_starts_with} {function_name}: Checking status of job {compliance_job_id}"
        )
        str_job_status = yield context.call_activity(
            compliance_status_and_chunk, str_activity_data
        )
        try:
            job_status = json.loads(str_job_status)
        except json.JSONDecodeError as json_err:
            logging.error(
                f"{logs_starts_with} {function_name}: Error while loading JSON data from activity. Error: {json_err}"
            )
            raise Exception(json_err)
        logging.info(
            f"{logs_starts_with} {function_name}: {compliance_job_id} is currently in this state: {job_status['status']}"
        )

        if "status" in job_status and job_status["status"] in ["FINISHED", "ERROR", "CANCELLED"]:
            logging.info(f"{logs_starts_with} {function_name}: Job is completed with {job_status["status"].lower()}!")
            chunks = job_status["chunks_available"]
            logging.info(f"{logs_starts_with} {function_name}: Found these chunks: {chunks}")
            break
        logging.info(
            f"{logs_starts_with} {function_name}: Job is not completed. Retrying shortly..."
        )
        next_check = context.current_utc_datetime + timedelta(
            minutes=export_poll_schedule_minutes
        )
        yield context.create_timer(next_check)

    logging.info(f"{logs_starts_with} {function_name}: Number of chunks: {len(chunks)}")

    tenable_status = TenableStatus.finished.value
    if "status" in job_status and (job_status["status"] == "CANCELLED" or job_status["status"] == "ERROR"):
        tenable_status = TenableStatus.failed.value

    return {
        "status": tenable_status,
        "id": compliance_job_id,
        "chunks": chunks,
        "complianceInstanceId": context.instance_id,
        "type": TenableExportType.compliance.value,
    }


main = df.Orchestrator.create(orchestrator_function)
