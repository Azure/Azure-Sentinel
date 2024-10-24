"""Orchestrator function for compliance export jobs."""

import json
import os
import logging
from datetime import timedelta
from ..tenable_helper import TenableExportType, TenableStatus

import azure.durable_functions as df

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

compliance_status_and_chunk = "TenableComplianceExportStatusAndSendChunks"
export_poll_schedule_minutes = int(os.getenv("TenableExportPollScheduleInMinutes", "1"))
chunks_found_log = "Found these chunks: {}"


def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to check the status of compliance export job and store chunks_available.

    Args:
        context: The durable orchestration context

    Returns:
        A dictionary containing the status, id, chunks, complianceInstanceId and type of the job
    """
    logging.info("started compliance export orchestrator")
    job_details = context.get_input()
    logging.info("loaded job details from orchestrator:")
    logging.info(job_details)

    compliance_job_id = (
        job_details["complianceJobId"] if "complianceJobId" in job_details else ""
    )
    if compliance_job_id == "":
        return {
            "status": TenableStatus.no_job.value,
            "id": "",
            "chunks": [],
            "complianceInstanceId": context.instance_id,
            "type": TenableExportType.compliance.value,
        }

    chunks = []
    logging.info(
        "checking status of job {}, outside while loop".format(compliance_job_id)
    )
    start_time = job_details.get("start_time", 0)
    str_activity_data = json.dumps({"compliance_job_id": compliance_job_id, "start_time": start_time})
    job_status = yield context.call_activity(
        compliance_status_and_chunk, str_activity_data
    )
    logging.info("{} is currently in this state:".format(compliance_job_id))
    logging.info(job_status)
    logging.info(job_status["status"])

    tio_status = ["ERROR", "CANCELLED", "FINISHED"]
    while ("status" not in job_status) or (job_status["status"] not in tio_status):
        logging.info(
            "Checking {} after waking up again, inside while loop:".format(
                compliance_job_id
            )
        )
        job_status = yield context.call_activity(
            compliance_status_and_chunk, str_activity_data
        )
        logging.info("{} is currently in this state:".format(compliance_job_id))
        logging.info(job_status)

        if "status" in job_status and job_status["status"] == "FINISHED":
            logging.info("job is completely finished!")
            chunks = job_status["chunks_available"]
            logging.info(chunks_found_log.format(chunks))
            break
        elif "status" in job_status and job_status["status"] == "ERROR":
            logging.info("job is completed with Error status!")
            chunks = job_status["chunks_available"]
            logging.info(chunks_found_log.format(chunks))
            break
        elif "status" in job_status and job_status["status"] == "CANCELLED":
            logging.info("job is completed with Cancelled status!")
            chunks = job_status["chunks_available"]
            logging.info(chunks_found_log.format(chunks))
            break
        else:
            logging.info("not quite ready, going to sleep...")
            next_check = context.current_utc_datetime + timedelta(
                minutes=export_poll_schedule_minutes
            )
            yield context.create_timer(next_check)

    logging.info("Checking that chunks exist...")
    logging.info("Number of chunks: {}".format(len(chunks)))

    tenable_status = TenableStatus.finished.value
    if "status" in job_status and (
        job_status["status"] == "CANCELLED" or job_status["status"] == "ERROR"
    ):
        tenable_status = TenableStatus.failed.value

    return {
        "status": tenable_status,
        "id": compliance_job_id,
        "chunks": chunks,
        "complianceInstanceId": context.instance_id,
        "type": TenableExportType.compliance.value,
    }


main = df.Orchestrator.create(orchestrator_function)
