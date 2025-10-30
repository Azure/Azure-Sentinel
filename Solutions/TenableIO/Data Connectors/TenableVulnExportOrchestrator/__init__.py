import os
import logging
from datetime import timedelta
from ..tenable_helper import TenableStatus, TenableExportType

import azure.functions as func
import azure.durable_functions as df

vuln_status_and_chunk = 'TenableVulnExportStatusAndSendChunks'
export_poll_schedule_minutes = int(os.getenv('TenableExportPollScheduleInMinutes', '1'))


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info('started vuln export orchestrator')
    job_details = context.get_input()
    logging.info('loaded job details from orchestrator:')
    logging.info(job_details)

    vuln_job_id = job_details['vulnJobId'] if 'vulnJobId' in job_details else ''
    if vuln_job_id == '':
        return {
            'status': TenableStatus.no_job.value,
            'id': '',
            'chunks': [],
            'vulnInstanceId': context.instance_id,
            'type': TenableExportType.vuln.value
        }

    chunks = []
    logging.info(f'checking status of job {vuln_job_id}, outside while loop')
    job_status = yield context.call_activity(vuln_status_and_chunk, vuln_job_id)

    logging.info(f'{vuln_job_id} is currently in this state:')
    logging.info(job_status)
    logging.info(job_status['status'])

    tio_status = ['ERROR', 'CANCELLED', 'FINISHED']
    while not 'status' in job_status or not (job_status['status'] in tio_status):
        job_status = yield context.call_activity(vuln_status_and_chunk, vuln_job_id)
        logging.info(
            f'Checking {vuln_job_id} after waking up again, inside while loop:')
        logging.info(job_status)
        logging.info(job_status['status'])

        if 'status' in job_status and job_status['status'] == 'FINISHED':
            logging.info('job is completely finished!')
            chunks = job_status['chunks_available']
            logging.info(f'Found these chunks: {chunks}')
            break
        elif 'status' in job_status and job_status['status'] == 'ERROR':
            logging.info('job is completed with Error status!')
            chunks = job_status['chunks_available']
            logging.info(f'Found these chunks: {chunks}')
            break
        elif 'status' in job_status and job_status['status'] == 'CANCELLED':
            logging.info('job is completed with Cancelled status!')
            chunks = job_status['chunks_available']
            logging.info(f'Found these chunks: {chunks}')
            break
        else:
            logging.info('not quite ready, going to sleep...')
            next_check = context.current_utc_datetime + timedelta(minutes=export_poll_schedule_minutes)
            yield context.create_timer(next_check)

    logging.info(
        f'all chunks have been sent to process! {vuln_job_id} finally COMPLETED')
    logging.info('Checking that chunks exist...')
    logging.info(f'Number of chunks: {len(chunks)}')

    tenable_status = TenableStatus.finished.value
    if 'status' in job_status and (job_status['status'] is 'CANCELLED' or job_status['status'] is 'ERROR'):
        tenable_status = TenableStatus.failed.value

    return {
        'status': tenable_status,
        'id': vuln_job_id,
        'chunks': chunks,
        'vulnInstanceId': context.instance_id,
        'type': TenableExportType.vuln.value
    }


main = df.Orchestrator.create(orchestrator_function)
