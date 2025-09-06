"""
Lumen Threat Intelligence Connector - Timer Starter Function

This function serves as a timer-triggered entry point to initiate the durable orchestration
for uploading threat intelligence data from Lumen to Microsoft Sentinel.

Schedule: 0 0 8 * * * (configurable in function.json)

"""

import logging
import azure.functions as func
import azure.durable_functions as df
import os
import json
import traceback
import tempfile
import glob
import time
from ..main import LumenSetup, MSALSetup, LumenSentinelUpdater
import ijson
import requests
root_logger = logging.getLogger()
root_logger.handlers[0].setFormatter(logging.Formatter("%(name)s: %(message)s"))

def cleanup_existing_temp_files():
    """
    Clean up any existing temporary files from previous runs.
       
    Returns:
        int: Number of files cleaned up
    """
    temp_dir = tempfile.gettempdir()
    pattern = os.path.join(temp_dir, 'lumen-threat-*.json')
    
    try:
        existing_files = glob.glob(pattern)
        cleaned_count = 0
        
        for file_path in existing_files:
            try:
                os.unlink(file_path)
                cleaned_count += 1
                logging.debug(f"[Timer Trigger] Cleaned up existing temp file: {os.path.basename(file_path)}")
            except Exception as e:
                logging.warning(f"[Timer Trigger] Failed to remove temp file {file_path}: {e}")
        
        if cleaned_count > 0:
            logging.debug(f"[Timer Trigger] Startup cleanup completed: {cleaned_count} old temp files removed")
        else:
            logging.debug("[Timer Trigger] Startup cleanup: No old temp files found")
            
        return cleaned_count
        
    except Exception as e:
        logging.error(f"[Timer Trigger] Error during startup cleanup: {e}")
        return 0

def download_threat_data_to_shared_disk(updater, indicator_types, max_indicators=None):
    """
    Returns list of temp file paths for the orchestrator to coordinate.
    """
    presigned_urls = updater.get_lumen_presigned_urls(indicator_types)
    temp_file_paths = []
    total_indicators_downloaded = 0
    
    for indicator_type, presigned_url in presigned_urls.items():
        # Check if we've already reached the limit
        if max_indicators and total_indicators_downloaded >= max_indicators:
            logging.debug(f"[Timer Trigger] SKIPPING {indicator_type} indicators - already reached limit of {max_indicators}")
            break
            
        logging.info(f"[Timer Trigger] Downloading {indicator_type} data to shared disk...")
        
        try:
            # Create temporary file for this indicator type
            temp_file = tempfile.NamedTemporaryFile(mode='w+b', delete=False, 
                                                  suffix=f'-{indicator_type}.json',
                                                  prefix='lumen-threat-')
            temp_file_path = temp_file.name
            
            # Stream download to disk
            response = requests.get(presigned_url, stream=True)
            response.raise_for_status()
            
            # Write response to disk in chunks
            downloaded_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
                    downloaded_bytes += len(chunk)
            
            temp_file.close()
            response.close()
            
            # Quick count of indicators in this file (for logging only)
            with open(temp_file_path, 'rb') as f:
                indicator_count = 0
                
                try:
                    for stix_obj in ijson.items(f, 'stixobjects.item'):
                        indicator_count += 1
                        
                        if max_indicators and total_indicators_downloaded + indicator_count >= max_indicators:
                            break
                except:
                    # If counting fails, just log what we downloaded
                    indicator_count = 0
            
            temp_file_paths.append({
                'file_path': temp_file_path,
                'indicator_type': indicator_type,
                'downloaded_bytes': downloaded_bytes,
                'estimated_indicators': indicator_count
            })
            
            total_indicators_downloaded += indicator_count
            
            logging.debug(f"[Timer Trigger] Downloaded {indicator_type}: {downloaded_bytes} bytes, ~{indicator_count} indicators to {temp_file_path}")
            
        except Exception as e:
            logging.error(f"[Timer Trigger] Failed to download {indicator_type}: {str(e)}")
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            continue
    
    logging.info(f"[Timer Trigger] Download complete. Total files: {len(temp_file_paths)}, Total indicators downloaded: ~{total_indicators_downloaded}")
    return temp_file_paths, total_indicators_downloaded

