import logging
import json
import azure.functions as func
import azure.durable_functions as df
from main import LumenSentinelUpdater, LumenSetup, MSALSetup
from azure.storage.blob import BlobServiceClient
import os

# Create the durable functions blueprint
bp = df.Blueprint()

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

@bp.orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    """Enhanced orchestrator with dynamic work distribution and progress tracking."""
    try:
        input_data = context.get_input()
        
        if not input_data:
            raise ValueError("No input data provided to orchestrator")
        
        blob_sources = input_data.get('blob_sources', [])
        config = input_data.get('config', {})
        run_id = input_data.get('run_id', 'unknown')
        indicators_per_request = input_data.get('indicators_per_request', 100)
        max_concurrent = input_data.get('max_concurrent_activities', 5)
        
        # Calculate work units with better distribution
        work_units = []
        total_estimated_objects = 0
        
        for source in blob_sources:
            filtered_count = source['filtered_count']
            total_estimated_objects += filtered_count
            
            # Calculate number of batches needed
            num_batches = (filtered_count + indicators_per_request - 1) // indicators_per_request
            
            for batch_idx in range(num_batches):
                work_units.append({
                    'blob_name': source['blob_name'],
                    'indicator_type': source['indicator_type'],
                    'batch_index': batch_idx,
                    'indicators_per_request': indicators_per_request,
                    'config': config,
                    'run_id': run_id,
                    'work_unit_id': f"{run_id}-{source['indicator_type']}-{batch_idx:03d}"
                })
        
        total_work_units = len(work_units)
        
        # Process work units in controlled batches
        results = []
        total_throttle_events = 0
        batch_size = max_concurrent
        
        for i in range(0, len(work_units), batch_size):
            batch = work_units[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(work_units) + batch_size - 1) // batch_size
            
            # Execute batch in parallel
            batch_tasks = [
                context.call_activity('activity_upload_from_blob', unit) 
                for unit in batch
            ]
            batch_results = yield context.task_all(batch_tasks)
            results.extend(batch_results)
            
            # Aggregate throttle events
            batch_throttle = sum(r.get('throttle_events', 0) for r in batch_results if r)
            total_throttle_events += batch_throttle
            
            # Log progress every 10 batches or if throttling
            if batch_num % 10 == 0 or batch_throttle > 0 or batch_num == total_batches:
                batch_uploaded = sum(r.get('uploaded_count', 0) for r in batch_results if r)
                total_uploaded_so_far = sum(r.get('uploaded_count', 0) for r in results if r)
                logging.info(f"Progress: Batch {batch_num}/{total_batches} - {total_uploaded_so_far:,} uploaded")
                
            if batch_throttle > 0:
                # Add delay between batches if throttling occurred
                yield context.create_timer(context.current_utc_datetime.replace(second=context.current_utc_datetime.second + 30))
        
        # Cleanup: Remove processed blobs
        cleanup_tasks = [
            context.call_activity('activity_cleanup_blob', {
                'blob_name': source['blob_name'],
                'run_id': run_id,
                'config': config
            })
            for source in blob_sources
        ]
        yield context.task_all(cleanup_tasks)
        
        # Calculate final statistics
        total_uploaded = sum(r.get('uploaded_count', 0) for r in results if r)
        total_errors = sum(r.get('error_count', 0) for r in results if r)
        
        final_result = {
            'run_id': run_id,
            'total_work_units': total_work_units,
            'total_uploaded': total_uploaded,
            'total_errors': total_errors,
            'total_throttle_events': total_throttle_events,
            'blob_sources_processed': len(blob_sources)
        }
        
        logging.info(f"=== ORCHESTRATION COMPLETE ===")
        logging.info(f"Final result: {final_result}")
        
        # For generators with yield, return without value
        context.set_custom_status(final_result)
        return
        
    except Exception as e:
        logging.error(f"Orchestrator error: {type(e).__name__}: {e}", exc_info=True)
        error_result = {
            'run_id': run_id if 'run_id' in locals() else 'unknown',
            'error': str(e),
            'status': 'failed'
        }
        context.set_custom_status(error_result)
        return

@bp.activity_trigger(input_name="work_unit")
def activity_upload_from_blob(work_unit):
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

@bp.activity_trigger(input_name="cleanup_info")
def activity_cleanup_blob(cleanup_info):
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
