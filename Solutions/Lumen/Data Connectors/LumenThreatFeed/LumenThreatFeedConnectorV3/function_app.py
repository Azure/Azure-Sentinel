import logging
import os
import uuid
import json
from datetime import datetime
import azure.functions as func
import azure.durable_functions as df
from azure.storage.blob import BlobServiceClient
import requests
import ijson
from main import LumenSetup, MSALSetup, LumenSentinelUpdater, INDICATOR_TYPES

app = func.FunctionApp()

# Configuration constants
CONFIDENCE_THRESHOLD = int(os.environ.get('LUMEN_CONFIDENCE_THRESHOLD', '60'))
BLOB_CONTAINER = os.environ.get('LUMEN_BLOB_CONTAINER', 'lumenti')

def _get_blob_client():
    conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
    if not conn:
        raise ValueError('LUMEN_BLOB_CONNECTION_STRING not set')
    svc = BlobServiceClient.from_connection_string(conn)
    return svc.get_container_client(BLOB_CONTAINER)

def _stream_and_filter_to_blob(container, indicator_type, url, run_id):
    blob_name = f'{run_id}-{indicator_type}.jsonl'
    total_count, filtered_count = 0, 0
    
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()
        blob_client = container.get_blob_client(blob_name)
        
        with blob_client.get_blob_client().open("wb") as blob_file:
            for item in ijson.items(resp.iter_content(chunk_size=8192), 'item'):
                total_count += 1
                confidence = item.get('confidence', 0)
                if confidence >= CONFIDENCE_THRESHOLD:
                    filtered_count += 1
                    blob_file.write((json.dumps(item) + '\n').encode())
    
    return {
        'blob_name': blob_name, 
        'indicator_type': indicator_type, 
        'total_indicators': total_count,
        'filtered_indicators': filtered_count
    }

