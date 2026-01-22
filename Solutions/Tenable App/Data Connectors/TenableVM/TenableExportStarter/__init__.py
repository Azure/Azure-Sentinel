"""Export Starter file."""

import logging
import os
from datetime import datetime, timezone
from ..exports_store import ExportsTableStore, ExportsTableNames

import azure.functions as func
import azure.durable_functions as df

connection_string = os.environ["AzureWebJobsStorage"]
checkpoint_table_name = ExportsTableNames.TenableExportCheckpointTable.value
stats_table_name = ExportsTableNames.TenableExportStatsTable.value
assets_export_table_name = ExportsTableNames.TenableAssetExportTable.value
vuln_export_table_name = ExportsTableNames.TenableVulnExportTable.value
compliance_export_table_name = ExportsTableNames.TenableComplianceExportTable.value
was_assets_export_table_name = ExportsTableNames.TenableWASAssetExportTable.value
was_vuln_export_table_name = ExportsTableNames.TenableWASVulnExportTable.value
ingest_compliance_data = True if os.environ.get("ComplianceDataIngestion", "False").lower() == "true" else False
ingest_was_asset_data = True if os.environ.get("WASAssetDataIngestion", "False").lower() == "true" else False

ingest_was_vulnerability_data = (
    True if os.environ.get("WASVulnerabilityDataIngestion", "False").lower() == "true" else False
)


export_orchestrator_function_name = "TenableExportsOrchestrator"
cleanup_orchestrator_function_name = "TenableCleanUpOrchestrator"
asset_download_chunk_orchestrator_function_name = (
    "TenableAssetDownloadChunkOrchestrator"
)
vuln_download_chunk_orchestrator_function_name = (
    "TenableVulnDownloadChunkOrchestrator"
)
compliance_download_chunk_orchestrator_function_name = (
    "TenableComplianceDownloadChunkOrchestrator"
)
was_asset_download_chunk_orchestrator_function_name = (
    "TenableWASAssetDownloadChunkOrchestrator"
)
was_vuln_download_chunk_orchestrator_function_name = "TenableWASVulnDownloadChunkOrchestrator"
logs_starts_with = "TenableVM"
function_name = "TenableExportStarter"


async def start_new_orchestrator(client, orchestrator_function_name, instance_id_key, orchestrator_client_data=None):
    """
    Start a new instance of an orchestrator function and record its instance_id in the stats table.

    :param client: The durable orchestration client.
    :param orchestrator_function_name: The name of the orchestrator function to start.
    :param instance_id_key: The key to use when storing the instance_id in the stats table.
    :param orchestrator_client_data: Optional client data to pass to the orchestrator function.
    :return: The instance_id of the newly started orchestrator function.
    """
    stats_table = ExportsTableStore(connection_string, stats_table_name)
    instance_id = await client.start_new(orchestrator_function_name, None, orchestrator_client_data)
    logging.info(
        f"{logs_starts_with} {function_name}: Started {orchestrator_function_name}"
        f" orchestration with ID = '{instance_id}'."
    )
    stats_table.merge("main", "current", {instance_id_key: instance_id})
    return instance_id


