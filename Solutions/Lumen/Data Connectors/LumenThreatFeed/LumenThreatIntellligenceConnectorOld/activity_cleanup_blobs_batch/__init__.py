import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from azure.storage.blob import BlobServiceClient

def main(params: dict) -> dict:
    """
    Durable Functions activity to clean up multiple blobs in parallel within a single execution.
    
    This optimized function handles multiple blob deletions simultaneously using ThreadPoolExecutor
    to achieve maximum performance while staying within Azure Functions timeout limits.
    
    Args:
        params (dict): Activity input parameters containing:
            - blob_container (str): Azure Storage container name
            - blob_names (list): List of blob file names to delete
    
    Returns:
        dict: Cleanup result containing:
            - deleted (int): Number of blobs successfully deleted
            - failed (int): Number of blobs that failed to delete
            - total (int): Total number of blobs processed
            - failed_blobs (list): Names of blobs that failed to delete
            - execution_time (float): Time taken to complete the batch
    
    Note:
        This function uses ThreadPoolExecutor to perform deletions in parallel,
        making it much faster than sequential deletion while maintaining reliability.
    """
    blob_names = params["blob_names"]
    blob_container = params["blob_container"]
    
    logging.info(f"Starting batch cleanup of {len(blob_names)} blobs")
    start_time = time.time()
    
    try:
        # Connect to Azure Storage
        blob_service_client = BlobServiceClient.from_connection_string(
            os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        )
        
        # Track results
        deleted_count = 0
        failed_count = 0
        failed_blobs = []
        
        def delete_single_blob(blob_name):
            """Delete a single blob and return result."""
            try:
                blob_client = blob_service_client.get_blob_client(
                    container=blob_container, 
                    blob=blob_name
                )
                blob_client.delete_blob()
                return {'success': True, 'blob_name': blob_name}
            except Exception as e:
                return {'success': False, 'blob_name': blob_name, 'error': str(e)}
        
        # Execute deletions in parallel using ThreadPoolExecutor
        # Use max_workers=20 for optimal balance between performance and resource usage
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(delete_single_blob, blob_names))
        
        # Process results
        for result in results:
            if result['success']:
                deleted_count += 1
            else:
                failed_count += 1
                failed_blobs.append(result['blob_name'])
                logging.warning(f"Failed to delete {result['blob_name']}: {result['error']}")
        
        elapsed_time = time.time() - start_time
        logging.info(f"Batch cleanup completed in {elapsed_time:.2f}s: {deleted_count} deleted, {failed_count} failed")
        
        return {
            'deleted': deleted_count,
            'failed': failed_count,
            'total': len(blob_names),
            'failed_blobs': failed_blobs,
            'execution_time': elapsed_time
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logging.error(f"Batch cleanup failed after {elapsed_time:.2f}s: {str(e)}", exc_info=True)
        return {
            'deleted': 0,
            'failed': len(blob_names),
            'total': len(blob_names),
            'failed_blobs': blob_names,
            'execution_time': elapsed_time,
            'error': str(e)
        }
