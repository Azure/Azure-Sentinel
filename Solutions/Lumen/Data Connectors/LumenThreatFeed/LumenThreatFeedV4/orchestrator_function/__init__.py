import logging
from datetime import timedelta
import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context):
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
        
        # New approach: schedule one activity per blob source; the activity uploads in chunks of 100 internally.
        total_work_units = len(blob_sources)

        activity_inputs = [
            {
                'blob_name': source['blob_name'],
                'indicator_type': source['indicator_type'],
                'indicators_per_request': indicators_per_request,
                'config': config,
                'run_id': run_id,
                'process_all': True,
                'work_unit_id': f"{run_id}-{source['indicator_type']}"
            }
            for source in blob_sources
        ]

        # Execute with limited parallelism
        results = []
        total_throttle_events = 0
        batch_size = max_concurrent
        for i in range(0, len(activity_inputs), batch_size):
            batch = activity_inputs[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(activity_inputs) + batch_size - 1) // batch_size

            batch_tasks = [context.call_activity('activity_upload_from_blob', inp) for inp in batch]
            batch_results = yield context.task_all(batch_tasks)
            results.extend(batch_results)

            batch_throttle = sum(r.get('throttle_events', 0) for r in batch_results if r)
            total_throttle_events += batch_throttle

            total_uploaded_so_far = sum(r.get('uploaded_count', 0) for r in results if r)
            logging.info(f"Progress: Blob batch {batch_num}/{total_batches} - {total_uploaded_so_far:,} uploaded")

            if batch_throttle > 0:
                # deterministic delay
                yield context.create_timer(context.current_utc_datetime + timedelta(seconds=30))
        
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
        
        logging.info(f"=== ORCHESTRATION COMPLETE ===")
        logging.info(f"Run ID: {run_id}")
        logging.info(f"Total work units: {total_work_units}")
        logging.info(f"Total uploaded: {total_uploaded}")
        logging.info(f"Total errors: {total_errors}")
        logging.info(f"Total throttle events: {total_throttle_events}")
        logging.info(f"Blob sources processed: {len(blob_sources)}")
        
        # Return result dictionary like the working orchestrator
        return {
            'success': True,
            'run_id': run_id,
            'total_work_units': total_work_units,
            'total_uploaded': total_uploaded,
            'total_errors': total_errors,
            'total_throttle_events': total_throttle_events,
            'blob_sources_processed': len(blob_sources)
        }
        
    except Exception as e:
        logging.error(f"Orchestrator error: {type(e).__name__}: {e}", exc_info=True)
        # Return error result like the working orchestrator
        return {
            'success': False,
            'error': str(e),
            'run_id': run_id if 'run_id' in locals() else 'unknown'
        }

# Create the orchestrator function binding like the working version
main = df.Orchestrator.create(orchestrator_function)