@app.route(route="starter", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
@app.durable_client_input(client_name="client")
def http_starter(req: func.HttpRequest, client) -> func.HttpResponse:
    try:
        run_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:6]
        logging.info(f"HTTP V3 run {run_id} triggered")
        
        lumen_setup = LumenSetup(os.environ.get('LUMEN_API_KEY'), os.environ.get('LUMEN_BASE_URL'), 3)
        msal_setup = MSALSetup(os.environ.get('TENANT_ID'), os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'), os.environ.get('WORKSPACE_ID'))
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        presigned = updater.get_lumen_presigned_urls(INDICATOR_TYPES)
        
        container = _get_blob_client()
        sources = []
        for itype, url in presigned.items():
            info = _stream_and_filter_to_blob(container, itype, url, run_id)
            sources.append(info)
        
        config = {
            'LUMEN_API_KEY': os.environ.get('LUMEN_API_KEY'),
            'LUMEN_BASE_URL': os.environ.get('LUMEN_BASE_URL'),
            'CLIENT_ID': os.environ.get('CLIENT_ID'),
            'CLIENT_SECRET': os.environ.get('CLIENT_SECRET'),
            'TENANT_ID': os.environ.get('TENANT_ID'),
            'WORKSPACE_ID': os.environ.get('WORKSPACE_ID'),
            'CONFIDENCE_THRESHOLD': CONFIDENCE_THRESHOLD,
            'RUN_ID': run_id,
            'BLOB_CONTAINER': BLOB_CONTAINER
        }
        
        input_data = {'blob_sources': sources, 'config': config, 'indicators_per_request': 100}
        instance_id = client.start_new('orchestrator_function', input_data)
        logging.info(f"HTTP started orchestration {instance_id}")
        
        return func.HttpResponse(f"Orchestration started: {instance_id}", status_code=202)
    except Exception as e:
        logging.error(f"HTTP starter V3 error: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.timer_trigger(schedule="0 30 8 * * *", arg_name="mytimer", run_on_startup=False, use_monitor=False)
@app.durable_client_input(client_name="client")
def timer_starter(mytimer: func.TimerRequest, client) -> None:
    try:
        run_id = datetime.utcnow().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:6]
        logging.info(f"Timer V3 run {run_id} triggered")
        
        lumen_setup = LumenSetup(os.environ.get('LUMEN_API_KEY'), os.environ.get('LUMEN_BASE_URL'), 3)
        msal_setup = MSALSetup(os.environ.get('TENANT_ID'), os.environ.get('CLIENT_ID'), os.environ.get('CLIENT_SECRET'), os.environ.get('WORKSPACE_ID'))
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        presigned = updater.get_lumen_presigned_urls(INDICATOR_TYPES)
        
        container = _get_blob_client()
        sources = []
        for itype, url in presigned.items():
            info = _stream_and_filter_to_blob(container, itype, url, run_id)
            sources.append(info)
        
        config = {
            'LUMEN_API_KEY': os.environ.get('LUMEN_API_KEY'),
            'LUMEN_BASE_URL': os.environ.get('LUMEN_BASE_URL'),
            'CLIENT_ID': os.environ.get('CLIENT_ID'),
            'CLIENT_SECRET': os.environ.get('CLIENT_SECRET'),
            'TENANT_ID': os.environ.get('TENANT_ID'),
            'WORKSPACE_ID': os.environ.get('WORKSPACE_ID'),
            'CONFIDENCE_THRESHOLD': CONFIDENCE_THRESHOLD,
            'RUN_ID': run_id,
            'BLOB_CONTAINER': BLOB_CONTAINER
        }
        
        input_data = {'blob_sources': sources, 'config': config, 'indicators_per_request': 100}
        instance_id = client.start_new('orchestrator_function', input_data)
        logging.info(f"Timer started orchestration {instance_id}")
    except Exception as e:
        logging.error(f"Timer starter V3 error: {e}")

@app.orchestration_trigger(context_name="context")
def orchestrator_function(context):
    try:
        input_data = context.get_input()
        blob_sources = input_data['blob_sources']
        config = input_data['config']
        indicators_per_request = input_data.get('indicators_per_request', 100)
        
        logging.info(f"Orchestrator V3 starting with {len(blob_sources)} blob sources")
        
        # Create work units for parallel processing
        work_units = []
        for source in blob_sources:
            estimated_batches = max(1, source['filtered_indicators'] // indicators_per_request)
            for batch_idx in range(estimated_batches):
                work_units.append({
                    'blob_name': source['blob_name'],
                    'indicator_type': source['indicator_type'],
                    'batch_index': batch_idx,
                    'indicators_per_request': indicators_per_request,
                    'config': config
                })
        
        logging.info(f"Created {len(work_units)} work units for processing")
        
        # Process work units with dynamic pacing
        results = []
        batch_size = 5  # Start with small batches
        total_throttle_events = 0
        
        for i in range(0, len(work_units), batch_size):
            batch = work_units[i:i+batch_size]
            
            # Execute batch in parallel
            batch_tasks = [context.call_activity('activity_upload_from_blob', unit) for unit in batch]
            batch_results = yield context.task_all(batch_tasks)
            
            # Collect results and count throttle events
            batch_throttles = sum(result.get('throttle_events', 0) for result in batch_results)
            total_throttle_events += batch_throttles
            results.extend(batch_results)
            
            # Adaptive pacing based on throttle events
            if batch_throttles > 0:
                # Slow down if we're hitting rate limits
                batch_size = max(1, batch_size - 1)
                yield context.create_timer(context.current_utc_datetime.add(seconds=30))
                logging.info(f"Throttling detected ({batch_throttles} events), reducing batch size to {batch_size}")
            elif batch_throttles == 0 and batch_size < 10:
                # Speed up if no throttling
                batch_size = min(10, batch_size + 1)
        
        # Cleanup blobs
        cleanup_tasks = [context.call_activity('activity_cleanup_blob', {'blob_name': source['blob_name'], 'config': config}) for source in blob_sources]
        yield context.task_all(cleanup_tasks)
        
        # Aggregate results
        total_uploaded = sum(result.get('uploaded_count', 0) for result in results)
        total_errors = sum(result.get('error_count', 0) for result in results)
        
        final_result = {
            'run_id': config['RUN_ID'],
            'total_uploaded': total_uploaded,
            'total_errors': total_errors,
            'total_throttle_events': total_throttle_events,
            'work_units_processed': len(work_units),
            'blob_sources_processed': len(blob_sources)
        }
        
        logging.info(f"Orchestration V3 completed: {final_result}")
        return final_result
        
    except Exception as e:
        logging.error(f"Orchestrator V3 error: {e}")
        raise

@app.activity_trigger(input_name="work_unit")
def activity_upload_from_blob(work_unit):
    try:
        from main import LumenSetup, MSALSetup, LumenSentinelUpdater
        
        config = work_unit['config']
        blob_name = work_unit['blob_name']
        batch_index = work_unit['batch_index']
        indicators_per_request = work_unit['indicators_per_request']
        
        # Get blob client
        conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
        if not conn:
            raise ValueError('LUMEN_BLOB_CONNECTION_STRING not set')
        svc = BlobServiceClient.from_connection_string(conn)
        container = svc.get_container_client(config['BLOB_CONTAINER'])
        blob_client = container.get_blob_client(blob_name)
        
        # Download and process blob content
        blob_data = blob_client.download_blob().readall().decode('utf-8')
        lines = blob_data.strip().split('\n')
        
        # Calculate batch slice
        start_idx = batch_index * indicators_per_request
        end_idx = min(start_idx + indicators_per_request, len(lines))
        batch_lines = lines[start_idx:end_idx]
        
        if not batch_lines:
            return {'uploaded_count': 0, 'error_count': 0, 'throttle_events': 0}
        
        # Setup Lumen client
        lumen_setup = LumenSetup(config['LUMEN_API_KEY'], config['LUMEN_BASE_URL'], 3)
        msal_setup = MSALSetup(config['TENANT_ID'], config['CLIENT_ID'], config['CLIENT_SECRET'], config['WORKSPACE_ID'])
        updater = LumenSentinelUpdater(lumen_setup, msal_setup)
        
        # Parse indicators
        indicators = []
        for line in batch_lines:
            if line.strip():
                indicators.append(json.loads(line))
        
        # Upload with retry logic
        uploaded_count = 0
        error_count = 0
        throttle_events = 0
        
        if indicators:
            try:
                result = updater.upload_indicators_to_sentinel(indicators)
                uploaded_count = len(indicators)
                if 'throttled' in str(result).lower():
                    throttle_events = 1
            except Exception as upload_error:
                if '429' in str(upload_error):
                    throttle_events = 1
                error_count = len(indicators)
                logging.error(f"Upload error for batch {batch_index}: {upload_error}")
        
        return {
            'uploaded_count': uploaded_count,
            'error_count': error_count,
            'throttle_events': throttle_events,
            'batch_index': batch_index
        }
        
    except Exception as e:
        logging.error(f"Activity upload error: {e}")
        return {'uploaded_count': 0, 'error_count': 1, 'throttle_events': 0}

@app.activity_trigger(input_name="cleanup_info")
def activity_cleanup_blob(cleanup_info):
    try:
        config = cleanup_info['config']
        blob_name = cleanup_info['blob_name']
        
        conn = os.environ.get('LUMEN_BLOB_CONNECTION_STRING')
        if not conn:
            raise ValueError('LUMEN_BLOB_CONNECTION_STRING not set')
        
        svc = BlobServiceClient.from_connection_string(conn)
        container = svc.get_container_client(config['BLOB_CONTAINER'])
        blob_client = container.get_blob_client(blob_name)
        
        blob_client.delete_blob()
        logging.info(f"Deleted blob: {blob_name}")
        return {'deleted': blob_name}
        
    except Exception as e:
        logging.error(f"Cleanup error for {cleanup_info.get('blob_name', 'unknown')}: {e}")
        return {'error': str(e)}
