import logging
import os
import json
import ijson
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater


def main(params: dict) -> dict:
    """
    Durable Functions activity to process a work unit of threat data from disk and upload to Microsoft Sentinel.
    
    This function reads a subset of STIX objects from a temp file on disk, processes them in chunks,
    and uploads each chunk to Sentinel API with proper formatting.
    
    Args:
        params (dict): Activity input parameters containing:
            - file_path (str): Path to temp file containing threat data
            - indicator_type (str): Type of indicators (e.g., 'malware-hash', 'domain')
            - start_offset (int): Starting position in the file (number of indicators to skip)
            - max_indicators (int): Maximum number of indicators to process in this work unit
            - work_unit_id (str): Unique identifier for this work unit
            - config (dict): Configuration containing API keys and endpoints
            - indicators_per_request (int): Number of indicators per Sentinel API request (100)
    
    Returns:
        dict: Processing result containing:
            - success (bool): Whether processing was successful
            - indicators_uploaded (int): Number of indicators successfully uploaded
            - requests_made (int): Number of API requests made to Sentinel
            - work_unit_id (str): The work unit identifier
            - error (str, optional): Error message if processing failed
    """
    file_path = params["file_path"]
    indicator_type = params["indicator_type"]
    start_offset = params.get("start_offset", 0)
    max_indicators = params.get("max_indicators", 1000)
    work_unit_id = params.get("work_unit_id", "unknown")
    config = params["config"]
    indicators_per_request = params.get("indicators_per_request", 100)

    try:
        logging.info(f"Processing work unit {work_unit_id}: {file_path} (offset: {start_offset}, max: {max_indicators})")
        
        # Check if file exists
        if not os.path.exists(file_path):
            logging.error(f"Temp file not found: {file_path}")
            return {
                "success": False,
                "indicators_uploaded": 0,
                "requests_made": 0,
                "work_unit_id": work_unit_id,
                "error": f"Temp file not found: {file_path}"
            }
        
        # Initialize Lumen and Microsoft authentication components
        lumen_setup = LumenSetup(
            api_key=config["LUMEN_API_KEY"],
            base_url=config["LUMEN_BASE_URL"],
            tries=3
        )
        msal_setup = MSALSetup(
            tenant_id=config["TENANT_ID"],
            client_id=config["CLIENT_ID"],
            client_secret=config["CLIENT_SECRET"],
            workspace_id=config["WORKSPACE_ID"]
        )
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        
        # Acquire token for Sentinel API
        if not updater.bearer_token:
            updater.bearer_token, updater.token_expiry_seconds = updater.acquire_token()
        
        # Process file in streaming chunks with offset and limit
        indicators_uploaded = 0
        requests_made = 0
        current_index = 0
        chunk_objects = []
        
        logging.debug(f"Reading {indicator_type} data from disk using streaming parser (offset: {start_offset}, max: {max_indicators})...")
        
        with open(file_path, 'rb') as f:
            # Use ijson to stream from disk file
            for stix_object in ijson.items(f, 'stixobjects.item'):
                # Skip objects until we reach the start offset
                if current_index < start_offset:
                    current_index += 1
                    continue
                
                # Stop if we've processed the max number of objects
                if indicators_uploaded >= max_indicators:
                    break
                
                chunk_objects.append(stix_object)
                current_index += 1
                
                # When we have a full chunk, upload it immediately
                if len(chunk_objects) >= indicators_per_request:
                    upload_result = upload_chunk_to_sentinel(
                        chunk_objects, 
                        indicator_type, 
                        updater, 
                        requests_made + 1
                    )
                    
                    if upload_result['success']:
                        indicators_uploaded += len(chunk_objects)
                        requests_made += 1
                        logging.debug(f"Work unit {work_unit_id}: Uploaded chunk {requests_made} for {indicator_type}: {len(chunk_objects)} indicators (total: {indicators_uploaded})")
                    else:
                        logging.error(f"Work unit {work_unit_id}: Failed to upload chunk for {indicator_type}: {upload_result['error']}")
                        return {
                            "success": False,
                            "indicators_uploaded": indicators_uploaded,
                            "requests_made": requests_made,
                            "work_unit_id": work_unit_id,
                            "error": upload_result['error']
                        }
                    
                    chunk_objects = []  # Clear memory immediately
            
            # Upload any remaining objects
            if chunk_objects:
                upload_result = upload_chunk_to_sentinel(
                    chunk_objects, 
                    indicator_type, 
                    updater, 
                    requests_made + 1
                )
                
                if upload_result['success']:
                    indicators_uploaded += len(chunk_objects)
                    requests_made += 1
                    logging.debug(f"Work unit {work_unit_id}: Uploaded final chunk for {indicator_type}: {len(chunk_objects)} indicators (total: {indicators_uploaded})")
                else:
                    logging.error(f"Work unit {work_unit_id}: Failed to upload final chunk for {indicator_type}: {upload_result['error']}")
                    return {
                        "success": False,
                        "indicators_uploaded": indicators_uploaded,
                        "requests_made": requests_made,
                        "work_unit_id": work_unit_id,
                        "error": upload_result['error']
                    }
        
        logging.info(f"Work unit {work_unit_id} completed processing {indicator_type}: {indicators_uploaded} indicators in {requests_made} requests")
        
        return {
            "success": True,
            "indicators_uploaded": indicators_uploaded,
            "requests_made": requests_made,
            "work_unit_id": work_unit_id,
            "indicator_type": indicator_type
        }

    except Exception as e:
        logging.error(f"Activity error processing {indicator_type} from {file_path} (work unit {work_unit_id}): {e}")
        return {
            "success": False,
            "indicators_uploaded": 0,
            "requests_made": 0,
            "work_unit_id": work_unit_id,
            "error": str(e)
        }


def upload_chunk_to_sentinel(stix_objects, indicator_type, updater, request_number):
    """
    Upload a chunk of STIX objects to Sentinel API with proper formatting.
    
    Args:
        stix_objects (list): List of STIX objects to upload
        indicator_type (str): Type of indicators being uploaded
        updater (LumenSentinelUpdater): Configured Sentinel API client
        request_number (int): Request number for logging
    
    Returns:
        dict: Upload result with success status and error message if applicable
    """
    try:
        # Upload directly to Sentinel
        response = updater.upload_stix_objects_to_sentinel(updater.bearer_token, stix_objects)
        
        if response.status_code == 200:
            return {"success": True}
        else:
            return {
                "success": False, 
                "error": f"Sentinel API returned status code: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload error for {indicator_type} request {request_number}: {str(e)}"
        }
