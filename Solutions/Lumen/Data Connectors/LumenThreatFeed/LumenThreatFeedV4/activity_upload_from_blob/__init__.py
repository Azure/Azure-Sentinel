import logging
import json
import os
from azure.storage.blob import BlobServiceClient
from ..main import LumenSentinelUpdater, LumenSetup, MSALSetup

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
    """Activity function to upload indicators from blob storage to Sentinel."""
    try:
        blob_name = work_unit['blob_name']
        indicator_type = work_unit['indicator_type']
        batch_index = work_unit['batch_index']
        indicators_per_request = work_unit['indicators_per_request']
        config = work_unit['config']
        run_id = work_unit['run_id']
        work_unit_id = work_unit['work_unit_id']
        
        logging.debug(f"Processing work unit: {work_unit_id}")
        
        # Initialize updater
        updater = LumenSentinelUpdater(
            LumenSetup(config['LUMEN_API_KEY'], config['LUMEN_BASE_URL'], 3),
            MSALSetup(config['TENANT_ID'], config['CLIENT_ID'], 
                     config['CLIENT_SECRET'], config['WORKSPACE_ID'])
        )
        
        # Get blob container
        container_client = _get_blob_container()
        blob_client = container_client.get_blob_client(blob_name)
        
        # Read all data from blob
        blob_data = blob_client.download_blob().readall().decode('utf-8')
        
        # Parse STIX objects
        all_objects = []
        for line in blob_data.strip().split('\n'):
            if line:
                all_objects.append(json.loads(line))
        
        # Calculate slice for this batch
        start_idx = batch_index * indicators_per_request
        end_idx = min(start_idx + indicators_per_request, len(all_objects))
        batch_objects = all_objects[start_idx:end_idx]
        
        if not batch_objects:
            logging.debug(f"No objects in batch {batch_index} for {work_unit_id}")
            return {'uploaded_count': 0, 'error_count': 0, 'throttle_events': 0}
        
        logging.debug(f"Uploading {len(batch_objects)} objects from {work_unit_id}")
        
        # Upload to Sentinel
        result = updater.upload_indicators_to_sentinel(
            batch_objects, 
            f"({indicator_type} batch {batch_index + 1})"
        )
        
        logging.debug(f"✓ Work unit {work_unit_id} completed: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Activity error for {work_unit_id}: {e}", exc_info=True)
        return {
            'uploaded_count': 0,
            'error_count': len(batch_objects) if 'batch_objects' in locals() else 0,
            'throttle_events': 0,
            'error': str(e)
        }
