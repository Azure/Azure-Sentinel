import logging
import os
from azure.storage.blob import BlobServiceClient

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
        container_client.create_container()
    except Exception:
        pass  # Container already exists
    
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
        blob_client.delete_blob()
        logging.debug(f"✓ Deleted blob: {blob_name}")
        
        return {'status': 'success', 'blob_name': blob_name}
        
    except Exception as e:
        logging.error(f"Cleanup error for {blob_name}: {e}")
        return {'status': 'error', 'blob_name': blob_name, 'error': str(e)}
