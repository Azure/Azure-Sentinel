import logging
import os

from ..exports_store import ExportsTableStore, ExportsTableNames

connection_string = os.environ['AzureWebJobsStorage']
assets_export_table_name = ExportsTableNames.TenableAssetExportTable.value
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value


def remove_finished_chunks(table_client: ExportsTableStore):
    finished_jobs = table_client.query_for_all_finished_chunks()
    finished_chunks_by_job_id = {}

    for f in finished_jobs:
        job_id = f['PartitionKey']
        chunk_id = f['RowKey']
        if not f['PartitionKey'] in finished_chunks_by_job_id:
            finished_chunks_by_job_id[job_id] = [('delete',
                                                  {'PartitionKey': job_id, 'RowKey': chunk_id})]
        else:
            finished_chunks_by_job_id[job_id].append(('delete',
                                                      {'PartitionKey': job_id, 'RowKey': chunk_id}))
    logging.info(finished_chunks_by_job_id)

    batch_size = 50
    for j in finished_chunks_by_job_id.keys():
        batches = [finished_chunks_by_job_id[j][i:i + batch_size]
                   for i in range(0, len(finished_chunks_by_job_id[j]), batch_size)]
        for batch in batches:
            logging.info('deleting batch')
            table_client.batch(batch)


def main(name: str) -> str:
    assets_table = ExportsTableStore(
        connection_string, assets_export_table_name)
    vuln_table = ExportsTableStore(connection_string, vuln_export_table_name)
    logging.info('batch deleting finished chunks from asset table.')
    remove_finished_chunks(assets_table)
    logging.info('batch deleting finished chunks from vuln table.')
    remove_finished_chunks(vuln_table)
    return True
