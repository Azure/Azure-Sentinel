"""
Lumen Threat Intelligence Connector - Timer Starter Function (Chunked Version)

This function serves as a timer-triggered entry point to initiate the durable orchestration
for uploading threat intelligence data from Lumen to Microsoft Sentinel.

Schedule: Every hour (for testing)
"""

import logging
import azure.functions as func
import azure.durable_functions as df
import os
import json
import uuid
import traceback
from azure.storage.blob import BlobServiceClient
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater

async def main(mytimer: func.TimerRequest, starter: str) -> None:
    """
    Timer starter function to begin the durable orchestration for Lumen threat intelligence upload (chunked).
    This function runs every hour by default (for testing).
    """
    try:
        logging.info("[Timer Trigger] Starting Lumen Threat Intelligence upload orchestration (chunked)")
        client = df.DurableOrchestrationClient(starter)

        # Configure Lumen API client settings
        lumen_setup = LumenSetup(
            api_key=os.environ.get("LUMEN_API_KEY"),
            base_url=os.environ.get("LUMEN_BASE_URL"),
            tries=3
        )
        msal_setup = MSALSetup(
            tenant_id=os.environ.get("TENANT_ID"),
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET"),
            workspace_id=os.environ.get("WORKSPACE_ID")
        )
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)

        # Step 1: Get presigned URLs from Lumen API for all indicator types
        from ..main import INDICATOR_TYPES
        presigned_urls = updater.get_lumen_presigned_urls(INDICATOR_TYPES)

        # Step 2: Download threat intelligence data from Lumen for all indicator types
        all_threat_data = []
        for indicator_type, presigned_url in presigned_urls.items():
            logging.info(f"[Timer Trigger] Downloading {indicator_type} threat data from presigned URL")
            threat_data = updater.get_lumen_threat_data(presigned_url)
            logging.info(f"[Timer Trigger] Downloaded {indicator_type} threat data. Data size: {len(str(threat_data))} characters")
            stix_objects = threat_data.get('stixobjects', []) if isinstance(threat_data, dict) else threat_data
            if stix_objects:
                all_threat_data.extend(stix_objects)
                logging.info(f"[Timer Trigger] Added {len(stix_objects)} {indicator_type} indicators to processing queue")
        logging.info(f"[Timer Trigger] Total indicators collected: {len(all_threat_data)}")

        # Step 3: Split threat data into chunks and upload each chunk as a separate blob
        blob_service_client = BlobServiceClient.from_connection_string(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
        container_name = "lumen-threat-data"
        chunk_size = 100
        indicators = all_threat_data
        max_indicators = None  # Set to None to process all indicators
        if max_indicators and len(indicators) > max_indicators:
            indicators = indicators[:max_indicators]
            logging.info(f"[Timer Trigger] LIMITED TO FIRST {max_indicators} indicators for testing")
        total_indicators = len(indicators)
        blob_names = []
        for i in range(0, total_indicators, chunk_size):
            chunk = indicators[i:i+chunk_size]
            chunk_blob_name = f"stix-chunk-{uuid.uuid4()}.json"
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=chunk_blob_name)
            blob_client.upload_blob(json.dumps(chunk), overwrite=True)
            blob_names.append(chunk_blob_name)
            logging.info(f"[Timer Trigger] Uploaded chunk {len(blob_names)}: {container_name}/{chunk_blob_name} ({len(chunk)} indicators)")
        logging.info(f"[Timer Trigger] Uploaded {len(blob_names)} chunks to blob storage.")

        # Step 4: Prepare configuration for the orchestrator
        config = {
            'LUMEN_API_KEY': os.environ.get("LUMEN_API_KEY"),
            'LUMEN_BASE_URL': os.environ.get("LUMEN_BASE_URL"),
            'CLIENT_ID': os.environ.get("CLIENT_ID"),
            'CLIENT_SECRET': os.environ.get("CLIENT_SECRET"),
            'TENANT_ID': os.environ.get("TENANT_ID"),
            'WORKSPACE_ID': os.environ.get("WORKSPACE_ID")
        }
        input_data = {
            'blob_container': container_name,
            'blob_names': blob_names,
            'config': config,
            'parallel_chunk_size': 10
        }

        # Step 5: Start the durable orchestration
        logging.info("[Timer Trigger] Starting durable orchestration (chunked)")
        instance_id = await client.start_new('orchestrator_function', None, input_data)
        logging.info(f"[Timer Trigger] Started orchestration with ID = '{instance_id}'.")

    except Exception as e:
        logging.error(f"[Timer Trigger] Starter function error: {e}")
        logging.error(traceback.format_exc())
