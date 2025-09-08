import logging
import os
import json
import gc
from azure.storage.blob import BlobServiceClient
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater


def main(params: dict) -> dict:
    """
    Durable Functions activity to upload a chunk of STIX objects to Microsoft Sentinel.
    
    This function downloads a chunk (list) of STIX objects from blob storage and uploads all objects in the chunk.
    
    Args:
        params (dict): Activity input parameters containing:
            - blob_container (str): Azure Storage container name
            - blob_name (str): Blob file name containing a chunk of threat data (list of STIX objects)
            - config (dict): Configuration containing API keys and endpoints
    
    Returns:
        dict: Upload result containing:
            - status (str|int): 'complete', 'error', or HTTP status code
            - count (int): Number of objects processed in this chunk
            - error (str, optional): Error message if upload failed
    """
    blob_container = params["blob_container"]
    blob_name = params["blob_name"]
    config = params["config"]

    try:
        # Download chunked threat intelligence data from blob storage
        logging.info(f"Downloading chunk from blob storage: {blob_container}/{blob_name}")
        blob_service_client = BlobServiceClient.from_connection_string(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
        blob_client = blob_service_client.get_blob_client(container=blob_container, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        blob_size_mb = len(blob_data) / (1024 * 1024)
        logging.info(f"Downloaded blob data: {blob_size_mb:.2f} MB")
        stix_objects = json.loads(blob_data)
        del blob_data
        total_objects = len(stix_objects)
        logging.info(f"Total STIX objects in chunk: {total_objects}")
        if not stix_objects:
            logging.info(f"Chunk {blob_name} is empty, marking as complete")
            return {"status": "complete", "count": 0}
            
        # Initialize Lumen and Microsoft authentication components
        lumen_setup = LumenSetup(
            api_key=config["LUMEN_API_KEY"],
            base_url=config["LUMEN_BASE_URL"],
            tries=3,
        )
        msal_setup = MSALSetup(
            tenant_id=config["TENANT_ID"],
            client_id=config["CLIENT_ID"],
            client_secret=config["CLIENT_SECRET"],
            workspace_id=config["WORKSPACE_ID"],
        )
        
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        if not updater.bearer_token:
            updater.bearer_token, updater.token_expiry_seconds = updater.acquire_token()
            
        # Log the chunk loaded from blob
        logging.info(f"Loaded {total_objects} STIX objects from chunk {blob_name}")
        
        # Upload the entire chunk as a batch to Sentinel
        logging.info(f"Uploading chunk {blob_name} ({total_objects} objects) to Sentinel...")
        response = updater.upload_stix_objects_to_sentinel(updater.bearer_token, stix_objects)        
        # Handle upload response
        if response.status_code == 200:
            logging.info(f"Successfully uploaded chunk {blob_name} ({total_objects} objects)")
        else:
            logging.error(f"Failed to upload chunk {blob_name}: HTTP {response.status_code}")
        
        # Clean up memory
        del stix_objects
        del updater
        gc.collect()
        
        return {
            "status": response.status_code,
            "count": total_objects
        }
    except Exception as e:
        logging.error(f"Chunk {blob_name} upload failed: {str(e)}", exc_info=True)
        gc.collect()
        return {
            "status": "error",
            "error": str(e),
            "count": 0
        }