async def main(mytimer: func.TimerRequest, starter: str) -> None:
    """
    Timer starter function to begin the durable orchestration for Lumen threat intelligence upload (Parallel Batch Processing).
    
    This function runs on a timer schedule and uses the same parallel batch processing
    architecture as the HTTP starter function for optimal performance.
    
    Architecture:
    - Downloads threat data to temporary disk files
    - Processes 3 work units simultaneously in parallel batches
    - Targets 95 requests/minute for optimal API utilization
    - Each batch completes in ~18.9 seconds
    """
    try:
        start_time = time.time()
        logging.info("[Timer Trigger] Starting Lumen Threat Intelligence upload orchestration...")
        
        # Step 0: Clean up any existing temp files from previous runs
        cleanup_existing_temp_files()
        
        client = df.DurableOrchestrationClient(starter)

        # Configure Lumen API client settings
        lumen_setup = LumenSetup(
            api_key=os.environ.get("LUMEN_API_KEY"),
            base_url=os.environ.get("LUMEN_BASE_URL"),
            tries=3
        )
        msal_setup = MSALSetup(
            tenant_id=os.environ.get("TENANT_ID"),
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET"),
            workspace_id=os.environ.get("WORKSPACE_ID")
        )
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)

        # Step 1: Download all threat data to shared disk
        from ..main import INDICATOR_TYPES
        max_indicators = None  # Limited for timer-based processing
        logging.debug("[Timer Trigger] Downloading threat data to shared disk for orchestrator processing...")
        
        temp_file_paths, total_indicators = download_threat_data_to_shared_disk(
            updater, 
            INDICATOR_TYPES, 
            max_indicators
        )
        logging.debug(f"[Timer Trigger] Download complete. Files: {len(temp_file_paths)}, Total indicators downloaded: ~{total_indicators}")

        # Calculate estimated completion time based on parallel batch processing
        # Process 3 work units simultaneously, targeting 95 req/min
        max_indicators_per_work_unit = 1000  # Indicators per work unit
        work_unit_count = sum(
            (file_info['estimated_indicators'] + max_indicators_per_work_unit - 1) // max_indicators_per_work_unit
            for file_info in temp_file_paths
        )
        
        # Each work unit makes ~10 API requests (1000 indicators / 100 per request)
        # Parallel batches: 3 work units = ~30 requests per batch
        # Target rate: 95 requests/minute = 1.583 req/sec
        # Each batch target time: ~18.9 seconds (30 requests / 1.583 req/sec)
        batch_size = 3
        batch_count = (work_unit_count + batch_size - 1) // batch_size  # Round up division
        batch_interval_seconds = 18.9  # Target 18.9 seconds per batch (95 req/min)
        estimated_total_seconds = batch_count * batch_interval_seconds
        estimated_total_minutes = estimated_total_seconds / 60
        
        total_requests = total_indicators / 100  # 100 indicators per request
        
        logging.debug(f"[Timer Trigger] 📊 Processing Summary:")
        logging.debug(f"[Timer Trigger]    Total indicators downloaded: ~{total_indicators}")
        logging.debug(f"[Timer Trigger]    Work units: {work_unit_count} (max {max_indicators_per_work_unit} indicators each)")
        logging.debug(f"[Timer Trigger]    Parallel batches: {batch_count} batches of {batch_size} work units")
        logging.debug(f"[Timer Trigger]    Total API requests: ~{total_requests:.0f}")
        logging.debug(f"[Timer Trigger]    Processing: Parallel batches (targeting 95 req/min)")
        logging.debug(f"[Timer Trigger]    Estimated completion time: {estimated_total_minutes:.1f} minutes")

        # Step 2: Prepare configuration for the orchestrator
        config = {
            'LUMEN_API_KEY': os.environ.get("LUMEN_API_KEY"),
            'LUMEN_BASE_URL': os.environ.get("LUMEN_BASE_URL"),
            'CLIENT_ID': os.environ.get("CLIENT_ID"),
            'CLIENT_SECRET': os.environ.get("CLIENT_SECRET"),
            'TENANT_ID': os.environ.get("TENANT_ID"),
            'WORKSPACE_ID': os.environ.get("WORKSPACE_ID")
        }

        # Step 3: Prepare input data for the orchestrator (list of temp file paths)
        indicators_per_request = 100  # Sentinel API limit
        
        input_data = {
            'temp_file_paths': temp_file_paths,  # List of temp files with threat data
            'config': config,
            'indicators_per_request': indicators_per_request
        }

        # Step 4: Start the durable orchestration with temp file paths
        logging.info("[Timer Trigger] Starting durable orchestration with downloaded threat data files...")
        instance_id = await client.start_new('orchestrator_function', None, input_data)
        logging.info(f"[Timer Trigger] Started orchestration with ID = '{instance_id}'.")

        # Calculate elapsed time and log completion summary
        elapsed_time = time.time() - start_time
        elapsed_minutes = elapsed_time / 60
        logging.debug(f"[Timer Trigger] 🎯 Operation Started Successfully:")
        logging.debug(f"[Timer Trigger]    Total indicators queued for upload: ~{total_indicators}")
        logging.debug(f"[Timer Trigger]    Elapsed time for initialization: {elapsed_time:.2f} seconds ({elapsed_minutes:.2f} minutes)")
        logging.debug(f"[Timer Trigger]    Orchestration ID: {instance_id}")
        logging.debug(f"[Timer Trigger]    Status: Threat intelligence upload orchestration initiated")

        # Memory cleanup: Clear data structures
        del temp_file_paths
        del input_data

    except Exception as e:
        logging.error(f"[Timer Trigger] Starter function error: {e}")
        logging.error(traceback.format_exc())
