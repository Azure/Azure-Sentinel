import logging
import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from azure.core.exceptions import ResourceNotFoundError

# Suppress verbose Azure SDK HTTP logs
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
logging.getLogger('azure.storage').setLevel(logging.ERROR)

def _get_blob_container():
    """Get blob container client, creating container if needed."""
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING environment variable not set')
    
    container_name = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenthreatfeed')

    service_client = BlobServiceClient.from_connection_string(conn)
    container_client = service_client.get_container_client(container_name)
    
    # Create container if it doesn't exist
    try:
        if not container_client.exists():
            container_client.create_container()
            logging.info(f"Created blob container: {container_name}")
    except ResourceExistsError:
        pass  # Container already exists (race)
    except Exception as e:
        logging.warning(f"Error ensuring container {container_name}: {e}")
    
    return container_client

def main(cleanup_info):
    """Activity function to cleanup processed blob files."""
    try:
        blob_name = cleanup_info['blob_name']
        run_id = cleanup_info['run_id']
        
        logging.debug(f"Cleaning up blob: {blob_name}")
        
        container_client = _get_blob_container()
        blob_client = container_client.get_blob_client(blob_name)
        
        # Delete the blob
        try:
            blob_client.delete_blob()
        except ResourceNotFoundError:
            # Already deleted by a concurrent worker or a previous attempt – treat as success
            logging.debug(f"Blob not found during cleanup (already deleted): {blob_name}")
        logging.debug(f"✓ Deleted blob: {blob_name}")
        
        return {'status': 'success', 'blob_name': blob_name}
        
    except Exception as e:
        logging.error(f"Cleanup error for {blob_name}: {e}")
        return {'status': 'error', 'blob_name': blob_name, 'error': str(e)}
