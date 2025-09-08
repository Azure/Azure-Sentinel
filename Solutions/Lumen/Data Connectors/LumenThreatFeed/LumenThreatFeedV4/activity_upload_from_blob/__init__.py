import logging
import json
import os
import sys
from azure.storage.blob import BlobServiceClient

# Add parent directory to path for importing main module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import LumenSentinelUpdater, LumenSetup, MSALSetup


def _get_blob_container():
    """Get blob container client, creating container if needed."""
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')

    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client('lumenthreatfeed')

    # Create container if it doesn't exist
    try:
        container_client.create_container()
    except Exception:
        pass  # Container already exists

    return container_client


def main(work_unit):
    """Activity uploads indicators from the given blob to Sentinel.

    Supports batched processing via start_batch/num_batches to keep activity runtime bounded.
    """
    # Extract parameters
    blob_name = work_unit['blob_name']
    indicator_type = work_unit['indicator_type']
    batch_index = work_unit.get('batch_index', 0)
    indicators_per_request = work_unit.get('indicators_per_request', 100)
    start_batch = work_unit.get('start_batch')
    num_batches = work_unit.get('num_batches')
    config = work_unit['config']
    run_id = work_unit['run_id']
    work_unit_id = work_unit['work_unit_id']
    process_all = work_unit.get('process_all', False)

    logging.debug(f"Processing work unit: {work_unit_id}")

    uploaded_total = 0
    error_total = 0
    throttle_total = 0
    batch_objects = None  # for error reporting

    try:
        # Initialize updater
        updater = LumenSentinelUpdater(
            LumenSetup(config['LUMEN_API_KEY'], config['LUMEN_BASE_URL'], 3),
            MSALSetup(config['TENANT_ID'], config['CLIENT_ID'], config['CLIENT_SECRET'], config['WORKSPACE_ID'])
        )

        # Get blob and read content
        container_client = _get_blob_container()
        blob_client = container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall().decode('utf-8')

        # Parse JSONL into objects
        all_objects = []
        for line in blob_data.strip().split('\n'):
            if line:
                all_objects.append(json.loads(line))

        if start_batch is not None and num_batches is not None:
            # Process a bounded window of batches
            for b in range(start_batch, start_batch + num_batches):
                start_idx = b * indicators_per_request
                end_idx = min(start_idx + indicators_per_request, len(all_objects))
                chunk = all_objects[start_idx:end_idx]
                if not chunk:
                    break
                result = updater.upload_indicators_to_sentinel(chunk, f"({indicator_type} batch {b + 1})")
                uploaded_total += result.get('uploaded_count', 0)
                error_total += result.get('error_count', 0)
                throttle_total += result.get('throttle_events', 0)
        elif process_all:
            # Back-compat: process the entire blob in chunks
            for i in range(0, len(all_objects), indicators_per_request):
                chunk = all_objects[i:i + indicators_per_request]
                if not chunk:
                    break
                result = updater.upload_indicators_to_sentinel(chunk, f"({indicator_type} batch {i // indicators_per_request + 1})")
                uploaded_total += result.get('uploaded_count', 0)
                error_total += result.get('error_count', 0)
                throttle_total += result.get('throttle_events', 0)
        else:
            # Single batch slice
            start_idx = batch_index * indicators_per_request
            end_idx = min(start_idx + indicators_per_request, len(all_objects))
            batch_objects = all_objects[start_idx:end_idx]
            if not batch_objects:
                logging.debug(f"No objects in batch {batch_index} for {work_unit_id}")
                return {'uploaded_count': 0, 'error_count': 0, 'throttle_events': 0}
            result = updater.upload_indicators_to_sentinel(batch_objects, f"({indicator_type} batch {batch_index + 1})")
            uploaded_total += result.get('uploaded_count', 0)
            error_total += result.get('error_count', 0)
            throttle_total += result.get('throttle_events', 0)

        logging.debug(
            f"✓ Work unit {work_unit_id} completed: uploaded={uploaded_total}, errors={error_total}, throttles={throttle_total}"
        )
        return {'uploaded_count': uploaded_total, 'error_count': error_total, 'throttle_events': throttle_total}

    except Exception as e:
        logging.error(f"Activity error for {work_unit_id}: {e}", exc_info=True)
        return {
            'uploaded_count': 0,
            'error_count': len(batch_objects) if batch_objects else 0,
            'throttle_events': 0,
            'error': str(e)
        }
