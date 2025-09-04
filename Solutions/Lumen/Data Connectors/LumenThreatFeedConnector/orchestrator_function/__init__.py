"""
Lumen Threat Intelligence Connector - Orchestrator Function

This function coordinates the parallel processing of threat intelligence data
by managing multiple activity functions that read from disk and upload to Microsoft Sentinel.

Key Features:
- Processes threat data directly from temp files (no blob storage)
- Creates work units for parallel workers to process disk chunks
- Stays within API rate limits (95 requests/minute)  
- Automatically cleans up temp files after completion

"""

import logging
import azure.durable_functions as df
from datetime import timedelta

def orchestrator_function(context: df.DurableOrchestrationContext):
    """
    Orchestrator function to manage parallel processing from disk files.
    
    This function coordinates the processing of threat intelligence data by:
    1. Reading temp file paths and metadata from input
    2. Creating work units for parallel processing of disk chunks
    3. Managing rate limits by processing in groups
    4. Cleaning up temp files after completion
    
    Args:
        context (df.DurableOrchestrationContext): Durable Functions context containing:
            - temp_file_paths: List of temp file metadata (file_path, indicator_type, etc.)
            - config: Configuration dictionary with API credentials
            - indicators_per_request: Number of indicators per Sentinel API request (100)
    
    Returns:
        dict: Summary of results from all processing activities
    """
    try:
        # Record start time for total operation tracking
        start_time = context.current_utc_datetime
        
        # Extract input parameters from the starter function
        input_data = context.get_input()
        temp_file_paths = input_data['temp_file_paths']
        config = input_data['config']
        indicators_per_request = input_data.get('indicators_per_request', 100)

        logging.debug(f"Starting orchestration for {len(temp_file_paths)} temp files")

        # Create work units for all temp files - break large files into smaller work units
        work_units = []
        max_indicators_per_work_unit = 1000  # Process 1000 indicators per activity (10 API requests, ~10-20 seconds)
        
        for file_info in temp_file_paths:
            estimated_indicators = file_info['estimated_indicators']
            
            if estimated_indicators <= max_indicators_per_work_unit:
                # Small file - process entire file in one work unit
                work_units.append({
                    'file_path': file_info['file_path'],
                    'indicator_type': file_info['indicator_type'],
                    'start_offset': 0,
                    'max_indicators': estimated_indicators,
                    'work_unit_id': f"{file_info['indicator_type']}-1",
                    'config': config,
                    'indicators_per_request': indicators_per_request
                })
            else:
                # Large file - break into multiple work units
                num_work_units = (estimated_indicators + max_indicators_per_work_unit - 1) // max_indicators_per_work_unit
                logging.debug(f"Breaking {file_info['indicator_type']} ({estimated_indicators} indicators) into {num_work_units} work units")
                
                for i in range(num_work_units):
                    start_offset = i * max_indicators_per_work_unit
                    remaining_indicators = estimated_indicators - start_offset
                    work_unit_size = min(max_indicators_per_work_unit, remaining_indicators)
                    
                    work_units.append({
                        'file_path': file_info['file_path'],
                        'indicator_type': file_info['indicator_type'],
                        'start_offset': start_offset,
                        'max_indicators': work_unit_size,
                        'work_unit_id': f"{file_info['indicator_type']}-{i+1}",
                        'config': config,
                        'indicators_per_request': indicators_per_request
                    })

        # Log work unit summary after creation
        logging.debug(f"Created {len(work_units)} work units (max {max_indicators_per_work_unit} indicators each)")
        logging.debug(f"Indicators per request: {indicators_per_request}, Batch size: 3 work units")

        # Process 3 work units simultaneously to maximize API rate limit utilization
        # Target: ~95 requests/minute (95% of 100 req/min limit)
        
        results = []
        total_work_units = len(work_units)
        batch_size = 3
        
        logging.debug(f"Processing work units in parallel batches of {batch_size}")
        
        for batch_start in range(0, total_work_units, batch_size):
            batch_end = min(batch_start + batch_size, total_work_units)
            batch = work_units[batch_start:batch_end]
            
            batch_start_time = context.current_utc_datetime
            logging.debug(f"Starting batch {batch_start//batch_size + 1}: work units {batch_start+1}-{batch_end} ({len(batch)} units)")
            
            # Process all work units in this batch in parallel
            parallel_tasks = []
            for work_unit in batch:
                parallel_tasks.append(
                    context.call_activity('activity_upload_from_disk', work_unit)
                )
            
            # Wait for all work units in batch to complete
            batch_results = yield context.task_all(parallel_tasks)
            results.extend(batch_results)
            
            # Calculate batch timing and metrics
            batch_end_time = context.current_utc_datetime
            batch_duration = (batch_end_time - batch_start_time).total_seconds()
            
            # Log results for each work unit in the batch
            for i, (work_unit, result) in enumerate(zip(batch, batch_results)):
                work_unit_index = batch_start + i
                progress_pct = ((work_unit_index + 1) / total_work_units) * 100
                requests_in_this_unit = result.get('requests_made', 0)
                indicators_in_this_unit = result.get('indicators_uploaded', 0)
                
                if result.get('success', False):
                    logging.debug(f"Work unit {work_unit_index+1}/{total_work_units} completed: {indicators_in_this_unit} indicators in {requests_in_this_unit} requests ({progress_pct:.1f}%)")
                else:
                    logging.error(f"Work unit {work_unit_index+1}/{total_work_units} failed: {result.get('error', 'Unknown error')}")
            
            # Rate limiting for 95 req/min target
            if batch_end < total_work_units:  # Don't delay after the last batch
                total_requests_in_batch = sum(r.get('requests_made', 0) for r in batch_results)
                total_indicators_in_batch = sum(r.get('indicators_uploaded', 0) for r in batch_results)
                
                # Target rate: 95 requests/minute = 1.583 req/sec
                # For 3 work units (~30 requests), target batch time: ~18.9 seconds
                target_rate_per_second = 1.583  # 95 req/min
                target_batch_time = total_requests_in_batch / target_rate_per_second
                
                if batch_duration < target_batch_time:
                    # Batch finished faster than target - add precise delay
                    delay_seconds = target_batch_time - batch_duration
                    logging.debug(f"Batch control: {total_requests_in_batch} requests, {total_indicators_in_batch} indicators in {batch_duration:.1f}s, adding {delay_seconds:.1f}s delay (95 req/min target)")
                    yield context.create_timer(context.current_utc_datetime + timedelta(seconds=delay_seconds))
                else:
                    # Batch took expected time or longer - no additional delay
                    logging.debug(f"Batch control: {total_requests_in_batch} requests, {total_indicators_in_batch} indicators in {batch_duration:.1f}s, no delay (maintaining 95 req/min pace)")
                    # No delay at all - maintain maximum performance

        # Summarize results
        total_indicators_uploaded = sum(r.get('indicators_uploaded', 0) for r in results)
        total_requests_made = sum(r.get('requests_made', 0) for r in results)
        successful_work_units = sum(1 for r in results if r.get('success', False))
        
        # Calculate total elapsed time for upload process
        end_time = context.current_utc_datetime
        total_elapsed = end_time - start_time
        total_elapsed_seconds = total_elapsed.total_seconds()
        total_elapsed_minutes = total_elapsed_seconds / 60
        
        # Calculate upload rate metrics
        indicators_per_second = total_indicators_uploaded / total_elapsed_seconds if total_elapsed_seconds > 0 else 0
        requests_per_minute = (total_requests_made / total_elapsed_minutes) if total_elapsed_minutes > 0 else 0
        
        logging.info(f"Processing completed: {successful_work_units}/{total_work_units} work units successful")
        logging.info(f"Total indicators uploaded: {total_indicators_uploaded}")
        logging.info(f"Total API requests made: {total_requests_made}")
        
        # Completion summary
        logging.debug(f"🏁 Upload Process Completed:")
        logging.debug(f"   📊 Total indicators uploaded: {total_indicators_uploaded:,}")
        logging.debug(f"   ⏱️  Total elapsed time: {total_elapsed_seconds:.1f} seconds ({total_elapsed_minutes:.2f} minutes)")
        logging.debug(f"   🚀 Upload rate: {indicators_per_second:.1f} indicators/second")
        logging.debug(f"   📡 API rate: {requests_per_minute:.1f} requests/minute")
        logging.debug(f"   ✅ Success rate: {successful_work_units}/{total_work_units} work units ({(successful_work_units/total_work_units*100):.1f}%)")

        # Clean up temp files after successful processing
        logging.debug(f"Cleaning up {len(temp_file_paths)} temporary files...")
        cleanup_tasks = []
        
        for file_info in temp_file_paths:
            cleanup_tasks.append(
                context.call_activity('activity_cleanup_temp_file', {
                    'file_path': file_info['file_path'],
                    'indicator_type': file_info['indicator_type']
                })
            )
        
        cleanup_results = yield context.task_all(cleanup_tasks)
        cleaned_files = sum(1 for r in cleanup_results if r.get('success', False))
        
        logging.debug(f"Cleanup complete: {cleaned_files}/{len(temp_file_paths)} temp files deleted")

        return {
            'success': True,
            'work_units_processed': successful_work_units,
            'total_work_units': total_work_units,
            'indicators_uploaded': total_indicators_uploaded,
            'requests_made': total_requests_made,
            'temp_files_cleaned': cleaned_files,
            'elapsed_time_seconds': total_elapsed_seconds,
            'elapsed_time_minutes': total_elapsed_minutes,
            'indicators_per_second': indicators_per_second,
            'requests_per_minute': requests_per_minute
        }

    except Exception as e:
        logging.error(f"Orchestrator error: {e}")
        raise

# Create the orchestrator function binding
main = df.Orchestrator.create(orchestrator_function)
