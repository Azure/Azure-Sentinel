import logging
import os
from datetime import datetime, timedelta
from tenable_helper import TenableStatus

from ..exports_store import ExportsTableStore, ExportsTableNames

connection_string = os.environ['AzureWebJobsStorage']
stats_table_name = ExportsTableNames.TenableExportStatsTable.value
assets_export_table_name = ExportsTableNames.TenableAssetExportTable.value
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value


def generate_finished_stats(table_client: ExportsTableStore, stats_table: ExportsTableStore):
    finished_chunks = table_client.query_for_all_finished_chunks()
    jobs_with_finished_chunks = {}

    for fc in finished_chunks:
        logging.info(fc)
        job_id = fc['PartitionKey']
        chunk_id = fc['RowKey']
        if not fc['PartitionKey'] in jobs_with_finished_chunks:
            jobs_with_finished_chunks[job_id] = {
                'chunks': [chunk_id]
            }
        else:
            jobs_with_finished_chunks[job_id]['chunks'].append(chunk_id)

    for job_id in jobs_with_finished_chunks.keys():
        logging.info(f'sending finished stats for {job_id}')
        job = stats_table.get(job_id, 'prime')
        existing_finished_chunks = job['finishedChunks'] if 'finishedChunks' in job else ''

        ids = list(filter(None, existing_finished_chunks.split(',')))
        to_add_ids = jobs_with_finished_chunks[job_id]['chunks']

        logging.info(f'checking existing ids: {ids}')
        if sorted(ids) == sorted(to_add_ids):
            logging.info('nothing to update here')
            continue
        else:
            chunk_ids = list(set(ids) | set(to_add_ids))
            chunk_ids_comma_list = ','.join(str(c) for c in chunk_ids)

        logging.info(f'adding in these chunks {chunk_ids} to finished list')
        chunk_count = len(chunk_ids)
        result = stats_table.merge(job_id, 'prime', {
            'finishedChunks': chunk_ids_comma_list,
            'finishedChunkCount': chunk_count
        })
        logging.info(result)


def generate_processing_stats(table_client: ExportsTableStore, stats_table: ExportsTableStore):
    processing_chunks = table_client.query_for_all_processing_chunks()
    jobs_with_processing_chunks = {}

    for pc in processing_chunks:
        logging.info(pc)
        job_id = pc['PartitionKey']
        chunk_id = pc['RowKey']
        if not pc['PartitionKey'] in jobs_with_processing_chunks:
            jobs_with_processing_chunks[job_id] = {
                'chunks': [chunk_id]
            }
        else:
            jobs_with_processing_chunks[job_id]['chunks'].append(chunk_id)

    for job_id in jobs_with_processing_chunks.keys():
        logging.info(f'sending processing stats for {job_id}')
        job = stats_table.get(job_id, 'prime')
        existing_processing_chunks = job['processingChunks'] if 'processingChunks' in job else ''
        existing_finished_chunks = job['finishedChunks'] if 'finishedChunks' in job else ''
        existing_failed_chunks = job['failedChunks'] if 'failedChunks' in job else ''

        finished_ids = list(filter(None, existing_finished_chunks.split(',')))
        failed_ids = list(filter(None, existing_failed_chunks.split(',')))
        processing_ids = list(
            filter(None, existing_processing_chunks.split(',')))
        to_add_ids = jobs_with_processing_chunks[job_id]['chunks']

        chunk_ids = list((set(processing_ids) | set(to_add_ids)
                          ) - set(finished_ids) - set(failed_ids))
        chunk_ids_comma_list = ','.join(str(c) for c in chunk_ids)

        logging.info(f'adding in these chunks {chunk_ids} to processing list')
        update_job = {}
        chunk_count = len(chunk_ids)
        if chunk_count > 0:
            started_at = job['startedAt'] if 'startedAt' in job else 0
            if started_at == 0:
                update_job.update({'startedAt': datetime.now().timestamp()})
            else:
                started_at_time = datetime.fromtimestamp(
                    started_at) + timedelta(days=3)
                if started_at_time < datetime.now():
                    update_job.update({'status': TenableStatus.failed.value})

        update_job.update({
            'processingChunks': chunk_ids_comma_list,
            'processingChunkCount': chunk_count
        })
        result = stats_table.merge(job_id, 'prime', update_job)
        logging.info(result)


def generate_failed_stats(table_client: ExportsTableStore, stats_table: ExportsTableStore):
    failed_chunks = table_client.query_for_all_failed_chunks()
    jobs_with_failed_chunks = {}

    for fc in failed_chunks:
        logging.info(fc)
        job_id = fc['PartitionKey']
        chunk_id = fc['RowKey']
        if not fc['PartitionKey'] in jobs_with_failed_chunks:
            jobs_with_failed_chunks[job_id] = {
                'chunks': [chunk_id], 'failedCount': 1}
        else:
            jobs_with_failed_chunks[job_id]['chunks'].append(chunk_id)
            jobs_with_failed_chunks[job_id]['failedCount'] += 1

    for job_id in jobs_with_failed_chunks.keys():
        logging.info(f'sending failure stats for {job_id}')
        job = stats_table.get(job_id, 'prime')
        existing_failed_chunks = job['failedChunks'] if 'failedChunks' in job else ''

        ids = list(filter(None, existing_failed_chunks.split(',')))
        to_add_ids = jobs_with_failed_chunks[job_id]['chunks']

        logging.info(f'checking existing ids: {ids}')
        if sorted(ids) == sorted(to_add_ids):
            logging.info('nothing to update here')
            continue
        else:
            chunk_ids = list(set(ids) | set(to_add_ids))
            chunk_ids_comma_list = ','.join(str(c) for c in chunk_ids)

        logging.info(f'adding in these chunks {chunk_ids} to failure list')
        update_job = {}
        chunk_count = len(chunk_ids)

        if chunk_count > 0:
            update_job['status'] = TenableStatus.failed.value

        update_job.update({
            'failedChunks': chunk_ids_comma_list,
            'failedChunkCount': chunk_count
        })
        result = stats_table.merge(job_id, 'prime', update_job)
        logging.info(result)


def main(name) -> str:
    stats_table = ExportsTableStore(connection_string, stats_table_name)
    assets_table = ExportsTableStore(
        connection_string, assets_export_table_name)
    vuln_table = ExportsTableStore(connection_string, vuln_export_table_name)

    generate_finished_stats(assets_table, stats_table)
    generate_finished_stats(vuln_table, stats_table)

    generate_failed_stats(assets_table, stats_table)
    generate_failed_stats(vuln_table, stats_table)

    generate_processing_stats(assets_table, stats_table)
    generate_processing_stats(vuln_table, stats_table)
    return True
