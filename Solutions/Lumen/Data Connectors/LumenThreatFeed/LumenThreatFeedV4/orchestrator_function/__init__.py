import logging
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