def first_run_setup():
    """
    Perform setup tasks for the first run of the TenableExportStarter function.

    This function sets up the necessary resources (tables) for the other functions to run.
    It also records that the first run has been completed in the stats table.
    It initializes the checkpoint with 0 timestamp values for all the data types.
    """
    logging.info(f"{logs_starts_with} {function_name}: First run detected...")
    logging.info(f"{logs_starts_with} {function_name}: Setting up the following resources:")
    logging.info(stats_table_name)
    logging.info(assets_export_table_name)
    logging.info(vuln_export_table_name)
    if ingest_compliance_data:
        logging.info(compliance_export_table_name)
    if ingest_was_asset_data:
        logging.info(was_assets_export_table_name)
    if ingest_was_vulnerability_data:
        logging.info(was_vuln_export_table_name)
    logging.info(checkpoint_table_name)

    stats_table = ExportsTableStore(connection_string, stats_table_name)
    stats_table.create()

    checkpoint_table = ExportsTableStore(connection_string, checkpoint_table_name)
    checkpoint_table.create()

    asesets_table = ExportsTableStore(connection_string, assets_export_table_name)
    asesets_table.create()

    vuln_table = ExportsTableStore(connection_string, vuln_export_table_name)
    vuln_table.create()

    compliance_table = ExportsTableStore(connection_string, compliance_export_table_name)
    compliance_table.create()
    was_assets_table = ExportsTableStore(connection_string, was_assets_export_table_name)
    was_assets_table.create()

    was_vuln_table = ExportsTableStore(connection_string, was_vuln_export_table_name)
    was_vuln_table.create()
    stats_table.post(
        "main",
        "current",
        {
            "exportsInstanceId": "",
            "cleanupInstanceId": "",
            "assetdownloadchunkInstanceId": "",
            "vulndownloadchunkInstanceId": "",
            "wasassetdownloadchunkInstanceId": "",
            "wasvulnsdownloadchunkInstanceId": "",
            "isFirstRun": False,
        },
    )

    checkpoint_table.post("assets", "timestamp", {"assets_timestamp": 0})

    checkpoint_table.post("vulns", "timestamp", {"vulns_timestamp": 0})

    checkpoint_table.post("compliance", "timestamp", {"compliance_timestamp": 0})

    checkpoint_table.post("was_asset", "timestamp", {"was_asset_timestamp": 0})

    checkpoint_table.post("was_vulns", "timestamp", {"was_vulns_timestamp": 0})


async def check_and_create_new_orchestrator(
    client,
    job_info,
    orchestrator_instance_id,
    orchestrator_function_name,
    orchestrator_client_data=None,
):
    """
    Check if an existing singleton orchestrator instance is already running, and if not, start a new one.

    Parameters:
        client (DurableOrchestrationClient): The client to use to interact with the durable orchestration service.
        job_info (dict): The current job info dictionary from the stats table in the exports table store.
        orchestrator_instance_id (str): The key in the stats table where the instance id of the orchestrator is stored.
        orchestrator_function_name (str): The name of the orchestrator function to start a new instance of.
        orchestrator_client_data (dict, optional): The client data to pass to the orchestrator function
        when starting a new instance.

    Returns:
        str: The instance id of the newly started orchestrator function if a new instance was started,
        otherwise the existing instance id.
    """
    logging.info(
        f"{logs_starts_with} {function_name}: Checking if an existing {orchestrator_function_name} instance was found."
    )
    singleton_instance_id = job_info[orchestrator_instance_id] if orchestrator_instance_id in job_info else ""
    logging.info(f"{logs_starts_with} {function_name}: {orchestrator_instance_id} value: {singleton_instance_id}")
    if singleton_instance_id != "":
        logging.info(
            f"{logs_starts_with} {function_name}: Located an existing orchestrator instance: {singleton_instance_id}"
        )
        existing_instance = await client.get_status(singleton_instance_id)
        logging.info(f"{logs_starts_with} {function_name}: Existing Instance : {existing_instance}")
        logging.info(
            f"{logs_starts_with} {function_name}: Existing Instance Status: {existing_instance.runtime_status}"
        )

        if existing_instance is None or existing_instance.runtime_status in [
            df.OrchestrationRuntimeStatus.Completed,
            df.OrchestrationRuntimeStatus.Failed,
            df.OrchestrationRuntimeStatus.Terminated,
            None,
        ]:
            new_instance_id = await start_new_orchestrator(
                client,
                orchestrator_function_name,
                orchestrator_instance_id,
                orchestrator_client_data,
            )
            logging.info(f"{logs_starts_with} {function_name}: Started new instance -- {new_instance_id}")
        else:
            logging.info(
                f"{logs_starts_with} {function_name}: {orchestrator_function_name} job is already currently running."
                " Will try again later."
            )
    else:
        logging.info(f"{logs_starts_with} {function_name}: Not a first run, but no instance id found yet.")
        logging.info(f"{logs_starts_with} {function_name}: Starting new instance id.")
        new_instance_id = await start_new_orchestrator(
            client,
            orchestrator_function_name,
            orchestrator_instance_id,
            orchestrator_client_data,
        )
        logging.info(f"{logs_starts_with} {function_name}: Started new instance -- {new_instance_id}")


