"""Export Orchestrator file."""

import logging
import os
from datetime import timedelta

import azure.durable_functions as df

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableStatus, TenableExportType

connection_string = os.environ["AzureWebJobsStorage"]
ingest_compliance_data = True if os.environ.get("ComplianceDataIngestion", "False").lower() == "true" else False
ingest_was_asset_data = True if os.environ.get("WASAssetDataIngestion", "False").lower() == "true" else False
ingest_was_vulnerability_data = (
    True if os.environ.get("WASVulnerabilityDataIngestion", "False").lower() == "true" else False
)
stats_table_name = ExportsTableNames.TenableExportStatsTable.value
checkpoint_table_name = ExportsTableNames.TenableExportCheckpointTable.value
export_schedule_minutes = int(os.getenv("TenableExportScheduleInMinutes", "1440"))
start_asset_job_name = "TenableStartAssetExportJob"
start_vuln_job_name = "TenableStartVulnExportJob"
asset_orchestrator_name = "TenableAssetExportOrchestrator"
vuln_orchestrator_name = "TenableVulnExportOrchestrator"
start_compliance_job_name = "TenableStartComplianceExportJob"
compliance_orchestrator_name = "TenableComplianceExportOrchestrator"
start_was_asset_job_name = "TenableStartWASAssetExportJob"
was_asset_orchestrator_name = "TenableWASAssetExportOrchestrator"
start_was_vuln_job_name = "TenableStartWASVulnExportJob"
was_vuln_orchestrator_name = "TenableWASVulnExportOrchestrator"
logs_starts_with = "TenableVM"
function_name = "TenableExportsOrchestrator"
stats_store = ExportsTableStore(connection_string, stats_table_name)


def process_data(results, job_types):
    """Process results data and update Stats table.

    Args:
        results (list): Results of sub-orchestrator calls.
    """
    for index in range(len(results)):
        job_finished = results[index]
        job_id = job_finished["id"] if "id" in job_finished else ""
        chunks = job_finished["chunks"] if "chunks" in job_finished else []
        chunk_ids = ",".join(str(c) for c in chunks)
        stats_data = {
            "status": TenableStatus.finished.value,
            "chunks": chunk_ids,
            "totalChunksCount": len(chunks),
        }
        if job_id != "":
            update_stats_table(job_id, stats_data)
            logging.info(f"{logs_starts_with} {function_name}: Updated stats table for {job_types[index]} job {job_id}")


def update_stats_table(pk, data):
    """Update Stats table.

    Args:
        pk (str): The partition key for the Stats table.
        data (dict): The data to be updated in the Stats table.
    """
    stats_store.merge(pk, "prime", data)


