import logging
import os
import json
import ijson
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater


def main(params: dict) -> dict:
    """Process a work unit of threat data from a temp file and upload to Sentinel.

    Confidence filtering is applied inline with a fixed threshold (60). Indicators
    with a confidence value below 60 are skipped before batching.
    """
    file_path = params["file_path"]
    indicator_type = params["indicator_type"]
    start_offset = params.get("start_offset", 0)
    max_indicators = params.get("max_indicators", 1000)
    work_unit_id = params.get("work_unit_id", "unknown")
    config = params["config"]
    indicators_per_request = params.get("indicators_per_request", 100)
    min_confidence = 60  # Fixed confidence threshold

    try:
        logging.info(f"Processing work unit {work_unit_id}: {file_path} (offset: {start_offset}, max: {max_indicators})")

        if not os.path.exists(file_path):
            return {"success": False, "indicators_uploaded": 0, "requests_made": 0, "work_unit_id": work_unit_id, "error": f"Temp file not found: {file_path}"}

        lumen_setup = LumenSetup(api_key=config["LUMEN_API_KEY"], base_url=config["LUMEN_BASE_URL"], tries=3)
        msal_setup = MSALSetup(tenant_id=config["TENANT_ID"], client_id=config["CLIENT_ID"], client_secret=config["CLIENT_SECRET"], workspace_id=config["WORKSPACE_ID"])
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        if not updater.bearer_token:
            updater.bearer_token, updater.token_expiry_seconds = updater.acquire_token()

        indicators_uploaded = 0
        requests_made = 0
        current_index = 0
        chunk = []

        logging.debug(f"Reading {indicator_type} (offset {start_offset}, max {max_indicators}) (confidence>=60)")
        with open(file_path, 'rb') as f:
            for stix_object in ijson.items(f, 'stixobjects.item'):
                if current_index < start_offset:
                    current_index += 1
                    continue
                if max_indicators >= 0 and indicators_uploaded >= max_indicators:
                    break

                # Confidence filter
                if stix_object.get('type') == 'indicator':
                    conf = stix_object.get('confidence')
                    if conf is not None:
                        try:
                            if int(conf) < min_confidence:
                                current_index += 1
                                continue
                        except (ValueError, TypeError):
                            pass  # keep object

                chunk.append(stix_object)
                current_index += 1

                if len(chunk) >= indicators_per_request:
                    upload_result = upload_chunk_to_sentinel(chunk, indicator_type, updater, requests_made + 1)
                    if not upload_result['success']:
                        return {"success": False, "indicators_uploaded": indicators_uploaded, "requests_made": requests_made, "work_unit_id": work_unit_id, "error": upload_result['error']}
                    indicators_uploaded += len(chunk)
                    requests_made += 1
                    chunk = []

            if chunk:
                upload_result = upload_chunk_to_sentinel(chunk, indicator_type, updater, requests_made + 1)
                if not upload_result['success']:
                    return {"success": False, "indicators_uploaded": indicators_uploaded, "requests_made": requests_made, "work_unit_id": work_unit_id, "error": upload_result['error']}
                indicators_uploaded += len(chunk)
                requests_made += 1

        logging.info(f"Work unit {work_unit_id} processed {indicators_uploaded} {indicator_type} indicators in {requests_made} requests")
        return {"success": True, "indicators_uploaded": indicators_uploaded, "requests_made": requests_made, "work_unit_id": work_unit_id, "indicator_type": indicator_type}

    except Exception as e:
        logging.error(f"Activity error processing {indicator_type} from {file_path} (work unit {work_unit_id}): {e}")
        return {"success": False, "indicators_uploaded": 0, "requests_made": 0, "work_unit_id": work_unit_id, "error": str(e)}


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
