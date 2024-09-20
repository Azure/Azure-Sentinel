import os
import logging
from datetime import timedelta
from ..tenable_helper import TenableExportType, TenableStatus

import azure.functions as func
import azure.durable_functions as df

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

asset_status_and_chunk = 'TenableAssetExportStatusAndSendChunks'
export_poll_schedule_minutes = int(os.getenv('TenableExportPollScheduleInMinutes', '1'))

def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info('started asset export orchestrator')
    job_details = context.get_input()
    logging.info('loaded job details from orchestrator:')
    logging.info(job_details)

    asset_job_id = job_details['assetJobId'] if 'assetJobId' in job_details else ''
    if asset_job_id == '':
        return {
            'status': TenableStatus.no_job.value,
            'id': '',
            'chunks': [],
            'assetInstanceId': context.instance_id,
            'type': TenableExportType.asset.value
        }

    chunks = []
    logging.info(f'checking status of job {asset_job_id}, outside while loop')
    job_status = yield context.call_activity(asset_status_and_chunk, asset_job_id)
    logging.info(f'{asset_job_id} is currently in this state:')
    logging.info(job_status)
    logging.info(job_status['status'])

    tio_status = ['ERROR', 'CANCELLED', 'FINISHED']
    while not 'status' in job_status or not (job_status['status'] in tio_status):
        logging.info(
            f'Checking {asset_job_id} after waking up again, inside while loop:')
        job_status = yield context.call_activity(asset_status_and_chunk, asset_job_id)
        logging.info(f'{asset_job_id} is currently in this state:')
        logging.info(job_status)

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

    logging.info('Checking that chunks exist...')
    logging.info(f'Number of chunks: {len(chunks)}')

    tenable_status = TenableStatus.finished.value
    if 'status' in job_status and (job_status['status'] is 'CANCELLED' or job_status['status'] is 'ERROR'):
        tenable_status = TenableStatus.failed.value

    return {
        'status': tenable_status,
        'id': asset_job_id,
        'chunks': chunks,
        'assetInstanceId': context.instance_id,
        'type': TenableExportType.asset.value
    }


main = df.Orchestrator.create(orchestrator_function)