def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to handle Tenable.io export jobs.

    It calls activity functions to start asset, vuln and compliance export jobs, and then
    calls sub-orchestrators to process the results of the jobs. It also updates the Stats
    table with the status of the jobs. If user opted for compliance data ingestion, it
    processes compliance job data and updates the Stats table.

    Args:
        context: The durable orchestration context

    Returns:
        None
    """
    logging.info(f"{logs_starts_with} {function_name}: Started main orchestrator")
    logging.info(
        f"{logs_starts_with} {function_name}: instance id: {context.instance_id} at {context.current_utc_datetime}"
    )
    first_run = context.get_input()
    if first_run is not None and "isFirstRun" in first_run and first_run["isFirstRun"]:
        assets_timestamp = 0
        vulns_timestamp = 0
        compliance_timestamp = 0
        was_asset_timestamp = 0
        was_vulns_timestamp = 0
    else:
        checkpoint_store = ExportsTableStore(connection_string, checkpoint_table_name)
        assets_timestamp = checkpoint_store.get("assets", "timestamp").get(
            "assets_timestamp", 0
        )
        vulns_timestamp = checkpoint_store.get("vulns", "timestamp").get(
            "vulns_timestamp", 0
        )
        compliance_timestamp = checkpoint_store.get("compliance", "timestamp").get(
            "compliance_timestamp", 0
        )
        was_asset_timestamp = checkpoint_store.get("was_asset", "timestamp").get(
            "was_asset_timestamp", 0
        )
        was_vulns_timestamp = checkpoint_store.get("was_vulns", "timestamp").get(
            "was_vulns_timestamp", 0
        )
    job_types = []

    logging.info(
        f"{logs_starts_with} {function_name}: Checkpoint timestamp value for assets: {assets_timestamp}"
    )
    asset_start_time = int(context.current_utc_datetime.timestamp())
    asset_export_job_id = yield context.call_activity(start_asset_job_name, assets_timestamp)
    logging.info(f"{logs_starts_with} {function_name}: Retrieved a new asset job ID")
    logging.info(
        f"{logs_starts_with} {function_name}: instance id: {context.instance_id}"
        f" working with asset export job {asset_export_job_id}, sending to sub orchestrator"
    )
    job_types.append("asset")
    asset_stats_data = {
        "status": TenableStatus.processing.value,
        "exportType": TenableExportType.asset.value,
        "failedChunks": "",
        "chunks": "",
        "totalChunksCount": 0,
        "jobTimestamp": assets_timestamp,
        "startedAt": context.current_utc_datetime.timestamp(),
    }
    update_stats_table(asset_export_job_id, asset_stats_data)
    logging.info(
        f"{logs_starts_with} {function_name}: Saved {asset_export_job_id} to stats table. Moving to start vuln job."
    )

    logging.info(
        f"{logs_starts_with} {function_name}: Checkpoint timestamp value for vulns: {vulns_timestamp}"
    )
    vulns_start_time = int(context.current_utc_datetime.timestamp())
    vuln_export_job_id = yield context.call_activity(start_vuln_job_name, vulns_timestamp)
    logging.info(f"{logs_starts_with} {function_name}: Retrieved a new vuln job ID")
    logging.info(
        f"{logs_starts_with} {function_name}: instance id: f{context.instance_id}"
        f" working with vuln export job {vuln_export_job_id}, sending to sub orchestrator"
    )
    job_types.append("vulns")
    vuln_stats_data = {
        "status": TenableStatus.processing.value,
        "exportType": TenableExportType.vuln.value,
        "failedChunks": "",
        "chunks": "",
        "totalChunksCount": 0,
        "jobTimestamp": vulns_timestamp,
        "startedAt": context.current_utc_datetime.timestamp(),
    }
    update_stats_table(vuln_export_job_id, vuln_stats_data)

    if ingest_compliance_data:
        logging.info(
            f"{logs_starts_with} {function_name}: Checkpoint timestamp value for compliance: {compliance_timestamp}"
        )
        compliance_start_time = int(context.current_utc_datetime.timestamp())
        compliance_export_job_id = yield context.call_activity(start_compliance_job_name, compliance_timestamp)
        logging.info(f"{logs_starts_with} {function_name}: Retrieved a new compliance job ID")
        logging.info(
            f"{logs_starts_with} {function_name}: instance id: {context.instance_id}"
            f" working with compliance export job {compliance_export_job_id}, sending to sub orchestrator"
        )

        logging.info(f"{logs_starts_with} {function_name}: Filter by time for compliance: {compliance_timestamp}")
        job_types.append("compliance")
        compliance_stats_data = {
            "status": TenableStatus.processing.value,
            "exportType": TenableExportType.compliance.value,
            "failedChunks": "",
            "chunks": "",
            "totalChunksCount": 0,
            "jobTimestamp": compliance_timestamp,
            "startedAt": context.current_utc_datetime.timestamp(),
        }
        update_stats_table(compliance_export_job_id, compliance_stats_data)
        logging.info(f"{logs_starts_with} {function_name}: Saved {compliance_export_job_id} to stats table.")
    else:
        logging.info(
            f"{logs_starts_with} {function_name}: User opted not to ingest compliance data."
            " Skipping compliance export job"
        )

    if ingest_was_asset_data:
        logging.info(
            f"{logs_starts_with} {function_name}: Checkpoint timestamp value for was_asset: {was_asset_timestamp}"
        )
        was_asset_start_time = int(context.current_utc_datetime.timestamp())
        was_asset_export_job_id = yield context.call_activity(start_was_asset_job_name, was_asset_timestamp)
        logging.info(f"{logs_starts_with} {function_name}: Retrieved a new WAS assets job ID")
        logging.info(
            f"{logs_starts_with} {function_name}: instance id: {context.instance_id}"
            f" working with WAS assets export job {was_asset_export_job_id}, sending to sub orchestrator"
        )

        logging.info(f"{logs_starts_with} {function_name}: Filter by time for WAS assets: {was_asset_timestamp}")
        job_types.append("was_asset")
        was_asset_stats_data = {
            "status": TenableStatus.processing.value,
            "exportType": TenableExportType.was_asset.value,
            "failedChunks": "",
            "chunks": "",
            "totalChunksCount": 0,
            "jobTimestamp": was_asset_timestamp,
            "startedAt": context.current_utc_datetime.timestamp(),
        }
        update_stats_table(was_asset_export_job_id, was_asset_stats_data)
        logging.info(f"{logs_starts_with} {function_name}: Saved {was_asset_export_job_id} to stats table.")
    else:
        logging.info(
            f"{logs_starts_with} {function_name}: User opted not to ingest WAS asset data."
            " Skipping WAS asset export job"
        )

    if ingest_was_vulnerability_data:
        logging.info(
            f"{logs_starts_with} {function_name}: Checkpoint timestamp value for was_vulns: {was_vulns_timestamp}"
        )
        was_vulns_start_time = int(context.current_utc_datetime.timestamp())
        was_vulns_export_job_id = yield context.call_activity(start_was_vuln_job_name, was_vulns_timestamp)
        logging.info(f"{logs_starts_with} {function_name}: Retrieved a new WAS Vulnerability job ID")
        logging.info(
            f"{logs_starts_with} {function_name}: instance id: {context.instance_id}"
            f" working with WAS Vulnerability export job {was_vulns_export_job_id}, sending to sub orchestrator"
        )

        logging.info(f"{logs_starts_with} {function_name}: Filter by time for WAS Vulnerability: {was_vulns_timestamp}")
        job_types.append("was_vuln")
        was_vuln_stats_data = {
                "status": TenableStatus.processing.value,
                "exportType": TenableExportType.was_vuln.value,
                "failedChunks": "",
                "chunks": "",
                "totalChunksCount": 0,
                "jobTimestamp": was_vulns_timestamp,
                "startedAt": context.current_utc_datetime.timestamp(),
        }
        update_stats_table(was_vulns_export_job_id, was_vuln_stats_data)
        logging.info(f"{logs_starts_with} {function_name}: Saved {was_vulns_export_job_id} to stats table.")
    else:
        logging.info(
            f"{logs_starts_with} {function_name}: User opted not to ingest WAS Vulnerability data data."
            " Skipping WAS Vulnerability export job"
        )

    export_suborchestrator_call = []
    asset_export = context.call_sub_orchestrator(
        asset_orchestrator_name,
        {
            "timestamp": assets_timestamp,
            "assetJobId": asset_export_job_id,
            "mainOrchestratorInstanceId": context.instance_id,
            "start_time": asset_start_time,
        },
    )
    export_suborchestrator_call.append(asset_export)
    update_stats_table(asset_export_job_id, {"status": TenableStatus.sent_to_sub_orchestrator.value})

    vuln_export = context.call_sub_orchestrator(
        vuln_orchestrator_name,
        {
            "timestamp": vulns_timestamp,
            "vulnJobId": vuln_export_job_id,
            "mainOrchestratorInstanceId": context.instance_id,
            "start_time": vulns_start_time,
        },
    )
    export_suborchestrator_call.append(vuln_export)
    update_stats_table(vuln_export_job_id, {"status": TenableStatus.sent_to_sub_orchestrator.value})

    if ingest_compliance_data:
        compliance_export = context.call_sub_orchestrator(
            compliance_orchestrator_name,
            {
                "timestamp": compliance_timestamp,
                "complianceJobId": compliance_export_job_id,
                "mainOrchestratorInstanceId": context.instance_id,
                "start_time": compliance_start_time,
            },
        )
        export_suborchestrator_call.append(compliance_export)
        update_stats_table(compliance_export_job_id, {"status": TenableStatus.sent_to_sub_orchestrator.value})
    else:
        logging.info(
            f"{logs_starts_with} {function_name}: User opted not to ingest compliance data."
            " Skipping compliance export sub orchestrator call."
        )

    if ingest_was_asset_data:
        was_asset_export = context.call_sub_orchestrator(
            was_asset_orchestrator_name,
            {
                "timestamp": was_asset_timestamp,
                "wasassetJobId": was_asset_export_job_id,
                "mainOrchestratorInstanceId": context.instance_id,
                "start_time": was_asset_start_time,
            },
        )
        export_suborchestrator_call.append(was_asset_export)
        update_stats_table(was_asset_export_job_id, {"status": TenableStatus.sent_to_sub_orchestrator.value})
    else:
        logging.info(
            f"{logs_starts_with} {function_name}: User opted not to ingest WAS assets data."
            " Skipping WAS assets export sub orchestrator call."
        )

    if ingest_was_vulnerability_data:
        was_vuln_export = context.call_sub_orchestrator(
            was_vuln_orchestrator_name,
            {
                "timestamp": was_vulns_timestamp,
                "wasVulnJobId": was_vulns_export_job_id,
                "mainOrchestratorInstanceId": context.instance_id,
                "start_time": was_vulns_start_time,
            },
        )
        export_suborchestrator_call.append(was_vuln_export)
        update_stats_table(was_vulns_export_job_id, {"status": TenableStatus.sent_to_sub_orchestrator.value})
    else:
        logging.info(
            f"{logs_starts_with} {function_name}: User opted not to ingest WAS vulnerability data."
            " Skipping WAS vulnerability export sub orchestrator call."
        )

    results = yield context.task_all(export_suborchestrator_call)
    logging.info(f"{logs_starts_with} {function_name}: Finished all jobs! Results: {results}")
    # process job data
    process_data(results, job_types)

    next_check = context.current_utc_datetime + timedelta(minutes=export_schedule_minutes)
    logging.info(f"{logs_starts_with} {function_name}: Next check at time: {next_check}")
    yield context.create_timer(next_check)
    yield context.continue_as_new(None)


main = df.Orchestrator.create(orchestrator_function)
