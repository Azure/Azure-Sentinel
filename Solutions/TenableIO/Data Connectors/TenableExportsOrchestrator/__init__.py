import logging
import os
from datetime import timedelta, datetime, timezone

import azure.functions as func
import azure.durable_functions as df

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableStatus, TenableExportType

connection_string = os.environ['AzureWebJobsStorage']
stats_table_name = ExportsTableNames.TenableExportStatsTable.value
export_schedule_minutes = int(
    os.getenv('TenableExportScheduleInMinutes', '1440'))
start_asset_job_name = 'TenableStartAssetExportJob'
start_vuln_job_name = 'TenableStartVulnExportJob'
asset_orchestrator_name = 'TenableAssetExportOrchestrator'
vuln_orchestrator_name = 'TenableVulnExportOrchestrator'


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info('started main orchestrator')
    logging.info(
        f'instance id: f{context.instance_id} at {context.current_utc_datetime}')
    first_run = context.get_input()
    if first_run is not None and 'isFirstRun' in first_run and first_run['isFirstRun'] == True:
        filter_by_time = 0
    else:
        filter_by_time = int(
            (datetime.now(timezone.utc) - timedelta(minutes=export_schedule_minutes)).timestamp())
    logging.info('filter by time: %d', filter_by_time)

    stats_store = ExportsTableStore(connection_string, stats_table_name)

    asset_export_job_id = yield context.call_activity(start_asset_job_name, filter_by_time)
    logging.info('retrieved a new asset job ID')
    logging.warn(
        f'instance id: f{context.instance_id} working with asset export job {asset_export_job_id}, sending to sub orchestrator')

    stats_store.merge(asset_export_job_id, 'prime', {
        'status': TenableStatus.processing.value,
        'exportType': TenableExportType.asset.value,
        'failedChunks': '',
        'chunks': '',
        'totalChunksCount': 0,
        'jobTimestamp': filter_by_time,
        'startedAt': context.current_utc_datetime.timestamp()
    })
    logging.info(
        f'saved {asset_export_job_id} to stats table. moving to start vuln job.')

    vuln_export_job_id = yield context.call_activity(start_vuln_job_name, filter_by_time)
    logging.info('retrieved a new vuln job ID')
    logging.warn(
        f'instance id: f{context.instance_id} working with vuln export job {vuln_export_job_id}, sending to sub orchestrator')

    stats_store.merge(vuln_export_job_id, 'prime', {
        'status': TenableStatus.processing.value,
        'exportType': TenableExportType.vuln.value,
        'failedChunks': '',
        'chunks': '',
        'totalChunksCount': 0,
        'jobTimestamp': filter_by_time,
        'startedAt': context.current_utc_datetime.timestamp()
    })

    asset_export = context.call_sub_orchestrator(asset_orchestrator_name, {
        'timestamp': filter_by_time,
        'assetJobId': asset_export_job_id,
        'mainOrchestratorInstanceId': context.instance_id
    })
    stats_store.merge(asset_export_job_id, 'prime', {
        'status': TenableStatus.sent_to_sub_orchestrator.value
    })

    vuln_export = context.call_sub_orchestrator(vuln_orchestrator_name, {
        'timestamp': filter_by_time,
        'vulnJobId': vuln_export_job_id,
        'mainOrchestratorInstanceId': context.instance_id
    })
    stats_store.merge(vuln_export_job_id, 'prime', {
        'status': TenableStatus.sent_to_sub_orchestrator.value
    })

    results = yield context.task_all([asset_export, vuln_export])
    logging.info('Finished both jobs!')
    logging.info(results)

    try:
        asset_job_finished = results[0]
        asset_id = asset_job_finished['id'] if 'id' in asset_job_finished else ''
        chunks = asset_job_finished['chunks'] if 'chunks' in asset_job_finished else [
        ]
        chunk_ids = ','.join(str(c) for c in chunks)
        if asset_id != '':
            stats_store.merge(asset_id, 'prime', {
                'status': TenableStatus.finished.value,
                'chunks': chunk_ids,
                'totalChunksCount': len(chunks)
            })
    except IndexError as e:
        logging.warn('asset job returned no results')
        logging.warn(e)

    try:
        vuln_job_finished = results[1]
        vuln_id = vuln_job_finished['id'] if 'id' in vuln_job_finished else ''
        chunks = vuln_job_finished['chunks'] if 'chunks' in vuln_job_finished else [
        ]
        chunk_ids = ','.join(str(c) for c in chunks)
        if vuln_id != '':
            stats_store.merge(vuln_id, 'prime', {
                'status': TenableStatus.finished.value,
                'chunks': chunk_ids,
                'totalChunksCount': len(chunks)
            })
    except IndexError as e:
        logging.warn('vuln job returned no results')
        logging.warn(e)

    next_check = context.current_utc_datetime + \
        timedelta(minutes=export_schedule_minutes)
    yield context.create_timer(next_check)
    context.continue_as_new(None)


main = df.Orchestrator.create(orchestrator_function)
