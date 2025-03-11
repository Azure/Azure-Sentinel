import logging
import os
from datetime import timedelta
import time

import azure.durable_functions as df

from ..exports_store import ExportsTableStore, ExportsTableNames
from ..tenable_helper import TenableStatus, TenableExportType

connection_string = os.environ["AzureWebJobsStorage"]
ingest_compliance_data = True if os.environ.get("ComplianceDataIngestion", "False").lower() == "true" else False
stats_table_name = ExportsTableNames.TenableExportStatsTable.value
checkpoint_table_name = ExportsTableNames.TenableExportCheckpointTable.value
export_schedule_minutes = int(
    os.getenv("TenableExportScheduleInMinutes", "1440"))
start_asset_job_name = "TenableStartAssetExportJob"
start_vuln_job_name = "TenableStartVulnExportJob"
asset_orchestrator_name = "TenableAssetExportOrchestrator"
vuln_orchestrator_name = "TenableVulnExportOrchestrator"
start_compliance_job_name = "TenableStartComplianceExportJob"
compliance_orchestrator_name = "TenableComplianceExportOrchestrator"



def process_compliance_data(results, stats_store):
    """Process compliance data and update Stats table.

    Args:
        results (list): Results of sub-orchestrator calls.
        stats_store (ExportsTableStore): Object of Stats table to be updated.
    """
    try:
        compliance_job_finished = results[2]
        compliance_id = compliance_job_finished["id"] if "id" in compliance_job_finished else ""
        chunks = compliance_job_finished["chunks"] if "chunks" in compliance_job_finished else [
        ]
        chunk_ids = ",".join(str(c) for c in chunks)
        if compliance_id != "":
            stats_store.merge(compliance_id, "prime", {
                "status": TenableStatus.finished.value,
                "chunks": chunk_ids,
                "totalChunksCount": len(chunks)
            })
    except IndexError as e:
        logging.warning("compliance job returned no results")
        logging.warning(e)

