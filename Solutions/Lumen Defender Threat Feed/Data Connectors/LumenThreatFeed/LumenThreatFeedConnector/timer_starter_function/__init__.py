import logging
import json
import azure.functions as func
import azure.durable_functions as df
import os
import time
import uuid
import sys
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

# Add parent directory to path for importing main module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import LumenSetup, MSALSetup, LumenSentinelUpdater, INDICATOR_TYPES, MAX_TOTAL_INDICATORS

# Suppress verbose Azure SDK logging (avoid 409 ContainerAlreadyExists noise)
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
logging.getLogger('azure.storage').setLevel(logging.ERROR)

# Configuration constants
CONFIDENCE_THRESHOLD = int(os.environ.get('LUMEN_CONFIDENCE_THRESHOLD', '80'))
BLOB_CONTAINER = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenthreatfeed')

def _get_blob_container():
    """Get blob container client, creating container if needed."""
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')
    
    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client(BLOB_CONTAINER)
    
    # Create container if it doesn't exist (avoid 409 by probing first)
    try:
        if not container_client.exists():
            container_client.create_container()
            logging.info(f"Created blob container: {BLOB_CONTAINER}")
        else:
            logging.debug(f"Blob container already present: {BLOB_CONTAINER}")
    except ResourceExistsError:
        # Race: another worker created it after our exists() check
        logging.debug(f"Blob container {BLOB_CONTAINER} already exists (race)")
    except Exception as e:
        logging.warning(f"Error ensuring container {BLOB_CONTAINER}: {e}")
    
    return container_client

def _cleanup_blob_container(container_client):
    """Clean up stale files in blob storage container."""
    try:
        logging.debug("🧹 Starting blob storage housekeeping...")
        
        # List all blobs in the container
        blob_list = list(container_client.list_blobs())
        
        if not blob_list:
            logging.debug("✓ Blob container is already clean (no files found)")
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
        
        logging.debug(f"✓ Housekeeping complete: deleted {deleted_count:,} files "
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
        logging.debug("🧹 Performing housekeeping...")
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

        # Stream data to blobs with optional global cap
        blob_sources = []  # flattened list of chunk descriptors
        remaining_total = MAX_TOTAL_INDICATORS if MAX_TOTAL_INDICATORS > 0 else None
        for indicator_type, presigned_url in presigned_urls.items():
            try:
                # Calculate per-type max_remaining for this call
                per_call_remaining = remaining_total if remaining_total is not None else None
                chunks = updater.stream_and_filter_to_blob(
                    container_client, indicator_type, presigned_url, run_id, max_remaining=per_call_remaining
                )
                blob_sources.extend(chunks)
                total_filtered = sum(c.get('filtered_count', 0) for c in chunks)
                logging.info(f"✓ Streamed {indicator_type}: {total_filtered:,} objects in {len(chunks)} chunk(s)")
                # Decrement global remaining budget
                if remaining_total is not None:
                    remaining_total = max(0, remaining_total - total_filtered)
                    if remaining_total == 0:
                        logging.info("Reached MAX_TOTAL_INDICATORS limit; stopping further streaming")
                        break
            except Exception as e:
                logging.error(f"✗ Failed to stream {indicator_type}: {e}")
        
        if not blob_sources:
            logging.error("No data was successfully streamed to blobs")
            return

        # Write a compact manifest containing only the fields needed for upload
        manifest_name = f"{run_id}-manifest.json"
        manifest_items = [
            {
                'blob_name': s['blob_name'],
                'indicator_type': s.get('indicator_type', 'unknown')
            }
            for s in blob_sources
        ]
        try:
            manifest_client = container_client.get_blob_client(manifest_name)
            manifest_client.upload_blob(json.dumps(manifest_items).encode('utf-8'), overwrite=True)
            logging.info(f"✓ Wrote manifest: {manifest_name} ({len(manifest_items)} items)")
        except Exception as e:
            logging.error(f"Failed to write manifest {manifest_name}: {e}")
            return
        
        # Phase 2: Start orchestration for upload
        logging.info("=== PHASE 2: STARTING ORCHESTRATION ===")
        
        orchestration_input = {
            'run_id': run_id,
            # pass manifest pointer instead of full list
            'manifest_blob_name': manifest_name,
            # keep payload minimal; activities read config from environment
            'indicators_per_request': 100,  # Keep at 100 (Sentinel API limit)
            'max_concurrent_activities': int(os.environ.get('LUMEN_MAX_CONCURRENT_ACTIVITIES', '10')),
            # paging controls
            'page_offset': 0,
            'page_size': int(os.environ.get('LUMEN_MANIFEST_PAGE_SIZE', '500'))
        }
        
        instance_id = await client.start_new("orchestrator_function", None, orchestration_input)
        
        logging.info(f"✓ Timer triggered orchestration started: {instance_id}")
        
    except Exception as e:
        logging.error(f"Timer trigger error: {e}", exc_info=True)
