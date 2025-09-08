"""
Lumen Threat Intelligence Connector - Starter Function (Chunked Version)

This function serves as the HTTP endpoint to initiate the durable orchestration
for uploading threat intelligence data from Lumen to Microsoft Sentinel.

Flow:
1. Download threat intelligence data from Lumen API
2. Split data into chunks and upload each chunk to Azure Blob Storage
3. Start durable orchestration for parallel chunk processing
4. Return status URLs for monitoring progress

"""

import logging
import azure.functions as func
import azure.durable_functions as df
import os
import json
import traceback
import uuid
from azure.storage.blob import BlobServiceClient
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    HTTP starter function to begin the durable orchestration for Lumen threat intelligence upload (chunked).
    
    This function:
    1. Downloads threat intelligence data from Lumen API for all indicator types
    2. Splits the data into chunks and uploads each chunk to Azure Blob Storage
    3. Starts a durable orchestration that processes the data in parallel chunks
    4. Returns HTTP response with orchestration status URLs for monitoring
    
    Args:
        req (func.HttpRequest): The HTTP request (POST to trigger the process)
        starter (str): Durable Functions orchestration client binding
        
    Returns:
        func.HttpResponse: Response with orchestration status URLs or error message
    """
    try:
        logging.info("Starting Lumen Threat Intelligence upload orchestration (chunked)")
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
            logging.info(f"About to download {indicator_type} threat data from presigned URL")
            threat_data = updater.get_lumen_threat_data(presigned_url)
            logging.info(f"Successfully downloaded {indicator_type} threat data from Lumen. Data size: {len(str(threat_data))} characters")
            
            # Extract STIX objects and add to combined list
            stix_objects = threat_data.get('stixobjects', []) if isinstance(threat_data, dict) else threat_data
            if stix_objects:
                all_threat_data.extend(stix_objects)
                logging.info(f"Added {len(stix_objects)} {indicator_type} indicators to processing queue")
        
        logging.info(f"Total indicators collected from all types: {len(all_threat_data)}")
        
        # Step 3: Split threat data into chunks and upload each chunk as a separate blob
        blob_service_client = BlobServiceClient.from_connection_string(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
        container_name = "lumen-threat-data"
        chunk_size = 100  # Number of indicators per chunk/blob (Sentinel API limit: 100 objects per request)

        # Use the combined threat data from all indicator types
        indicators = all_threat_data
        # TESTING LIMIT: Uncomment the next line to limit to 1000 indicators for testing
        max_indicators = None  # Set to None to process all indicators
        if max_indicators and len(indicators) > max_indicators:
            indicators = indicators[:max_indicators]
            logging.info(f"LIMITED TO FIRST {max_indicators} indicators for testing")
        
        total_indicators = len(indicators)
        logging.info(f"Found {total_indicators} STIX objects to chunk")
        blob_names = []
        for i in range(0, total_indicators, chunk_size):
            chunk = indicators[i:i+chunk_size]
            chunk_blob_name = f"stix-chunk-{uuid.uuid4()}.json"
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=chunk_blob_name)
            blob_client.upload_blob(json.dumps(chunk), overwrite=True)
            blob_names.append(chunk_blob_name)
            logging.info(f"Uploaded chunk {len(blob_names)}: {container_name}/{chunk_blob_name} ({len(chunk)} indicators)")
        logging.info(f"Uploaded {len(blob_names)} chunks to blob storage.")

        # Calculate estimated completion time
        # Factors: Sentinel API rate limit (~95 requests/minute), parallel processing, chunk size
        parallel_chunk_size = 10  # From input_data below
        total_chunks = len(blob_names)
        estimated_requests_per_minute = 95  # Sentinel API rate limit
        estimated_chunks_per_minute = min(estimated_requests_per_minute, parallel_chunk_size * 60 / 10)  # Assume ~10 seconds per chunk group
        estimated_total_minutes = total_chunks / estimated_chunks_per_minute
        
        logging.info(f"📊 Processing Summary:")
        logging.info(f"   Total indicators: {total_indicators}")
        logging.info(f"   Total chunks: {total_chunks}")
        logging.info(f"   Parallel processing: {parallel_chunk_size} chunks at a time")
        logging.info(f"   Estimated completion time: {estimated_total_minutes:.1f} minutes")
        logging.info(f"   (Actual time may vary based on API response times and system load)")

        # Step 4: Prepare configuration for the orchestrator
        config = {
            'LUMEN_API_KEY': os.environ.get("LUMEN_API_KEY"),
            'LUMEN_BASE_URL': os.environ.get("LUMEN_BASE_URL"),
            'CLIENT_ID': os.environ.get("CLIENT_ID"),
            'CLIENT_SECRET': os.environ.get("CLIENT_SECRET"),
            'TENANT_ID': os.environ.get("TENANT_ID"),
            'WORKSPACE_ID': os.environ.get("WORKSPACE_ID")
        }

        # Step 5: Prepare input data for the orchestrator (list of blob names)
        input_data = {
            'blob_container': container_name,
            'blob_names': blob_names,  # List of chunked blob names
            'config': config,
            'parallel_chunk_size': parallel_chunk_size  # Use the same value from estimation
        }

        # Step 6: Start the durable orchestration
        logging.info("About to start durable orchestration (chunked)")
        instance_id = await client.start_new('orchestrator_function', None, input_data)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")

        # Step 7: Return HTTP response with status URLs
        return client.create_check_status_response(req, instance_id)

    except Exception as e:
        logging.error(f"Starter function error: {e}")
        logging.error(traceback.format_exc())
        return func.HttpResponse(
            f"Error starting orchestration: {str(e)}",
            status_code=500
        )
