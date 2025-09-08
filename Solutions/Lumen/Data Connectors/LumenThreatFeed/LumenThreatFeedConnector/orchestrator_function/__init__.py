import logging
import os
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
        # Concurrency: default low; can be overridden by input or env
        max_concurrent = input_data.get(
            'max_concurrent_activities',
            int(os.environ.get('LUMEN_MAX_CONCURRENT_ACTIVITIES', '2'))
        )
        
        # Deterministic batching: create grouped activities per blob.
        # Each activity will process `group_size` batches of size `indicators_per_request`.
        group_size = input_data.get(
            'group_size',
            int(os.environ.get('LUMEN_GROUP_SIZE', '10'))
        )  # 10 x 100 = 1,000 per activity
        activity_inputs = []
        for source in blob_sources:
            filtered_count = int(source.get('filtered_count', 0))
            num_batches = (filtered_count + indicators_per_request - 1) // indicators_per_request
            for start_batch in range(0, num_batches, group_size):
                count_for_unit = min(group_size, num_batches - start_batch)
                activity_inputs.append({
                    'blob_name': source['blob_name'],
                    'indicator_type': source['indicator_type'],
                    'indicators_per_request': indicators_per_request,
                    'config': config,
                    'run_id': run_id,
                    'start_batch': start_batch,
                    'num_batches': count_for_unit,
                    'work_unit_id': f"{run_id}-{source['indicator_type']}-{start_batch:05d}+{count_for_unit}"
                })

        total_work_units = len(activity_inputs)

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
            logging.debug(f"Progress: Blob batch {batch_num}/{total_batches} - {total_uploaded_so_far:,} uploaded")

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
        
        # Return result dictionary 
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
        # Return error result 
        return {
            'success': False,
            'error': str(e),
            'run_id': run_id if 'run_id' in locals() else 'unknown'
        }

# Create the orchestrator function binding 
main = df.Orchestrator.create(orchestrator_function)