def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("started main orchestrator")
    logging.info(
        f"instance id: f{context.instance_id} at {context.current_utc_datetime}")
    first_run = context.get_input()
    if first_run is not None and "isFirstRun" in first_run and first_run["isFirstRun"]:
        assets_timestamp = 0
        vulns_timestamp = 0
        compliance_timestamp = 0
    else:
        checkpoint_store = ExportsTableStore(connection_string, checkpoint_table_name)
        assets_timestamp = checkpoint_store.get("assets", "timestamp").get("assets_timestamp", 0)
        vulns_timestamp = checkpoint_store.get("vulns", "timestamp").get("vulns_timestamp", 0)
        compliance_timestamp = checkpoint_store.get("compliance", "timestamp").get("compliance_timestamp", 0)

    logging.info("checkpoint timestamp value for assets: %d", assets_timestamp)
    logging.info("checkpoint timestamp value for vulns: %d", vulns_timestamp)

    stats_store = ExportsTableStore(connection_string, stats_table_name)
    asset_start_time = int(time.time())
    asset_export_job_id = yield context.call_activity(start_asset_job_name, assets_timestamp)
    logging.info("retrieved a new asset job ID")
    logging.warning(
        f"instance id: f{context.instance_id} working with asset export job {asset_export_job_id}, sending to sub orchestrator")

    stats_store.merge(asset_export_job_id, "prime", {
        "status": TenableStatus.processing.value,
        "exportType": TenableExportType.asset.value,
        "failedChunks": "",
        "chunks": "",
        "totalChunksCount": 0,
        "jobTimestamp": assets_timestamp,
        "startedAt": context.current_utc_datetime.timestamp()
    })
    logging.info(
        f"saved {asset_export_job_id} to stats table. moving to start vuln job.")
    vulns_start_time = int(time.time())
    vuln_export_job_id = yield context.call_activity(start_vuln_job_name, vulns_timestamp)
    logging.info("retrieved a new vuln job ID")
    logging.warning(
        f"instance id: f{context.instance_id} working with vuln export job {vuln_export_job_id}, sending to sub orchestrator")

    stats_store.merge(vuln_export_job_id, "prime", {
        "status": TenableStatus.processing.value,
        "exportType": TenableExportType.vuln.value,
        "failedChunks": "",
        "chunks": "",
        "totalChunksCount": 0,
        "jobTimestamp": vulns_timestamp,
        "startedAt": context.current_utc_datetime.timestamp()
    })

    if ingest_compliance_data:
        compliance_start_time = int(time.time())
        compliance_export_job_id = yield context.call_activity(start_compliance_job_name, compliance_timestamp)
        logging.info("retrieved a new compliance job ID")
        logging.warning(
            "instance id: {} working with compliance export job {}, sending to sub orchestrator".format(
                context.instance_id, compliance_export_job_id
            )
        )

        logging.info("filter by time for compliance: %d", compliance_timestamp)
        stats_store.merge(compliance_export_job_id, "prime", {
            "status": TenableStatus.processing.value,
            "exportType": TenableExportType.compliance.value,
            "failedChunks": "",
            "chunks": "",
            "totalChunksCount": 0,
            "jobTimestamp": compliance_timestamp,
            "startedAt": context.current_utc_datetime.timestamp()
        })
        logging.info(
            "saved {} to stats table.".format(compliance_export_job_id))
    else:
        logging.info("User opted not to ingest compliance data. Skipping compliance export job")
    asset_export = context.call_sub_orchestrator(asset_orchestrator_name, {
        "timestamp": assets_timestamp,
        "assetJobId": asset_export_job_id,
        "mainOrchestratorInstanceId": context.instance_id,
        "start_time": asset_start_time
    })
    stats_store.merge(asset_export_job_id, "prime", {
        "status": TenableStatus.sent_to_sub_orchestrator.value
    })

    vuln_export = context.call_sub_orchestrator(vuln_orchestrator_name, {
        "timestamp": vulns_timestamp,
        "vulnJobId": vuln_export_job_id,
        "mainOrchestratorInstanceId": context.instance_id,
        "start_time": vulns_start_time
    })
    stats_store.merge(vuln_export_job_id, "prime", {
        "status": TenableStatus.sent_to_sub_orchestrator.value
    })

    if ingest_compliance_data:
        compliance_export = context.call_sub_orchestrator(compliance_orchestrator_name, {
            "timestamp": compliance_timestamp,
            "complianceJobId": compliance_export_job_id,
            "mainOrchestratorInstanceId": context.instance_id,
            "start_time": compliance_start_time
        })
        stats_store.merge(compliance_export_job_id, "prime", {
            "status": TenableStatus.sent_to_sub_orchestrator.value
        })

        results = yield context.task_all([asset_export, vuln_export, compliance_export])
    else:
        logging.info("User opted not to ingest compliance data. Skipping compliance export sub orchestrator call.")
        results = yield context.task_all([asset_export, vuln_export])
    logging.info("Finished all jobs!")
    logging.info(results)

    try:
        asset_job_finished = results[0]
        asset_id = asset_job_finished["id"] if "id" in asset_job_finished else ""
        chunks = asset_job_finished["chunks"] if "chunks" in asset_job_finished else [
        ]
        chunk_ids = ",".join(str(c) for c in chunks)
        if asset_id != "":
            stats_store.merge(asset_id, "prime", {
                "status": TenableStatus.finished.value,
                "chunks": chunk_ids,
                "totalChunksCount": len(chunks)
            })
    except IndexError as e:
        logging.warning("asset job returned no results")
        logging.warning(e)

    try:
        vuln_job_finished = results[1]
        vuln_id = vuln_job_finished["id"] if "id" in vuln_job_finished else ""
        chunks = vuln_job_finished["chunks"] if "chunks" in vuln_job_finished else [
        ]
        chunk_ids = ",".join(str(c) for c in chunks)
        if vuln_id != "":
            stats_store.merge(vuln_id, "prime", {
                "status": TenableStatus.finished.value,
                "chunks": chunk_ids,
                "totalChunksCount": len(chunks)
            })
    except IndexError as e:
        logging.warning("vuln job returned no results")
        logging.warning(e)

    # condition to process compliance job data only if user opted for it
    if ingest_compliance_data:
        process_compliance_data(results, stats_store)

    next_check = context.current_utc_datetime + \
        timedelta(minutes=export_schedule_minutes)
    yield context.create_timer(next_check)
    context.continue_as_new(None)


main = df.Orchestrator.create(orchestrator_function)
