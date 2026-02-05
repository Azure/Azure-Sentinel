import logging
import os

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableStatus

connection_string = os.environ["AzureWebJobsStorage"]
assets_export_table_name = ExportsTableNames.TenableAssetExportTable.value
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value
compliance_export_table_name = ExportsTableNames.TenableComplianceExportTable.value
was_asset_export_table_name = ExportsTableNames.TenableWASAssetExportTable.value
was_vuln_export_table_name = ExportsTableNames.TenableWASVulnExportTable.value
ingest_compliance_data = True if os.environ.get("ComplianceDataIngestion", "False").lower() == "true" else False
ingest_was_asset_data = True if os.environ.get("WASAssetDataIngestion", "False").lower() == "true" else False
ingest_was_vuln_data = True if os.environ.get("WASVulnerabilityDataIngestion", "False").lower() == "true" else False
logs_starts_with = "TenableVM"
function_name = "TenableCleanUpTables"


def process_finished_chunks_by_job_id(chunks) -> dict:
    """Process chunks data and create dictionary for finished chunks by job id.

    Args:
        chunks (list): list of chunks.

    Returns:
        dict: Finished chunks by job id
    """
    finished_chunks_by_job_id = {}
    queued_chunks_by_job_id = {}
    for f in chunks:
        job_id = f["PartitionKey"]
        chunk_id = f["RowKey"]
        status = f["jobStatus"]
        if status in [TenableStatus.finished.value, TenableStatus.expired.value]:
            if f["PartitionKey"] not in finished_chunks_by_job_id:
                finished_chunks_by_job_id[job_id] = [("delete", {"PartitionKey": job_id, "RowKey": chunk_id})]
            else:
                finished_chunks_by_job_id[job_id].append(("delete", {"PartitionKey": job_id, "RowKey": chunk_id}))
        elif status == TenableStatus.queued.value:
            if f["PartitionKey"] not in queued_chunks_by_job_id:
                queued_chunks_by_job_id[job_id] = [("queued", {"PartitionKey": job_id, "RowKey": chunk_id})]
            else:
                queued_chunks_by_job_id[job_id].append(("queued", {"PartitionKey": job_id, "RowKey": chunk_id}))
    for job_id in queued_chunks_by_job_id.keys():
        if finished_chunks_by_job_id.get(job_id):
            del finished_chunks_by_job_id[job_id]
            logging.info(
                f"{logs_starts_with} {function_name}:"
                f" Skipping job id for which the chunks are yet to be processed. {job_id}"
            )
    return finished_chunks_by_job_id


def remove_finished_chunks(table_client: ExportsTableStore):
    """
    Removes finished chunks from the given table client.

    :param table_client: The ExportsTableStore instance to use for deleting chunks.
    :type table_client: ExportsTableStore
    """
    all_chunks = table_client.query_for_all_queued_finished_and_expired_chunks()
    logging.info(f"Total chunk count {all_chunks}")
    finished_chunks_by_job_id = process_finished_chunks_by_job_id(all_chunks)

    logging.info(f"{logs_starts_with} {function_name}: {finished_chunks_by_job_id}")

    batch_size = 50
    for j in finished_chunks_by_job_id.keys():
        batches = [
            finished_chunks_by_job_id[j][i: i + batch_size]
            for i in range(0, len(finished_chunks_by_job_id[j]), batch_size)
        ]
        for batch in batches:
            logging.info(f"{logs_starts_with} {function_name}: Deleting batch")
            table_client.batch(batch)


def main(name: str) -> str:
    """This function deletes finished chunks from the asset, vuln, and compliance tables.

    :return: True
    """
    assets_table = ExportsTableStore(connection_string, assets_export_table_name)
    vuln_table = ExportsTableStore(connection_string, vuln_export_table_name)
    logging.info(f"{logs_starts_with} {function_name}: Batch deleting finished chunks from asset table.")
    remove_finished_chunks(assets_table)
    logging.info(f"{logs_starts_with} {function_name}: Batch deleting finished chunks from vuln table.")
    remove_finished_chunks(vuln_table)
    if ingest_compliance_data:
        compliance_table = ExportsTableStore(connection_string, compliance_export_table_name)
        logging.info(f"{logs_starts_with} {function_name}: Batch deleting finished chunks from compliance table.")
        remove_finished_chunks(compliance_table)
    if ingest_was_asset_data:
        was_assets_table = ExportsTableStore(connection_string, was_asset_export_table_name)
        logging.info(f"{logs_starts_with} {function_name}: Batch deleting finished chunks from WAS asset table.")
        remove_finished_chunks(was_assets_table)
    if ingest_was_vuln_data:
        was_vuln_table = ExportsTableStore(connection_string, was_vuln_export_table_name)
        logging.info(f"{logs_starts_with} {function_name}: Batch deleting finished chunks from WAS Vuln table.")
        remove_finished_chunks(was_vuln_table)
    return "True"
