import logging
import azure.functions as func
import azure.durable_functions as df
import os
import time
import uuid
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater, INDICATOR_TYPES

# Suppress verbose Azure SDK logging
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
logging.getLogger('azure.storage').setLevel(logging.WARNING)

# Configuration constants
CONFIDENCE_THRESHOLD = int(os.environ.get('LUMEN_CONFIDENCE_THRESHOLD', '60'))
BLOB_CONTAINER = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenthreatfeed')

def _get_blob_container():
    """Get blob container client, creating container if needed."""
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')
    
    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client(BLOB_CONTAINER)
    
    # Create container if it doesn't exist
    try:
        container_client.create_container()
        logging.info(f"Created blob container: {BLOB_CONTAINER}")
    except Exception as e:
        if "ContainerAlreadyExists" in str(e):
            logging.debug(f"Blob container {BLOB_CONTAINER} already exists")
        else:
            logging.warning(f"Error creating container {BLOB_CONTAINER}: {e}")
    
    return container_client

def _cleanup_blob_container(container_client):
    """Clean up stale files in blob storage container."""
    try:
        logging.info("🧹 Starting blob storage housekeeping...")
        
        # List all blobs in the container
        blob_list = list(container_client.list_blobs())
        
        if not blob_list:
            logging.info("✓ Blob container is already clean (no files found)")
            return
        
        deleted_count = 0
        total_size = 0
        
        # Delete all blobs
        for blob in blob_list:
            try:
                # Get blob size for reporting
                blob_size = blob.size if hasattr(blob, 'size') else 0
                total_size += blob_size
                
                # Delete the blob
                container_client.delete_blob(blob.name)
                deleted_count += 1
                logging.debug(f"Deleted blob: {blob.name} ({blob_size:,} bytes)")
                
            except Exception as e:
                logging.warning(f"Failed to delete blob {blob.name}: {e}")
        
        # Convert bytes to MB for reporting
        total_size_mb = total_size / (1024 * 1024)
        
        logging.info(f"✓ Housekeeping complete: deleted {deleted_count:,} files "
                    f"({total_size_mb:.2f} MB freed)")
        
    except Exception as e:
        logging.error(f"✗ Blob housekeeping failed: {e}")
        # Don't fail the entire process if housekeeping fails
        pass

def _generate_run_id() -> str:
    """Generate unique run ID for tracking."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique_id = uuid.uuid4().hex[:6]
    return f"{timestamp}-{unique_id}"

async def main(mytimer: func.TimerRequest, starter: str) -> None:
    """Timer trigger for scheduled threat intelligence updates."""
    try:
        logging.info("=== TIMER TRIGGER FIRED ===")
        logging.info("Starting scheduled Lumen threat feed update...")
        
        # Housekeeping: Clean up any stale files from previous runs
        logging.info("🧹 Performing housekeeping...")
        try:
            container_client = _get_blob_container()
            _cleanup_blob_container(container_client)
        except Exception as e:
            logging.warning(f"Housekeeping failed: {e}")
        
        client = df.DurableOrchestrationClient(starter)
        run_id = _generate_run_id()
        logging.info(f"Generated run ID: {run_id}")
        
        # Get environment configuration
        config = {
            'LUMEN_API_KEY': os.environ.get('LUMEN_API_KEY'),
            'LUMEN_BASE_URL': os.environ.get('LUMEN_BASE_URL'), 
            'TENANT_ID': os.environ.get('TENANT_ID'),
            'CLIENT_ID': os.environ.get('CLIENT_ID'),
            'CLIENT_SECRET': os.environ.get('CLIENT_SECRET'),
            'WORKSPACE_ID': os.environ.get('WORKSPACE_ID')
        }
        
        # Validate required config
        missing_vars = [k for k, v in config.items() if not v]
        if missing_vars:
            logging.error(f"Missing environment variables: {missing_vars}")
            return
        
        # Initialize components
        lumen_setup = LumenSetup(config['LUMEN_API_KEY'], config['LUMEN_BASE_URL'])
        updater = LumenSentinelUpdater(
            lumen_setup,
            MSALSetup(config['TENANT_ID'], config['CLIENT_ID'], 
                     config['CLIENT_SECRET'], config['WORKSPACE_ID'])
        )
        
        updater.log_config()
        
        # Get blob container
        container_client = _get_blob_container()
        
        # Phase 1: Stream data to blob storage
        logging.info("=== PHASE 1: STREAMING TO BLOB STORAGE ===")
        
        # Get presigned URLs
        presigned_urls = updater.get_lumen_presigned_urls(INDICATOR_TYPES)
        
        if not presigned_urls:
            logging.error("No presigned URLs obtained")
            return
        
        # Stream data to blobs
        blob_sources = []
        for indicator_type, presigned_url in presigned_urls.items():
            try:
                result = updater.stream_and_filter_to_blob(
                    container_client, indicator_type, presigned_url, run_id
                )
                blob_sources.append(result)
                logging.info(f"✓ Streamed {indicator_type}: {result['filtered_count']:,} objects")
            except Exception as e:
                logging.error(f"✗ Failed to stream {indicator_type}: {e}")
        
        if not blob_sources:
            logging.error("No data was successfully streamed to blobs")
            return
        
        # Phase 2: Start orchestration for upload
        logging.info("=== PHASE 2: STARTING ORCHESTRATION ===")
        
        orchestration_input = {
            'run_id': run_id,
            'blob_sources': blob_sources,
            'config': config,
            'indicators_per_request': 100,  # Keep at 100 (Sentinel API limit)
            'max_concurrent_activities': 10  # Increased concurrency for performance
        }
        
        instance_id = await client.start_new("orchestrator_function", None, orchestration_input)
        
        logging.info(f"✓ Timer triggered orchestration started: {instance_id}")
        
    except Exception as e:
        logging.error(f"Timer trigger error: {e}", exc_info=True)