async def main(mytimer: func.TimerRequest, starter: str) -> None:
    """
    Run the main entry point for the Azure Function App timer trigger for TenableVM exports.

    It runs on a schedule and checks if an instance of the TenableExportsOrchestrator is already running.
    If not, it starts a new instance. If there is an existing instance it simply exits.
    It also starts instances of the TenableCleanUpOrchestrator and DownloadChunkOrchestrator
    for all the different types.
    If this is the first run it sets up the necessary resources (tables) for the other functions to run.
    """
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    logging.info(f"{logs_starts_with} {function_name}: Python timer trigger function ran at {utc_timestamp}")

    client = df.DurableOrchestrationClient(starter)

    store = ExportsTableStore(connection_string=connection_string, table_name=stats_table_name)
    logging.info(f"{logs_starts_with} {function_name}: Looking in table storage for running instance")
    job_info = store.get("main", "current")
    logging.info(f"{logs_starts_with} {function_name}: Results from table storage: {job_info}")

    if job_info is not None:
        await check_and_create_new_orchestrator(
            client,
            job_info,
            "exportsInstanceId",
            export_orchestrator_function_name,
            {"isFirstRun": False},
        )
        await check_and_create_new_orchestrator(
            client, job_info, "cleanupInstanceId", cleanup_orchestrator_function_name
        )
        await check_and_create_new_orchestrator(
            client,
            job_info,
            "assetdownloadchunkInstanceId",
            asset_download_chunk_orchestrator_function_name,
        )
        await check_and_create_new_orchestrator(
            client, job_info, "vulndownloadchunkInstanceId", vuln_download_chunk_orchestrator_function_name
        )
        if ingest_compliance_data:
            await check_and_create_new_orchestrator(
                client,
                job_info,
                "compliancedownloadchunkInstanceId",
                compliance_download_chunk_orchestrator_function_name,
            )
        if ingest_was_asset_data:
            await check_and_create_new_orchestrator(
                client,
                job_info,
                "wasassetdownloadchunkInstanceId",
                was_asset_download_chunk_orchestrator_function_name,
            )
        if ingest_was_vulnerability_data:
            await check_and_create_new_orchestrator(
                client,
                job_info,
                "wasvulnsdownloadchunkInstanceId",
                was_vuln_download_chunk_orchestrator_function_name,
            )
    else:
        first_run_setup()
        await start_new_orchestrator(
            client,
            export_orchestrator_function_name,
            "exportsInstanceId",
            {"isFirstRun": True},
        )
        await start_new_orchestrator(client, cleanup_orchestrator_function_name, "cleanupInstanceId")
        await start_new_orchestrator(
            client,
            asset_download_chunk_orchestrator_function_name,
            "assetdownloadchunkInstanceId",
        )
        await start_new_orchestrator(
            client, vuln_download_chunk_orchestrator_function_name, "vulndownloadchunkInstanceId"
        )
        if ingest_compliance_data:
            await start_new_orchestrator(
                client,
                compliance_download_chunk_orchestrator_function_name,
                "compliancedownloadchunkInstanceId",
            )
        if ingest_was_asset_data:
            await start_new_orchestrator(
                client,
                was_asset_download_chunk_orchestrator_function_name,
                "wasassetdownloadchunkInstanceId",
            )
        if ingest_was_vulnerability_data:
            await start_new_orchestrator(
                client,
                was_vuln_download_chunk_orchestrator_function_name,
                "wasvulnsdownloadchunkInstanceId",
            )
        return None
