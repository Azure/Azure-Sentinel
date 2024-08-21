import logging
import os
from datetime import datetime, timedelta, timezone
from ..exports_store import ExportsTableStore, ExportsTableNames
from ..exports_queue import ExportsQueue, ExportsQueueNames

import azure.functions as func
import azure.durable_functions as df

connection_string = os.environ['AzureWebJobsStorage']
stats_table_name = ExportsTableNames.TenableExportStatsTable.value
assets_export_table_name = ExportsTableNames.TenableAssetExportTable.value
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value
assets_queue_name = ExportsQueueNames.TenableAssetExportsQueue.value
vuln_queue_name = ExportsQueueNames.TenableVulnExportsQueue.value

orchestrator_function_name = 'TenableExportsOrchestrator'
cleanup_orchestrator_function_name = 'TenableCleanUpOrchestrator'


async def start_new_orchestrator(client, is_first_run=False):
    stats_table = ExportsTableStore(connection_string, stats_table_name)
    if is_first_run:
        instance_id = await client.start_new(orchestrator_function_name, None, {'isFirstRun': True})
    else:
        instance_id = await client.start_new(orchestrator_function_name, None, {'isFirstRun': False})
    logging.info(f"Started orchestration with ID = '{instance_id}'.")
    stats_table.merge('main', 'current', {
        'exportsInstanceId': instance_id
    })
    return instance_id


async def start_new_cleanup_orchestrator(client):
    stats_table = ExportsTableStore(connection_string, stats_table_name)
    instance_id = await client.start_new(cleanup_orchestrator_function_name, None, None)
    logging.info(f"Started clean up orchestration with ID = '{instance_id}'.")
    stats_table.merge('main', 'current', {
        'cleanupInstanceId': instance_id
    })
    return instance_id


def first_run_setup():
    logging.info('First run detected...')
    logging.info('Setting up the following resources:')
    logging.info(stats_table_name)
    logging.info(assets_export_table_name)
    logging.info(vuln_export_table_name)
    logging.info(assets_queue_name)
    logging.info(vuln_queue_name)
    stats_table = ExportsTableStore(connection_string, stats_table_name)
    stats_table.create()

    asesets_table = ExportsTableStore(
        connection_string, assets_export_table_name)
    asesets_table.create()

    vuln_table = ExportsTableStore(connection_string, vuln_export_table_name)
    vuln_table.create()

    assets_queue = ExportsQueue(connection_string, assets_queue_name)
    assets_queue.create()

    vuln_queue = ExportsQueue(connection_string, vuln_queue_name)
    vuln_queue.create()

    stats_table.post('main', 'current', {
        'exportsInstanceId': '',
        'cleanupInstanceId': '',
        'isFirstRun': False
    })
    return


async def main(mytimer: func.TimerRequest, starter: str) -> None:
    utc_timestamp = datetime.utcnow().replace(
        tzinfo=timezone.utc).isoformat()
    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    client = df.DurableOrchestrationClient(starter)

    store = ExportsTableStore(
        connection_string=connection_string, table_name=stats_table_name)
    logging.info('looking in table storage for running instance')
    job_info = store.get('main', 'current')
    logging.info('results from table storage:')
    logging.info(job_info)

    if job_info is not None:
        logging.info('checking if an existing instance was found...')
        singleton_instance_id = job_info['exportsInstanceId'] if 'exportsInstanceId' in job_info else ''
        logging.info(f'exports instance id value: {singleton_instance_id}')
        if not singleton_instance_id == '':
            logging.info(
                f'Located an existing orchestrator instance: {singleton_instance_id}')
            existing_instance = await client.get_status(singleton_instance_id)
            logging.info(existing_instance)
            logging.info(existing_instance.runtime_status)

            if existing_instance is None or existing_instance.runtime_status in [df.OrchestrationRuntimeStatus.Completed, df.OrchestrationRuntimeStatus.Failed, df.OrchestrationRuntimeStatus.Terminated, None]:
                new_instance_id = await start_new_orchestrator(client)
                logging.info(f'started new instance -- {new_instance_id}')
            else:
                logging.info(
                    'Export job is already currently running. Will try again later.')
        else:
            logging.info('not a first run, but no instance id found yet.')
            logging.info('starting new instance id.')
            new_instance_id = await start_new_orchestrator(client)
            logging.info(f'started new instance -- {new_instance_id}')

        logging.info('checking for an existing cleanup instance was found...')
        cleanup_singleton_instance_id = job_info['cleanupInstanceId'] if 'cleanupInstanceId' in job_info else ''
        if not cleanup_singleton_instance_id == '':
            logging.info(
                f'Located an existing cleanup orchestrator instance: {cleanup_singleton_instance_id}')
            existing_cleanup_instance = await client.get_status(cleanup_singleton_instance_id)
            logging.info(existing_cleanup_instance)
            logging.info(existing_cleanup_instance.runtime_status)
            if existing_cleanup_instance is None or existing_cleanup_instance.runtime_status in [df.OrchestrationRuntimeStatus.Completed, df.OrchestrationRuntimeStatus.Failed, df.OrchestrationRuntimeStatus.Terminated, None]:
                new_cleanup_instance_id = await start_new_cleanup_orchestrator(client)
                logging.info(
                    f'started new instance -- {new_cleanup_instance_id}')
            else:
                logging.info(
                    'Cleanup job is already currently running. Will try again later.')
        else:
            logging.info(
                'not a first run, but no cleanup instance id found yet.')
            logging.info('starting new cleanup instance id.')
            cleanup_new_instance_id = await start_new_cleanup_orchestrator(client)
            logging.info(f'started new instance -- {cleanup_new_instance_id}')
    else:
        first_run_setup()
        await start_new_orchestrator(client, True)
        await start_new_cleanup_orchestrator(client)
        return
